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
        for edge in self.graph.edges:
            self.track_taints(edge)
        # self.write_files_back()

    def track_taints(self, edge: Edge):
        source_node = edge.source_node
        sink_node = edge.sink_node
        self.add_source_taint(source_node)
        self.add_sink_taint(sink_node)

    def add_source_taint(self, source_node: Node):
        file = source_node.code_path["physicalLocation"]["artifactLocation"]["uri"]
        node_line = source_node.code_path["physicalLocation"]["region"]["startLine"]
        tree = self.function_codes[file]
        for tree_node in ast.walk(tree):
            if getattr(tree_node, "lineno", None) == node_line:
                # "taint_set_{node.id}.add("test")"
                tree_node.body.append(
                    ast.Expr(
                        value=ast.Call(
                            func=ast.Attribute(
                                value=ast.Name(
                                    id=f"taint_set_{source_node.id}", ctx=ast.Load()
                                ),
                                attr="add",
                                ctx=ast.Load(),
                            ),
                            args=[ast.Str(s=source_node.id)],
                            keywords=[],
                        )
                    )
                )
                break

    def add_sink_taint(self, sink_node):
        pass

    def write_files_back(self):
        for file, tree in self.function_codes.items():
            with open(f"{app_path}/{file}", "w") as f:
                f.write(ast.unparse(ast.fix_missing_locations(tree)))

    def initialize_taints(self, node: Node):
        file = node.code_path["physicalLocation"]["artifactLocation"]["uri"]
        tree = self.function_codes[file]
        # "taint_set_{node.id} = set()"
        assignment = ast.Assign(
            targets=[ast.Name(id=f"taint_set_{node.id}", ctx=ast.Store())],
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
                                ast.Name(id=f"taint_set_{node.id}", ctx=ast.Store())
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
