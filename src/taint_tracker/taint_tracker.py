import ast

from src.graph.graph import Graph, Node, Edge
from src.logger import logger
from src.tmp_config import app_path


class TaintTracker:
    def __init__(self, graph: Graph):
        self.graph: Graph = graph
        self.nodes_with_taint: set[Node] = set()
        self.tainted_functions: set[str] = set()
        self.function_codes: dict[str, ast.Module] = {}
        for node in self.graph.nodes:
            if node.code_path:
                file = node.code_path["physicalLocation"]["artifactLocation"]["uri"]
                if file not in self.function_codes:
                    with open(f"{app_path}/{file}", "r") as f:
                        code = f.read()
                        tree = ast.parse(code)
                        self.function_codes[file] = tree

    def run(self):
        # initialize taint tracking for each function
        for node in self.graph.nodes:
            if node.code_path:  # TODO: remove this check
                if node.resource_type == "PARAM":
                    self.add_param_taint_extraction(node)
                else:
                    self.initialize_taints(node)

        for tree in self.function_codes.values():
            tree.body.insert(
                0,
                ast.ImportFrom(
                    module="growlithe_utils",
                    names=[ast.alias(name="TAINTS", asname=None)],
                ),
            )

        for edge in self.graph.edges:
            self.track_taints(edge)
        self.write_files_back()

    def track_taints(self, edge: Edge):
        source_node = edge.source_node
        sink_node = edge.sink_node
        self.add_source_taint(source_node)
        if sink_node.code_path:  # TODO: remove
            self.add_sink_taint(sink_node, source_node)

    def add_source_taint(self, source_node: Node):
        if (
            source_node.resource_type == "PARAM"
            or source_node.resource_type == "RETURN"
        ):
            return
        file = source_node.code_path["physicalLocation"]["artifactLocation"]["uri"]
        tree = self.function_codes[file]
        self.add_taint_to_line(tree, source_node)

    def add_taint_to_line(self, tree, source_node: Node):
        start_line = source_node.code_path["physicalLocation"]["region"]["startLine"]
        end_line = source_node.code_path["physicalLocation"]["region"].get(
            "endLine", start_line
        )
        if getattr(tree, "body", None):
            for i, ast_node in enumerate(tree.body):
                if (
                    getattr(ast_node, "lineno", None) == start_line
                    and getattr(ast_node, "end_lineno", None) == end_line
                ):
                    # if source_node.resource_type == "S3_BUCKET":
                    #     # add metadata = bucket.Object(fileName).metadata['taints']
                    #     tree.body.insert(
                    #         i + 1,
                    #         ast.Assign(
                    #             targets=[ast.Name(id="metadata", ctx=ast.Store())],
                    #             value=ast.Attribute(
                    #                 value=ast.Attribute(
                    #                     value=ast.Name(id="bucket", ctx=ast.Load()),
                    #                     attr="Object",
                    #                     ctx=ast.Load(),
                    #                 ),
                    #                 attr="metadata",
                    #                 ctx=ast.Load(),
                    #             ),
                    #         ),
                    #     )
                    tree.body.insert(
                        i + 1,
                        ast.Expr(
                            value=ast.Call(
                                func=ast.Attribute(
                                    value=ast.Name(
                                        id=f"TAINTS['{source_node.id}']", ctx=ast.Load()
                                    ),
                                    attr="add",
                                    ctx=ast.Load(),
                                ),
                                args=[ast.Str(s=source_node.id)],
                                keywords=[],
                            ),
                        ),
                    )
                    return
                self.add_taint_to_line(ast_node, source_node)
        return

    def add_sink_taint(self, sink_node, source_node):
        if sink_node.resource_type == "PARAM":
            return
        file = sink_node.code_path["physicalLocation"]["artifactLocation"]["uri"]
        tree = self.function_codes[file]
        self.add_sink_taint_to_line(tree, sink_node, source_node)

    def add_sink_taint_to_line(self, tree, sink_node: Node, source_node: Node):
        start_line = sink_node.code_path["physicalLocation"]["region"]["startLine"]
        end_line = sink_node.code_path["physicalLocation"]["region"].get(
            "endLine", start_line
        )
        if getattr(tree, "body", None):
            for i, ast_node in enumerate(tree.body):
                if (
                    getattr(ast_node, "lineno", None) == start_line
                    and getattr(ast_node, "end_lineno", None) == end_line
                ):
                    tree.body.insert(
                        i,
                        ast.Expr(
                            value=ast.Call(
                                func=ast.Attribute(
                                    value=ast.Name(
                                        id=f"TAINTS['{sink_node.id}']", ctx=ast.Load()
                                    ),
                                    attr="add",
                                    ctx=ast.Load(),
                                ),
                                args=[ast.Str(s=sink_node.id)],
                                keywords=[],
                            ),
                        ),
                    )
                    tree.body.insert(
                        i,
                        ast.Assign(
                            targets=[
                                ast.Name(
                                    id=f"TAINTS['{sink_node.id}']", ctx=ast.Store()
                                )
                            ],
                            value=ast.Call(
                                func=ast.Attribute(
                                    value=ast.Name(
                                        id=f"TAINTS['{sink_node.id}']", ctx=ast.Load()
                                    ),
                                    attr="union",
                                    ctx=ast.Load(),
                                ),
                                args=[
                                    ast.Name(
                                        id=f"TAINTS['{source_node.id}']", ctx=ast.Load()
                                    )
                                ],
                                keywords=[],
                            ),
                        ),
                    )
                    if sink_node.resource_type == "RETURN":
                        # modify return statement to return TAINTS[sink_node.id]
                        if isinstance(ast_node, ast.Return):
                            if isinstance(ast_node.value, ast.Dict):
                                # Add new field to existing dictionary
                                ast_node.value.keys.append(
                                    ast.Constant(value="GROWLITHE_TAINTS")
                                )
                                ast_node.value.values.append(
                                    ast.Name(
                                        id=f"TAINTS['{sink_node.id}']", ctx=ast.Load()
                                    )
                                )
                    return
                self.add_sink_taint_to_line(ast_node, sink_node, source_node)
        return

    def write_files_back(self):
        for file, tree in self.function_codes.items():
            with open(f"{app_path}/{file}", "w") as f:
                f.write(ast.unparse(ast.fix_missing_locations(tree)))

    def initialize_taints(self, node: Node):
        file = node.code_path["physicalLocation"]["artifactLocation"]["uri"]
        tree = self.function_codes[file]
        # "TAINTS['{node.id}'] = set()"
        assignment = ast.Assign(
            targets=[ast.Name(id=f"TAINTS['{node.id}']", ctx=ast.Store())],
            value=ast.Call(
                func=ast.Name(id="set", ctx=ast.Load()), args=[], keywords=[]
            ),
        )
        tree.body.insert(0, assignment)

    def add_param_taint_extraction(self, node):
        file = node.code_path["physicalLocation"]["artifactLocation"]["uri"]
        param_line = node.code_path["physicalLocation"]["region"]["startLine"]
        for tree_node in ast.walk(self.function_codes[file]):
            if isinstance(tree_node, ast.FunctionDef):
                if getattr(tree_node, "lineno", None) == param_line:
                    # "taint_set_{node.id} = event.get('GROWLITHE_TAINTS', set())"
                    tree_node.body.insert(
                        0,
                        ast.Assign(
                            targets=[
                                ast.Name(id=f"TAINTS['{node.id}']", ctx=ast.Store())
                            ],
                            value=ast.Call(
                                func=ast.Attribute(
                                    value=ast.Name(id="event", ctx=ast.Load()),
                                    attr="get",
                                    ctx=ast.Load(),
                                ),
                                args=[
                                    ast.Str(s="GROWLITHE_TAINTS"),
                                    ast.Call(
                                        func=ast.Name(id="set", ctx=ast.Load()),
                                        args=[],
                                        keywords=[],
                                    ),
                                ],
                                keywords=[],
                            ),
                        ),
                    )
                    break