import networkx as nx
import matplotlib.pyplot as plt
from node import Node, Node_Type


class Graph:
    def __init__(self):
        self.nodes = []

    def find_node(self, name):
        for node in self.nodes:
            if node.name == name:
                return node
        return None

    def find_node_or_create(self, name):
        node = self.find_node(name)
        if node is None:
            node = Node(name)
            self.nodes.append(node)
        return node

    @property
    def root(self):
        return self.nodes[0]

    def visualize(self, graphic=False):
        if graphic:
            nodes = [node.name for node in self.nodes if node.parent_function is None]
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
            plt.show()
        else:
            for node in self.nodes:
                if node.children == []:
                    print(
                        f"{node.name} ({node.parent_function.name if node.parent_function else 'None'}) -> End"
                    )
                for child in node.children:
                    print(
                        f"{node.name} ({node.parent_function.name if node.parent_function else 'None'}) -> {child.name}"
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
            if node.type == Node_Type.RESOURCE:
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
            if node.parent_function is not None:
                name = node.parent_function.name
            else:
                name = node.name
            if node.children == []:
                G.add_edge(name, "End", style="solid")
            for child in node.children:
                if child.type == Node_Type.RESOURCE or node.type == Node_Type.RESOURCE:
                    style = "dashed"
                else:
                    style = "solid"
                if child.parent_function is not None:
                    G.add_edge(name, child.parent_function.name, style=style)
                else:
                    G.add_edge(name, child.name, style=style)
