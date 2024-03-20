import ast

from src.graph.graph import Graph, Node, Edge
from src.logger import logger
from src.benchmark_config import app_path


class TaintTracker:
    def __init__(self, graph: Graph):
        self.graph: Graph = graph
        self.nodes_with_taint: set[Node] = set()
        self.tainted_functions: set[str] = set()
        self.function_codes: dict[str, ast.Module] = {}
        for edge in self.graph.edges:
            if edge.source_properties.get("CodePath"):
                file = edge.source_properties["CodePath"]["physicalLocation"][
                    "artifactLocation"
                ]["uri"]
                if file not in self.function_codes:
                    with open(f"{app_path}/{file}", "r") as f:
                        code = f.read()
                        tree = ast.parse(code)
                        self.function_codes[file] = tree
            if edge.sink_properties.get("CodePath"):
                file = edge.sink_properties["CodePath"]["physicalLocation"][
                    "artifactLocation"
                ]["uri"]
                if file not in self.function_codes:
                    with open(f"{app_path}/{file}", "r") as f:
                        code = f.read()
                        tree = ast.parse(code)
                        self.function_codes[file] = tree

    def run(self):
        for edge in self.graph.edges:
            if (
                edge.source_node.resource_type == "PARAM"
                and "context" not in edge.source_node.data_object.reference_name
            ):
                self.add_param_taint_extraction(
                    edge.source_node, edge.source_properties["CodePath"]
                )
            self.track_taints(edge)
        return self.function_codes

    def track_taints(self, edge: Edge):
        self.add_source_taint(edge.source_node, edge.source_properties["CodePath"])
        if edge.sink_properties["CodePath"]:  # TODO: remove
            self.add_sink_taint(
                edge.sink_node, edge.source_node, edge.sink_properties["CodePath"]
            )

    def add_source_taint(self, source_node: Node, code_path):
        if source_node.resource_type in ["RETURN", "DEFAULT"]:
            return
        file = code_path["physicalLocation"]["artifactLocation"]["uri"]
        tree = self.function_codes[file]
        self.add_source_taint_to_line(tree, source_node, code_path)

    def add_source_taint_to_line(self, tree, source_node: Node, code_path):
        start_line = code_path["physicalLocation"]["region"]["startLine"]
        end_line = code_path["physicalLocation"]["region"].get("endLine", start_line)
        if getattr(tree, "body", None):
            for i, ast_node in enumerate(tree.body):
                if (
                    getattr(ast_node, "lineno", None) == start_line
                    and getattr(ast_node, "end_lineno", None) == end_line
                ):
                    if source_node.resource_type == "S3_BUCKET":
                        # add metadata = bucket.Object(fileName).metadata['taints']
                        tree.body.insert(
                            i,
                            ast.parse(
                                f'GROWLITHE_TAINTS[f"{source_node.id}"] = GROWLITHE_TAINTS[f"{source_node.id}"].union(set(bucket.Object({source_node.data_object.reference_name}).metadata.get(\'growlithe_taints\', "").split(",")))'
                            ),
                        )
                    tree.body.insert(
                        i,
                        ast.parse(
                            f"GROWLITHE_TAINTS[f'{source_node.id}'].add(f'{source_node.id}')"
                        ),
                    )
                    return
                self.add_source_taint_to_line(ast_node, source_node, code_path)
        return

    def add_sink_taint(self, sink_node, source_node, code_path):
        if sink_node.resource_type == "PARAM":
            return
        file = code_path["physicalLocation"]["artifactLocation"]["uri"]
        tree = self.function_codes[file]
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
                    if sink_node.resource_type == "S3_BUCKET":
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
                                                            id=f"GROWLITHE_TAINTS[f'{sink_node.id}']",
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

                    tree.body.insert(
                        i,
                        ast.parse(
                            f"GROWLITHE_TAINTS[f'{sink_node.id}'].add(f'{sink_node.id}')"
                        ),
                    )
                    tree.body.insert(
                        i,
                        ast.Assign(
                            targets=[
                                ast.Name(
                                    id=f"GROWLITHE_TAINTS[f'{sink_node.id}']",
                                    ctx=ast.Store(),
                                )
                            ],
                            value=ast.Call(
                                func=ast.Attribute(
                                    value=ast.Name(
                                        id=f"GROWLITHE_TAINTS[f'{sink_node.id}']",
                                        ctx=ast.Load(),
                                    ),
                                    attr="union",
                                    ctx=ast.Load(),
                                ),
                                args=[
                                    ast.Name(
                                        id=f"GROWLITHE_TAINTS[f'{source_node.id}']",
                                        ctx=ast.Load(),
                                    )
                                ],
                                keywords=[],
                            ),
                        ),
                    )
                    if sink_node.resource_type == "RETURN":
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
                                                id=f"GROWLITHE_TAINTS[f'{sink_node.id}']",
                                                ctx=ast.Load(),
                                            )
                                        ],
                                        keywords=[],
                                    )
                                )
                    return
                self.add_sink_taint_to_line(ast_node, sink_node, source_node, code_path)
        return

    def write_files_back(self):
        for file, tree in self.function_codes.items():
            with open(f"{app_path}/{file}", "w") as f:
                f.write(ast.unparse(ast.fix_missing_locations(tree)))

    def add_param_taint_extraction(self, node, code_path):
        file = code_path["physicalLocation"]["artifactLocation"]["uri"]
        param_line = code_path["physicalLocation"]["region"]["startLine"]
        for tree_node in ast.walk(self.function_codes[file]):
            if isinstance(tree_node, ast.FunctionDef):
                if getattr(tree_node, "lineno", None) == param_line:
                    tree_node.body.insert(
                        0,
                        ast.parse(
                            "if 'detail' in event and 'bucket' in event['detail']:"
                            f"    GROWLITHE_TAINTS[f'{node.id}'].add(f\"trigger:S3_BUCKET:{{event['detail']['bucket']['name']}}:{{event['detail']['object']['key']}}_0\")"
                        ),
                    )
                    tree_node.body.insert(
                        0,
                        ast.parse(
                            "if 'Records' in event and 'dynamodb' in event['Records'][0]:"
                            f"    GROWLITHE_TAINTS[f'{node.id}'].add(f\"trigger:DYNAMODB_TABLE:{{event['Records'][0]['dynamodb']['Keys'][list(event['Records'][0]['dynamodb']['Keys'].keys())[0]]['S']}}_0\")"
                        ),
                    )
                    tree_node.body.insert(
                        0,
                        ast.parse(f"GROWLITHE_TAINTS[f'{node.id}'].add('{node.id}')"),
                    )
                    tree_node.body.insert(
                        0,
                        ast.parse(
                            f"GROWLITHE_TAINTS[f'{node.id}'] = set(event.get('GROWLITHE_TAINTS', '').split(','))"
                        ),
                    )
                    break
