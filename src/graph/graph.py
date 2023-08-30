import json
from typing import Any

import networkx as nx
import matplotlib.pyplot as plt
from collections import defaultdict

from src.graph.node import Node, SecurityType, NodeType, BroadType
import src.utility as utility
from src.logger import logger
from src.policy.policy import Policy, PERM
from src.policy.policy_interface import PolicyInterface


class Graph:
    def __init__(self):
        self.nodes = []
        self.private_nodes = []
        self.suggested_policies = []
        self.policies = []

        # Maps objects to list of policies defined on them
        self.object_to_policy_map = defaultdict(set)
        # Maps the tuple (subject, object, perm) to the policy
        self.policy_map = {}

        self.taint_sources = defaultdict(set)

    def find_node(self, name):
        for node in self.nodes:
            if node.name == name:
                return node
        return None

    def find_node_by_policy(self, name):
        for node in self.nodes:
            if node.policy_str == name:
                return node
        return None

    def find_node_by_physical_location(self, physical_location):
        for node in self.nodes:
            if node is not None and node.physical_location == physical_location:
                return node
        return None

    def find_node_or_create(self, name, physical_location=None):
        if physical_location is not None:
            node = self.find_node_by_physical_location(physical_location)
        else:
            node = self.find_node(name)
        if node is None:
            node = Node(name)
            self.nodes.append(node)
            if '/' in name and not node.is_root_node():
                parent_name = name.rsplit("/", 1)[0]
                parent_node = self.find_node_or_create(parent_name)
                parent_node.add_edge(node)
                node.add_parent(parent_node)
        return node

    @staticmethod
    def find_child_node_by_node_type(function_node, node_type):
        result = []
        for node in function_node.children:
            if node.node_type == node_type:
                result.append(node)
        return result

    def init_policies(self):
        self.traverse(self.suggest_policy)

        policy_interface = PolicyInterface(self)
        self.policies = policy_interface.get_policies()

    def annotate_edges(self):
        self.traverse(self.annotate_edge)

    def annotate_edge(self, node, next_node, _):
        subject, object, perm = None, None, None
        match node.broad_node_type, next_node.broad_node_type:
            # Reads from a resource
            case BroadType.RESOURCE, BroadType.IDH_OTHER:
                subject = next_node.parent_function_node
                idh_node = next_node
                object = node
                perm = PERM.READ
            # Execute Trigger from a resource
            case BroadType.RESOURCE, BroadType.IDH_PARAM:
                subject = node
                idh_node = None
                object = next_node.parent_function_node
                perm = PERM.EXECUTE
            case BroadType.RESOURCE, BroadType.COMPUTE:
                subject = node
                idh_node = None
                object = next_node
                perm = PERM.EXECUTE
            # Writes to a resource
            case BroadType.IDH_OTHER, BroadType.RESOURCE:
                subject = node.parent_function_node
                idh_node = node
                object = next_node
                perm = PERM.WRITE
                self.check_is_as_restrictive(node.parent_function_node, next_node)

            # TODO: Cover other cases
        if subject is not None and object is not None and perm is not None:
            policy = self.get_policy(subject, object, perm)
            if policy is None:
                print(self.policy_map)
                print(subject, object, perm)
                logger.debug(f'Edge is DENY {node.name} {next_node.name}')
            else:
                eval_results = policy.eval()
                if eval_results:
                    logger.debug(f'Edge is Allow {node.name} {next_node.name}')
                else:
                    missing_subject_attributes, missing_object_attributes, environment_attributes = eval_results
                    subject.missing_attributes.update(missing_subject_attributes)
                    object.missing_attributes.update(missing_object_attributes)
                    # TODO: Add required environment attributes somewhere
                    logger.info("Adding runtime checks...")
                    policy.add_runtime_checks(idh_node)

    def check_is_as_restrictive(self, node, next_node):
        policies = self.object_to_policy_map[next_node]
        taint_sources = self.taint_sources[node]
        for taint_source in taint_sources:
            source_policies = self.object_to_policy_map[taint_source]
            # if len(policies) < len(source_policies):
            #     logger.info('Policies not defined for all subjects')
            #     return False
            for source_policy in source_policies:
                if source_policy.perm == PERM.WRITE:
                    policy = self.get_policy(source_policy.subject, next_node, PERM.WRITE)
                    if policy is None:
                        logger.debug(f'No policy found for {source_policy}')
                        return False
                    elif not source_policy.is_as_restrictive(policy):
                        logger.debug(f'Integrity violation: {source_policy} is not as restrictive as {policy}')
                        return False
            for policy in policies:
                if policy.perm in [PERM.READ, PERM.EXECUTE]:
                    source_policy = self.get_policy(taint_source, policy.object, policy.perm)
                    if source_policy is None:
                        logger.debug(f'No source_policy found for {policy}')
                        return False
                    if not policy.is_as_restrictive(source_policy):
                        logger.debug(f'Confidentiality violation: {policy} is not as restrictive as {source_policy}')
                        return False
        return True

    def generate_taints(self):
        # TODO: Move map initilization to where policies are confirmed by developer
        self.init_policy_maps()
        for node in self.object_to_policy_map.keys():
            self.dfs_helper(node, set(), self.propagate_taints, node)

    def propagate_taints(self, _, next_node, source_node):
        # Propagate taints on a read or flow edge
        if next_node.broad_node_type == BroadType.IDH_OTHER:
            self.taint_sources[next_node].add(source_node)

    def get_policy(self, sub, obj, perm):
        if (sub, obj, perm) in self.policy_map:
            return self.policy_map[(sub, obj, perm)]
        return None

    def traverse(self, apply_func):
        visited = set()
        for node in self.nodes:
            # TODO: FIX Missing edges if started from intermediate node
            if node not in visited:
                visited.add(node)
                self.dfs_helper(node, visited, apply_func)

    def dfs_helper(self, node, visited, apply_func, apply_func_params=None):
        logger.debug(f"Visiting node {node.name}")
        for next_node in node.edges:
            # For detecting reads if already visited current function
            apply_func(node, next_node, apply_func_params)
            if next_node not in visited:
                visited.add(next_node)
                self.dfs_helper(next_node, visited, apply_func, apply_func_params)

    # Avoid creating duplicate policies
    def fetch_or_suggest_policy(self, subject, object, perm):
        for policy in self.suggested_policies:
            policy = self.get_policy(subject, object, perm)
            if policy is not None:
                return policy
        policy = Policy(subject, object, perm)
        self.suggested_policies.append(policy)
        self.object_to_policy_map[policy.object].add(policy)
        self.policy_map[(policy.subject, policy.object, policy.perm)] = policy
        return policy

    def init_policy_maps(self):
        self.object_to_policy_map.clear()
        self.policy_map.clear()

        for policy in self.policies:
            self.object_to_policy_map[policy.object].add(policy)
            # TODO: Flag duplicate tuple found here?
            self.policy_map[(policy.subject, policy.object, policy.perm)] = policy

    def suggest_policy(self, node, next_node, _):
        match node.broad_node_type, next_node.broad_node_type:
            # Reads from a resource
            case BroadType.RESOURCE, BroadType.IDH_OTHER:
                self.fetch_or_suggest_policy(next_node.parent_function_node, node, PERM.READ)
            # Execute Trigger from a resource
            case BroadType.RESOURCE, BroadType.IDH_PARAM:
                self.fetch_or_suggest_policy(next_node.parent_function_node, node, PERM.EXECUTE)
            case BroadType.RESOURCE, BroadType.COMPUTE:
                self.fetch_or_suggest_policy(next_node, node, PERM.EXECUTE)
            # Writes to a resource
            case BroadType.IDH_OTHER, BroadType.RESOURCE:
                self.fetch_or_suggest_policy(node.parent_function_node, next_node, PERM.WRITE)
            case BroadType.IDH_OTHER, BroadType.IDH_PARAM:
                self.fetch_or_suggest_policy(node.parent_function_node, next_node.parent_function_node, PERM.EXECUTE)
            # TODO: Cover all cases

    def init_security_labels(self, security_labels_file):
        labels = json.load(open(security_labels_file))
        private_locations = labels["private"]
        for location in private_locations:
            node = self.find_node_by_physical_location(location)
            if node is not None:
                node.security_type = SecurityType.PRIVATE
                self.private_nodes.append(node)
                logger.debug(f"Private node: {node.name}")
            else:
                logger.warning(f"{location} not found in graph")

        public_node_ids = labels["public"]
        for public_node_id in public_node_ids:
            node = self.find_node(public_node_id)
            if node is not None:
                node.security_type = SecurityType.PUBLIC
                logger.debug("Public node: {node.name}")
            else:
                logger.warning(f"{public_node_id} not found in graph")

    def find_violations(self):
        for node in self.private_nodes:
            logger.debug(f"Finding publicly reachable nodes from {node.name}")
            self.dfs(node, [node])
            # if node.parent_function_node is None:
            #     for edge in node.edges:
            #         self.propagate_labels(child)

    # Traverse the graph and propagate private labels
    def dfs(self, node, path):
        if node.security_type == SecurityType.PUBLIC:
            logger.info(f"Violation: Public node {node.name} is reachable via {path}")
            # TODO: Continue traversing even after public nodes
            return
        for edge in node.edges:
            # if edge.security_type == SecurityType.UNKNOWN:
            # edge.security_type = SecurityType.PRIVATE
            self.dfs(edge, path + [edge])

    def connect_nodes_across_functions(self, function_node):
        for next_function_node in function_node.edges:
            rets = self.find_child_node_by_node_type(function_node, NodeType.RETURN)
            # FIXME: There can be multiple params in next_node
            params = self.find_child_node_by_node_type(next_function_node, NodeType.PARAMETER)
            for ret in rets:
                for param in params:
                    ret.add_edge(param)
            self.connect_nodes_across_functions(next_function_node)

    @property
    def root(self):
        return self.nodes[0]

    def print(self):
        logger.debug(
            "======================================================================================================="
        )
        for node in self.nodes:
            logger.debug(
                f"{node.name} (Type: {node.node_type}) " +
                f"(Parent: {node.parent_function_node.name if node.parent_function_node else 'None'}) " +
                f"(Edges: {[edge.name for edge in node.edges]}) " +
                f"(children: {[child.name for child in node.children]})")
        logger.debug(
            "======================================================================================================="
        )

    def visualize(self, vis_out_path, graphic=False):
        if graphic:
            nodes = [node.name for node in self.nodes if node.parent_function_node is None]
            nodes.append("End")

            G = nx.DiGraph()
            G.add_nodes_from(nodes)

            self.add_edges(G)

            node_sizes, node_colors = self.customize_nodes()

            edge_styles = {edge: G.edges[edge]["style"] for edge in G.edges}

            pos = nx.spring_layout(G, seed=5)
            nx.draw_networkx(
                G,
                pos=pos,
                with_labels=True,
                arrows=True,
                node_size=[node_sizes[n] for n in nodes],
                node_color=[node_colors[n] for n in nodes],
                style=[edge_styles[edge] for edge in G.edges],
            )

            legend_handles = self.customize_legends()
            plt.legend(handles=legend_handles, loc="lower right")
            plt.show(block=False)
            plt.savefig(vis_out_path, format="PNG")
        else:
            for node in self.nodes:
                if not node.edgeren:
                    logger.debug(
                        f"{node.name} ({node.parent_function_node.name if node.parent_function_node else 'None'}) -> End"
                    )
                for edge in node.edgeren:
                    logger.debug(
                        f"{node.name} ({node.parent_function_node.name if node.parent_function_node else 'None'}) -> {edge.name}"
                    )

    @staticmethod
    def customize_legends():
        legend_handles = [plt.Line2D(
            [],
            [],
            color="blue",
            marker="o",
            linestyle="None",
            markersize=10,
            label="resource",
        ), plt.Line2D(
            [],
            [],
            color="green",
            marker="o",
            linestyle="None",
            markersize=10,
            label="function",
        ), plt.Line2D(
            [],
            [],
            color="red",
            marker="o",
            linestyle="None",
            markersize=10,
            label="end",
        ), plt.Line2D(
            [], [], color="black", linestyle="solid", label="Function edge"
        ), plt.Line2D(
            [], [], color="black", linestyle="dashed", label="Resource edge"
        )]

        return legend_handles

    def customize_nodes(self):
        node_sizes = {}
        node_colors = {}
        for node in self.nodes:
            if node.type == NodeType.S3_BUCKET:
                node_sizes[node.name] = 500
                node_colors[node.name] = "blue"
            else:
                node_sizes[node.name] = 1000
                node_colors[node.name] = "green"
        node_sizes["End"] = 1000
        node_colors["End"] = "red"
        return node_sizes, node_colors

    def add_edges(self, graph):
        for node in self.nodes:
            if node.parent_function_node is not None:
                name = node.parent_function_node.name
            else:
                name = node.name
            if not node.edgeren:
                graph.add_edge(name, "End", style="solid")
            for edge in node.edgeren:
                if edge.type == NodeType.S3_BUCKET or node.type == NodeType.S3_BUCKET:
                    style = "dashed"
                else:
                    style = "solid"
                if edge.parent_function_node is not None:
                    graph.add_edge(name, edge.parent_function_node.name, style=style)
                else:
                    graph.add_edge(name, edge.name, style=style)
