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
        self.nodes_with_taint: set[Node] = set()
        self.tainted_functions: set[str] = set()
        self.config = config

    def run(self):
        for function in self.graph.functions:
            self.add_preamble(function)
            self.add_param_taint_extraction(function)
        for edge in self.graph.edges:
            print(edge)
            if edge.edge_type != EdgeType.METADATA:
                self.track_taints(edge)

    def add_preamble(self, function: Function):
        function.code_tree.body.insert(
            0,
            ast.ImportFrom(
                module="growlithe_predicates",
                names=[ast.alias(name="*", asname=None)],
            ),
        )

    def track_taints(self, edge: Edge):
        self.add_source_taint(edge.source, edge.source.object_code_location)
        self.add_sink_taint(edge.sink, edge.source, edge.sink.object_code_location)

    def add_source_taint(self, source_node: Node, code_path):
        if source_node.object_type == "RETURN":
            return
        tree = source_node.object_fn.code_tree
        self.add_source_taint_to_line(tree, source_node, code_path)

    def add_source_taint_to_line(self, tree, source_node: Node, code_path):
        if not code_path:
            return
        start_line = code_path["physicalLocation"]["region"]["startLine"]
        end_line = code_path["physicalLocation"]["region"].get("endLine", start_line)
        if getattr(tree, "body", None):
            for i, ast_node in enumerate(tree.body):
                if (
                    getattr(ast_node, "lineno", None) == start_line
                    and getattr(ast_node, "end_lineno", None) == end_line
                ):
                    if source_node.object_type == "S3_BUCKET":
                        # add metadata = bucket.Object(fileName).metadata['taints']
                        tree.body.insert(
                            i,
                            ast.parse(
                                f'GROWLITHE_TAINTS[f"{online_taint_label(source_node)}"] = GROWLITHE_TAINTS[f"{online_taint_label(source_node)}"].union(set(bucket.Object({source_node.object.reference_name}).metadata.get(\'growlithe_taints\', "").split(",")))'
                            ),
                        )
                    if source_node.object_type == "LOCAL_FILE":
                        tree.body.insert(
                            i,
                            ast.parse(
                                f'GROWLITHE_TAINTS[f"{online_taint_label(source_node)}"] = GROWLITHE_TAINTS[f"{online_taint_label(source_node)}"].union(GROWLITHE_FILE_TAINTS[f\'{{{source_node.object.reference_name}}}\'])'
                            ),
                        )
                    tree.body.insert(
                        i,
                        ast.parse(
                            f"GROWLITHE_TAINTS[f'{online_taint_label(source_node)}'].update({{f'{online_taint_label(source_node)}', GROWLITHE_INVOCATION_ID}})"
                        ),
                    )
                    return
                self.add_source_taint_to_line(ast_node, source_node, code_path)
        return

    def add_sink_taint(self, sink_node, source_node, code_path):
        if sink_node.object_type == "PARAM":
            return
        tree = sink_node.object_fn.code_tree
        self.add_sink_taint_to_line(tree, sink_node, source_node, code_path)

    def add_sink_taint_to_line(
        self, tree, sink_node: Node, source_node: Node, code_path
    ):
        start_line = code_path["physicalLocation"]["region"]["startLine"]
        end_line = code_path["physicalLocation"]["region"].get("endLine", start_line)
        if getattr(tree, "body", None):
            for i, ast_node in enumerate(tree.body):
                if (
                    getattr(ast_node, "lineno", None) == start_line
                    and getattr(ast_node, "end_lineno", None) == end_line
                ):
                    if sink_node.object_type == "S3_BUCKET":
                        tree.body[i].value.keywords.append(
                            ast.keyword(
                                arg="ExtraArgs",
                                value=ast.Dict(
                                    keys=[ast.Str(s="Metadata")],
                                    values=[
                                        ast.Dict(
                                            keys=[ast.Str(s="GROWLITHE_TAINTS")],
                                            values=[
                                                ast.Call(
                                                    func=ast.Attribute(
                                                        value=ast.Str(s=","),
                                                        attr="join",
                                                        ctx=ast.Load(),
                                                    ),
                                                    args=[
                                                        ast.Name(
                                                            id=f"GROWLITHE_TAINTS[f'{online_taint_label(sink_node)}']",
                                                            ctx=ast.Load(),
                                                        )
                                                    ],
                                                    keywords=[],
                                                )
                                            ],
                                        )
                                    ],
                                ),
                            )
                        )

                    if sink_node.object_type == "LOCAL_FILE":
                        tree.body.insert(
                            i,
                            ast.parse(
                                f"GROWLITHE_FILE_TAINTS[f'{{{sink_node.object.reference_name}}}'] = GROWLITHE_FILE_TAINTS[f'{{{sink_node.object.reference_name}}}'].union(GROWLITHE_TAINTS[f'{online_taint_label(sink_node)}'])"
                            ),
                        )
                        tree.body.insert(
                            i,
                            ast.parse(
                                f"GROWLITHE_FILE_TAINTS[f'{{{sink_node.object.reference_name}}}'].update({{f'{online_taint_label(sink_node)}', GROWLITHE_INVOCATION_ID}})"
                            ),
                        )
                    tree.body.insert(
                        i,
                        ast.parse(
                            f"GROWLITHE_TAINTS[f'{online_taint_label(sink_node)}'].update({{f'{online_taint_label(sink_node)}', GROWLITHE_INVOCATION_ID}})"
                        ),
                    )
                    tree.body.insert(
                        i,
                        ast.Assign(
                            targets=[
                                ast.Name(
                                    id=f"GROWLITHE_TAINTS[f'{online_taint_label(sink_node)}']",
                                    ctx=ast.Store(),
                                )
                            ],
                            value=ast.Call(
                                func=ast.Attribute(
                                    value=ast.Name(
                                        id=f"GROWLITHE_TAINTS[f'{online_taint_label(sink_node)}']",
                                        ctx=ast.Load(),
                                    ),
                                    attr="union",
                                    ctx=ast.Load(),
                                ),
                                args=[
                                    ast.Name(
                                        id=f"GROWLITHE_TAINTS[f'{online_taint_label(source_node)}']",
                                        ctx=ast.Load(),
                                    )
                                ],
                                keywords=[],
                            ),
                        ),
                    )
                    if sink_node.object_type == "RETURN":
                        # modify return statement to return GROWLITHE_TAINTS: {','.join(GROWLITHE_TAINTS[sink_node.id])}
                        if isinstance(ast_node, ast.Return):
                            if isinstance(ast_node.value, ast.Dict):
                                # Add new field to existing dictionary
                                ast_node.value.keys.append(
                                    ast.Constant(value="GROWLITHE_TAINTS")
                                )
                                ast_node.value.values.append(
                                    ast.Call(
                                        func=ast.Attribute(
                                            value=ast.Str(s=","),
                                            attr="join",
                                            ctx=ast.Load(),
                                        ),
                                        args=[
                                            ast.Name(
                                                id=f"GROWLITHE_TAINTS[f'{online_taint_label(sink_node)}']",
                                                ctx=ast.Load(),
                                            )
                                        ],
                                        keywords=[],
                                    )
                                )
                            if isinstance(ast_node.value, ast.Name):
                                tree.body.insert(
                                    i,
                                    ast.parse(
                                        f"{ast_node.value.id}['GROWLITHE_TAINTS'] = ','.join(GROWLITHE_TAINTS[f'{online_taint_label(sink_node)}'])"
                                    ),
                                )

                    return
                self.add_sink_taint_to_line(ast_node, sink_node, source_node, code_path)
        return

    def save_files(self):
        for function in self.graph.functions:
            os.makedirs(os.path.dirname(function.function_path), exist_ok=True)
            with open(function.function_path, "w") as f:
                f.write(ast.unparse(ast.fix_missing_locations(function.code_tree)))

    def add_param_taint_extraction(self, function: Function):
        node = function.get_event_node()
        param_line = function.get_event_node().object_code_location["physicalLocation"][
            "region"
        ]["startLine"]
        for tree_node in ast.walk(function.code_tree):
            if isinstance(tree_node, ast.FunctionDef):
                if getattr(tree_node, "lineno", None) == param_line:
                    if function.trigger:
                        if function.trigger_type == "AWS::DynamoDB::Table":
                            tree_node.body.insert(
                                0,
                                ast.parse(
                                    f"GROWLITHE_TAINTS[f'{online_taint_label(node)}'].add(f\"DYNAMODB_TABLE:{{event['Records'][0]['dynamodb']['Keys'][list(event['Records'][0]['dynamodb']['Keys'].keys())[0]]['S']}}\")"
                                ),
                            )
                    tree_node.body.insert(
                        0,
                        ast.parse(
                            "if 'detail' in event and 'bucket' in event['detail']:"
                            f"    GROWLITHE_TAINTS[f'{online_taint_label(node)}'].add(f\"S3_BUCKET:{{event['detail']['bucket']['name']}}:{{event['detail']['object']['key']}}\")"
                        ),
                    )
                    tree_node.body.insert(
                        0,
                        ast.parse(
                            f"GROWLITHE_TAINTS[f'{online_taint_label(node)}'].update({{f'{online_taint_label(node)}', GROWLITHE_INVOCATION_ID}})"
                        ),
                    )
                    tree_node.body.insert(
                        0,
                        ast.parse(
                            f"GROWLITHE_TAINTS[f'{online_taint_label(node)}'] = set(event.get('GROWLITHE_TAINTS', '').split(','))"
                        ),
                    )
                    if function.trigger:
                        if function.trigger_type == "AWS::DynamoDB::Table":
                            pass
                    tree_node.body.insert(
                        0,
                        ast.parse(
                            f"""if 'detail' in event:
                                GROWLITHE_INVOCATION_ID =  event['detail']['bucket']['name'] + event['detail']['object']['key'] + event['time']"""
                        ),
                    )
                    tree_node.body.insert(
                        0,
                        ast.parse(
                            f"GROWLITHE_INVOCATION_ID = event.get('GROWLITHE_INVOCATION_ID', '')"
                        ),
                    )
                    break
