import networkx as nx
import matplotlib.pyplot as plt
from node import Node, NodeType, SecurityType, NodeType, BroadType
import utility
import json
from policy import Policy, PERM
from collections import defaultdict

from policy_interface import PolicyInterface


class Graph:
    def __init__(self):
        self.nodes = []
        self.privateNodes = []
        self.suggested_policies = []
        self.policies = []

        # Maps objects to list of policies defined on them
        self.objectToPolicyMap = defaultdict(set)
        # Maps the tuple (subject, object, perm) to the policy
        self.policyMap = {}

        self.taintSources = defaultdict(set)

    def find_node(self, name):
        for node in self.nodes:
            if node.name == name:
                return node
        return None

    def find_node_by_repr(self, name):
        for node in self.nodes:
            if node.__repr__() == name:
                return node
        return None

    def find_node_by_physicalLocation(self, physicalLocation):
        for node in self.nodes:
            if node is not None and node.physicalLocation == physicalLocation:
                return node
        return None

    def find_node_or_create(self, name, physical_location=None):
        if physical_location is not None:
            node = self.find_node_by_physicalLocation(physical_location)
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

    # Returns the node with the given endpoint type, returns first node if multiple nodes have the given endpoint type
    @staticmethod
    def find_child_node_by_node_type(function_node, node_type):
        result = []
        for node in function_node.children:
            if node.nodeType == node_type:
                result.append(node)
        return result

    def init_policies(self):
        self.traverse(self.suggest_policy)

        policy_interface = PolicyInterface(self)
        # TODO: Change this to use policies modified by developers
        self.policies = policy_interface.get_policies()

    def annotate_edges(self):
        self.traverse(self.annotate_edge)

    def annotate_edge(self, node, nextNode, _):
        subject, object, perm = None, None, None
        match node.get_broad_node_type(), nextNode.get_broad_node_type():
            # Reads from a resource
            case BroadType.RESOURCE, BroadType.IDH_OTHER:
                subject = nextNode.parentFunctionNode
                object = node
                perm = PERM.READ
            # Execute Trigger from a resource
            case BroadType.RESOURCE, BroadType.IDH_PARAM:
                subject = node
                object = nextNode.parentFunctionNode
                perm = PERM.EXECUTE
            # Writes to a resource
            case BroadType.IDH_OTHER, BroadType.RESOURCE:
                subject = node.parentFunctionNode
                object = nextNode
                perm = PERM.WRITE
                self.checkIsAsRestrictive(node.parentFunctionNode, nextNode)

            # TODO: Cover other cases
        if subject is not None and object is not None and perm is not None:
            policy = self.get_policy(subject, object, perm)
            if policy is None:
                print('Edge is DENY', node.name, nextNode.name)
            else:
                eval_results = policy.eval()
                if eval_results:
                    print('Edge is Allow', node.name, nextNode.name)
                else:
                    missing_subject_attributes, missing_object_attributes, environment_attributes = eval_results
                    subject.missingAttributes.update(missing_subject_attributes)
                    object.missingAttributes.update(missing_object_attributes)
                    # TODO: Add required environment attributes somewhere

    def checkIsAsRestrictive(self, node, nextNode):
        policies = self.objectToPolicyMap[nextNode]
        taintSources = self.taintSources[node]
        for taintSource in taintSources:
            sourcePolicies = self.objectToPolicyMap[taintSource]
            if len(policies) < len(sourcePolicies):
                print('Policies not defined for all subjects')
                return False
            for sourcePolicy in sourcePolicies:
                # for policy in policies:
                policy = next((p for p in policies if p.subject == sourcePolicy.subject and p.perm == sourcePolicy.perm), None)
                if policy is None:
                    print('No policy found for', sourcePolicy)
                    return False
                elif not policy.isAsRestrictive(sourcePolicy):
                    print('Policy is not as restrictive', policy, sourcePolicy)
                    return False
        return True

    def generate_taints(self):
        # TODO: Move map initilization to where policies are confirmed by developer
        self.init_policy_maps()
        for node in self.objectToPolicyMap.keys():
            self.dfs_helper(node, set(), self.propagate_taints, node)

    def propagate_taints(self, _, nextNode, sourceNode):
        # Propagate taints on a read or flow edge
        if nextNode.get_broad_node_type() == BroadType.IDH_OTHER:
            self.taintSources[nextNode].add(sourceNode)

    def get_policy(self, sub, obj, perm):
        if (sub, obj, perm) in self.policyMap:
            return self.policyMap[(sub, obj, perm)]
        return None

    def traverse(self, apply_func):
        visited = set()
        for node in self.nodes:
            if node not in visited:
                visited.add(node)
                self.dfs_helper(node, visited, apply_func)

    def dfs_helper(self, node, visited, apply_func, apply_func_params=None):
        for nextNode in node.edges:
            if nextNode not in visited:
                visited.add(nextNode)
                apply_func(node, nextNode, apply_func_params)
                self.dfs_helper(nextNode, visited, apply_func, apply_func_params)

    # Avoid creating duplicate policies
    def fetch_or_suggest_policy(self, subject, object, perm):
        for policy in self.suggested_policies:
            policy = self.get_policy(subject, object, perm)
            if policy is not None:
                return policy
        policy = Policy(subject, object, perm)
        self.suggested_policies.append(policy)
        self.objectToPolicyMap[policy.object].add(policy)
        self.policyMap[(policy.subject, policy.object, policy.perm)] = policy
        return policy

    def init_policy_maps(self):
        self.objectToPolicyMap.clear()
        self.policyMap.clear()

        for policy in self.policies:
            self.objectToPolicyMap[policy.object].add(policy)
            # TODO: Flag duplicate tuple found here?
            self.policyMap[(policy.subject, policy.object, policy.perm)] = policy

    def suggest_policy(self, node, next_node, _):
        match node.get_broad_node_type(), next_node.get_broad_node_type():
            # Reads from a resource
            case BroadType.RESOURCE, BroadType.IDH_OTHER:
                self.fetch_or_suggest_policy(next_node.parentFunctionNode, node, PERM.READ)
            # Execute Trigger from a resource
            case BroadType.RESOURCE, BroadType.IDH_PARAM:
                self.fetch_or_suggest_policy(next_node.parentFunctionNode, node, PERM.EXECUTE)
            # Writes to a resource
            case BroadType.IDH_OTHER, BroadType.RESOURCE:
                self.fetch_or_suggest_policy(node.parentFunctionNode, next_node, PERM.WRITE)
            case BroadType.IDH_OTHER, BroadType.IDH_PARAM:
                self.fetch_or_suggest_policy(node.parentFunctionNode, next_node.parentFunctionNode, PERM.EXECUTE)
            # TODO: Cover all cases

    def init_security_labels(self, security_labels_file):
        labels = json.load(open(security_labels_file))
        private_locations = labels["private"]
        for location in private_locations:
            node = self.find_node_by_physicalLocation(location)
            if node is not None:
                node.securityType = SecurityType.PRIVATE
                self.privateNodes.append(node)
                print("Private node: ", node.name)
            else:
                print(f"Warning: {location} not found in graph")

        public_node_ids = labels["public"]
        for publicNodeId in public_node_ids:
            node = self.find_node(publicNodeId)
            if node is not None:
                node.securityType = SecurityType.PUBLIC
                print("Public node: ", node.name)
            else:
                print(f"Warning: {publicNodeId} not found in graph")

    def find_violations(self):
        for node in self.privateNodes:
            print(f"Finding publicly reachable nodes from {node.name}")
            self.dfs(node, [node])
            # if node.parentFunctionNode is None:
            #     for edge in node.edges:
            #         self.propagate_labels(child)

    # Traverse the graph and propagate private labels
    def dfs(self, node, path):
        if node.securityType == SecurityType.PUBLIC:
            print(f"Violation: Public node {node.name} is reachable via {path}")
            # TODO: Continue traversing even after public nodes
            return
        for edge in node.edges:
            # if edge.securityType == SecurityType.UNKNOWN:
            # edge.securityType = SecurityType.PRIVATE
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
        utility.print_line()
        for node in self.nodes:
            print(f"{node.name : <10}\
                  (Parent: {node.parentFunctionNode.name if node.parentFunctionNode else 'None'})\
                  (Edge: {[edge.name for edge in node.edges]})\
                  (child: {[child.name for child in node.child]})\)")

    def visualize(self, vis_out_path, graphic=False):
        if graphic:
            nodes = [node.name for node in self.nodes if node.parentFunctionNode is None]
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
                    print(
                        f"{node.name} ({node.parentFunctionNode.name if node.parentFunctionNode else 'None'}) -> End"
                    )
                for edge in node.edgeren:
                    print(
                        f"{node.name} ({node.parentFunctionNode.name if node.parentFunctionNode else 'None'}) -> {edge.name}"
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
            if node.parentFunctionNode is not None:
                name = node.parentFunctionNode.name
            else:
                name = node.name
            if not node.edgeren:
                graph.add_edge(name, "End", style="solid")
            for edge in node.edgeren:
                if edge.type == NodeType.S3_BUCKET or node.type == NodeType.S3_BUCKET:
                    style = "dashed"
                else:
                    style = "solid"
                if edge.parentFunctionNode is not None:
                    graph.add_edge(name, edge.parentFunctionNode.name, style=style)
                else:
                    graph.add_edge(name, edge.name, style=style)
