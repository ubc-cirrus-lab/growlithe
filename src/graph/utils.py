import ast
from src.graph.graph import Graph, InterfaceType, Edge
from src.graph.policy.policy_evaluator import try_policy_eval

def add_policy_instrumentation(policy_result, code_path, tainted_file_trees):
    if (policy_result == True):
        pass
    elif (policy_result == False):
        pass
    else:
        policy_check = ast.parse(policy_result)
        file_tree = tainted_file_trees[code_path["physicalLocation"]["artifactLocation"]["uri"]]
        start_line = code_path["physicalLocation"]["region"]["startLine"]
        end_line = getattr(code_path["physicalLocation"]["region"], "endLine", start_line)
        add_policy_check_to_line(file_tree, start_line, end_line, policy_check)

def add_policy_check_to_line(tree, start_line, end_line, policy_check):
    if getattr(tree, "body", None):
        for i, ast_node in enumerate(tree.body):
            if (
                getattr(ast_node, "lineno", None) == start_line
                and getattr(ast_node, "end_lineno", None) == end_line
            ):
                tree.body.insert(i, policy_check)
                return
            add_policy_check_to_line(ast_node, start_line, end_line, policy_check)
    return


def taint_generation_and_policy_instrumentation(edge: Edge, edge_policy_map, tainted_file_trees):
    from_to_policy_key = (edge.source_node.function, edge.source_node.policy_id, edge.sink_node.function, edge.sink_node.policy_id)

    if from_to_policy_key in edge_policy_map:
        edge.edge_policy = edge_policy_map[from_to_policy_key]
        read_pol_eval = try_policy_eval(edge.edge_policy.read_policy, edge.source_node)
        add_policy_instrumentation(read_pol_eval, edge.source_properties['CodePath'], tainted_file_trees)
        write_pol_eval = try_policy_eval(edge.edge_policy.write_policy, edge.sink_node)
        add_policy_instrumentation(write_pol_eval, edge.sink_properties['CodePath'], tainted_file_trees)
    else:
        # TODO: This should be an error as we expect all edges to have a policy in the json
        # logger.warn(f"No policy found for edge {edge.source_node} -> {edge.sink_node}")
        pass