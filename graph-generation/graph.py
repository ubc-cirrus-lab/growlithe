import networkx as nx
import matplotlib.pyplot as plt
from node import Node, NodeType, SecurityType, NodeType, BroadType
import utility
import json
from policy import Policy, PERM

class Graph:
    def __init__(self):
        self.nodes = []
        self.privateNodes = []
        self.suggestedPolicies = []
        self.policies = []

    def find_node(self, name):
        for node in self.nodes:
            if node.name == name:
                return node
        return None
    
    def find_node_by_physicalLocation(self, physicalLocation):
        for node in self.nodes:
            if node != None and node.physicalLocation == physicalLocation:
                return node
        return None

    def find_node_or_create(self, name, physicalLocation=None):
        if physicalLocation is not None:
            node = self.find_node_by_physicalLocation(physicalLocation)
        else:
            node = self.find_node(name)
        if node is None:
            node = Node(name)
            self.nodes.append(node)
            if '/' in name and not node.is_root_node():
                parentName = name.rsplit("/", 1)[0]
                parentNode = self.find_node_or_create(parentName)
                parentNode.add_edge(node)
                node.add_parent(parentNode)
        return node

    # Returns the node with the given endpoint type, returns first node if multiple nodes have the given endpoint type
    def find_child_node_by_node_type(self, function_node, nodeType):
        result = []
        for node in function_node.children:
            if node.nodeType == nodeType:
                result.append(node)
                # print(result)
        return result

    def init_policies(self):
        self.traverse(self.suggestPolicy)

    def traverse(self, applyFunc):
        visited = set()
        for node in self.nodes:
            if node not in visited:
                visited.add(node)
                self.dfs_helper(node, visited, applyFunc)

    def dfs_helper(self, node, visited, applyFunc):
        for edge in node.edges:
            if edge not in visited:
                visited.add(edge)
                applyFunc(node, edge)
                self.dfs_helper(edge, visited, applyFunc)

    def suggestPolicy(self, node, edge):
        match node.get_broad_node_type(), edge.get_broad_node_type():
            # Reads from a resource
            case BroadType.RESOURCE, BroadType.IDH_OTHER:
                self.suggestedPolicies.append(Policy(edge.parentFunctionNode, node, PERM.READ))
            # Execute Trigger from a resource
            case BroadType.RESOURCE, BroadType.IDH_PARAM:
                self.suggestedPolicies.append(Policy(edge.parentFunctionNode, node, PERM.EXECUTE))
            # Writes to a resource
            case BroadType.IDH_OTHER, BroadType.RESOURCE:
                self.suggestedPolicies.append(Policy(node.parentFunctionNode, edge, PERM.WRITE))
            # TODO: Cover all cases

    def init_security_labels(self, security_labels_file):
        labels = json.load(open(security_labels_file))
        privateLocations = labels["private"]
        for location in privateLocations:
            node = self.find_node_by_physicalLocation(location)
            if node is not None:
                node.securityType = SecurityType.PRIVATE
                self.privateNodes.append(node)
                print("Private node: ", node.name)
            else:
                print(f"Warning: {location} not found in graph")
        
        publicNodeIds = labels["public"]
        for publicNodeId in publicNodeIds:
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
        # print(f"Propagating labels for {node.name} {'ParentFunc - ' + node.parentFunctionNode.name if node.parentFunctionNode else ''}")
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
                if node.edgeren == []:
                    print(
                        f"{node.name} ({node.parentFunctionNode.name if node.parentFunctionNode else 'None'}) -> End"
                    )
                for edge in node.edgeren:
                    print(
                        f"{node.name} ({node.parentFunctionNode.name if node.parentFunctionNode else 'None'}) -> {edge.name}"
                    )

    def customize_legends(self):
        legend_handles = []
        legend_handles.append(
                plt.Line2D(
                    [],
                    [],
                    color="blue",
                    marker="o",
                    linestyle="None",
                    markersize=10,
                    label="resource",
                )
            )
        legend_handles.append(
                plt.Line2D(
                    [],
                    [],
                    color="green",
                    marker="o",
                    linestyle="None",
                    markersize=10,
                    label="function",
                )
            )
        legend_handles.append(
                plt.Line2D(
                    [],
                    [],
                    color="red",
                    marker="o",
                    linestyle="None",
                    markersize=10,
                    label="end",
                )
            )

        legend_handles.append(
                plt.Line2D(
                    [], [], color="black", linestyle="solid", label="Function edge"
                )
            )
        legend_handles.append(
                plt.Line2D(
                    [], [], color="black", linestyle="dashed", label="Resource edge"
                )
            )
        
        return legend_handles

    def customize_nodes(self):
        node_sizes = {}
        node_colors = {}
        for node in self.nodes:
            if node.type == NodeType.RESOURCE:
                node_sizes[node.name] = 500
                node_colors[node.name] = "blue"
            else:
                node_sizes[node.name] = 1000
                node_colors[node.name] = "green"
        node_sizes["End"] = 1000
        node_colors["End"] = "red"
        return node_sizes, node_colors

    def add_edges(self, G):
        for node in self.nodes:
            if node.parentFunctionNode is not None:
                name = node.parentFunctionNode.name
            else:
                name = node.name
            if node.edgeren == []:
                G.add_edge(name, "End", style="solid")
            for edge in node.edgeren:
                if edge.type == NodeType.RESOURCE or node.type == NodeType.RESOURCE:
                    style = "dashed"
                else:
                    style = "solid"
                if edge.parentFunctionNode is not None:
                    G.add_edge(name, edge.parentFunctionNode.name, style=style)
                else:
                    G.add_edge(name, edge.name, style=style)
