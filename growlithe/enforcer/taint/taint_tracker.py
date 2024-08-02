import ast
import os

from .taint_utils import online_taint_label
from growlithe.graph.adg.graph import Graph
from growlithe.graph.adg.edge import Edge, EdgeType
from growlithe.graph.adg.node import Node
from growlithe.graph.adg.function import Function
from growlithe.common.logger import logger
from growlithe.config import Config


class TaintTracker:
    def __init__(self, graph: Graph, config: Config):
        self.graph: Graph = graph
        self.config = config

    def run(self):
        for function in self.graph.functions:
            self.add_preamble(function)
            self.add_param_taint_extraction(function)
        for edge in self.graph.edges:
            if edge.edge_type == EdgeType.DATA:
                self.track_direct_taints(edge)
            elif edge.edge_type == EdgeType.INDIRECT:
                self.track_indirect_taints(edge)

    def add_preamble(self, function: Function):
        function.code_tree.body.insert(0, ast.parse('from growlithe_predicates import *'))

    def track_indirect_taints(self, edge: Edge):
        source_node: Node = edge.source
        sink_node: Node = edge.sink
        if source_node.object_type not in ['S3_BUCKET', 'RETURN'] or sink_node.object_type not in ['S3_BUCKET', 'PARAM']:
            logger.error(f"indirect edge of type {source_node.object_type} -> {sink_node.object_type} not supported yet.")
            raise NotImplementedError
        if source_node.object_type == 'S3_BUCKET':
            self.add_s3_indirect_source_taint_to_line(source_node.object_fn.code_tree, source_node, edge.source.object_code_location)

    def add_s3_indirect_source_taint_to_line(self, tree, source_node: Node, code_path: dict):
        if not code_path:
            logger.warn(f"code_path not found for node {source_node}")
        start_line = code_path["physicalLocation"]["region"]["startLine"]
        end_line = code_path["physicalLocation"]["region"].get("endLine", start_line)
        if getattr(tree, "body", None):
            for i, ast_node in enumerate(tree.body):
                if getattr(ast_node, "lineno", None) == start_line and getattr(ast_node, "end_lineno", None) == end_line:
                    tree.body.insert(i, ast.parse(f"growlithe_save_s3_taint(f'{online_taint_label(source_node)}', bucket, {source_node.object.reference_name})"))
                    tree.body.insert(i, ast.parse(f"growlithe_add_self_taint(f'{online_taint_label(source_node)}')"))
                    return
                self.add_s3_indirect_source_taint_to_line(ast_node, source_node, code_path)


    def track_direct_taints(self, edge: Edge):
        self.add_source_taint(edge.source, edge.source.object_code_location)
        self.add_sink_taint(edge.sink, edge.source, edge.sink.object_code_location)

    def add_source_taint(self, source_node: Node, code_path):
        tree = source_node.object_fn.code_tree
        self.add_source_taint_to_line(tree, source_node, code_path)

    def add_source_taint_to_line(self, tree, source_node: Node, code_path):
        if not code_path:
            logger.warn(f"code_path not found for node {source_node}")
        start_line = code_path["physicalLocation"]["region"]["startLine"]
        end_line = code_path["physicalLocation"]["region"].get("endLine", start_line)
        if getattr(tree, "body", None):
            for i, ast_node in enumerate(tree.body):
                if getattr(ast_node, "lineno", None) == start_line and getattr(ast_node, "end_lineno", None) == end_line:
                    if source_node.object_type == "S3_BUCKET":
                        tree.body.insert(i, ast.parse(f"growlihte_add_s3_object_taint(f'{online_taint_label(source_node)}', bucket, {source_node.object.reference_name})"))
                    if source_node.object_type == "LOCAL_FILE":
                        tree.body.insert(i, ast.parse(f"growlithe_add_file_taint(f'{online_taint_label(source_node)}', {source_node.object.reference_name})"))
                    tree.body.insert(i, ast.parse(f"growlithe_add_self_taint(f'{online_taint_label(source_node)}')"))
                    return
                self.add_source_taint_to_line(ast_node, source_node, code_path)

    def add_sink_taint(self, sink_node, source_node, code_path):
        tree = sink_node.object_fn.code_tree
        self.add_sink_taint_to_line(tree, sink_node, source_node, code_path)

    def add_sink_taint_to_line(self, tree, sink_node: Node, source_node: Node, code_path):
        start_line = code_path["physicalLocation"]["region"]["startLine"]
        end_line = code_path["physicalLocation"]["region"].get("endLine", start_line)
        if getattr(tree, "body", None):
            for i, ast_node in enumerate(tree.body):
                if getattr(ast_node, "lineno", None) == start_line and getattr(ast_node, "end_lineno", None) == end_line:
                    if sink_node.object_type == "S3_BUCKET":
                        # add taint to the metadat of the s3 object.
                        tree.body[i].value.keywords.append(
                            ast.keyword(
                                arg="ExtraArgs",
                                value=ast.Dict(
                                    keys=[ast.Str(s="Metadata")],
                                    values=[
                                        ast.Dict(
                                            keys=[ast.Str(s="growlithe_taints")],
                                            values=[
                                                ast.Call(
                                                    func=ast.Attribute(value=ast.Str(s=","), attr="join", ctx=ast.Load()),
                                                    args=[ast.Name(id=f"GROWLITHE_TAINTS[f'{online_taint_label(sink_node)}']", ctx=ast.Load())],
                                                    keywords=[],
                                                )
                                            ],
                                        )
                                    ],
                                ),
                            )
                        )
                    elif sink_node.object_type == "LOCAL_FILE":
                        tree.body.insert(i, ast.parse(f"growlithe_update_file_taint({source_node.object.reference_name}, f'{online_taint_label(sink_node)}')"))
                    elif sink_node.object_type == "RETURN":
                        # modify return statement to return GROWLITHE_TAINTS: {','.join(GROWLITHE_TAINTS[sink_node.id])}
                        if isinstance(ast_node, ast.Return):
                            if isinstance(ast_node.value, ast.Dict):
                                # Add new field to existing dictionary
                                ast_node.value.keys.append(ast.Constant(value="GROWLITHE_TAINTS"))
                                ast_node.value.values.append(
                                    ast.Call(
                                        func=ast.Attribute(value=ast.Str(s=","), attr="join", ctx=ast.Load()),
                                        args=[
                                            ast.Name(id=f"GROWLITHE_TAINTS[f'{online_taint_label(sink_node)}']", ctx=ast.Load())
                                        ]
                                    )
                                )
                            if isinstance(ast_node.value, ast.Name):
                                # if the return is a dict variable
                                tree.body.insert(i, ast.parse(f"{ast_node.value.id}['GROWLITHE_TAINTS'] = ','.join(GROWLITHE_TAINTS[f'{online_taint_label(sink_node)}'])"))
                    tree.body.insert(i, ast.parse(f"growlithe_add_self_taint(f'{online_taint_label(sink_node)}')"))
                    tree.body.insert(i, ast.parse(f"growlithe_add_source_taint(f'{online_taint_label(sink_node)}', f'{online_taint_label(source_node)}')"))
                    return
                self.add_sink_taint_to_line(ast_node, sink_node, source_node, code_path)

    def save_files(self):
        for function in self.graph.functions:
            os.makedirs(os.path.dirname(function.growlithe_function_path), exist_ok=True)
            with open(function.growlithe_function_path, "w") as f:
                f.write(ast.unparse(ast.fix_missing_locations(function.code_tree)))
            logger.info(f"Saved tainted function {function.name} in {function.growlithe_function_path}")

    def add_param_taint_extraction(self, function: Function):
        node = function.get_event_node()
        param_line = function.get_event_node().object_code_location["physicalLocation"][
            "region"
        ]["startLine"]
        for tree_node in ast.walk(function.code_tree):
            if isinstance(tree_node, ast.FunctionDef):
                if getattr(tree_node, "lineno", None) == param_line:
                    tree_node.body.insert(0, ast.parse(f"growlithe_add_self_taint(f'{online_taint_label(node)}')"))
                    tree_node.body.insert(0, ast.parse(f"growlithe_extract_param_taint(f'{online_taint_label(node)}', event)"))
                    break
