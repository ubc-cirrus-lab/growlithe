import csv
import glob
import os
import networkx as nx
import matplotlib.pyplot as plt


class GraphVisualization:
   
    def __init__(self):
        self.visual = {}
        self.functions = []
        self.labels = set()

    def addEdge(self, a, b, function, label=""):
        self.visual[tuple([a, b])] = label
        self.functions.append(function)
        self.labels.update([a, b, function])

    def visualize(self):
        G = nx.DiGraph()
        G.add_edges_from([list(a) for a in self.visual.keys()])
        pos = nx.spring_layout(G, k=0.7, seed=0)
        nx.draw_networkx_nodes(G, pos, nodelist=self.functions, node_color="tab:red", alpha=0.1, node_size=400)
        nx.draw_networkx_labels(G, pos, labels={a: a for a in self.labels}, font_size=8)
        nx.draw_networkx_edges(G, pos, width=1)
        nx.draw_networkx_edge_labels(G, pos, edge_labels=self.visual, font_size=8)
        plt.show()


class Edge:
    def __init__(self, start, end, label, file):
        self.start = start
        self.end = end
        self.label = label
        self.file = file

    def __str__(self):
        return f'{self.start} -> {self.end} [label="{self.label}"]'


def visualize(edges):
    graph = GraphVisualization()
    for edge in edges:
        graph.addEdge(edge.start, edge.end, edge.file, edge.label)
    graph.visualize()

def read_variable(file_name, line_start, offset_start, line_end, offset_end):
    variable = ''
    with open(file_name, 'r') as f:
        lines = f.readlines()
        if line_start == line_end:
            variable = lines[line_start-1][offset_start-1:offset_end]
        else:
            variable = lines[line_start-1][offset_start-1:]
            for i in range(line_start, line_end-1):
                variable += lines[i]
            variable += lines[line_end-1][:offset_end]
    return variable

def main():
    os.chdir('../code')
    edges = []
    for filename in glob.glob('query_results/*.csv'):
        with open(filename, 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                file_name = row[4][1:]
                variable = read_variable(file_name, int(row[5]), int(row[6]), int(row[7]), int(row[8]))
                label = row[3]
                if label in ['write', 'post', 'put']:
                    start = file_name
                    end = variable
                else:
                    start = variable
                    end = file_name
                edges.append(Edge(start, end, label, file_name))

    for edge in edges:
        print(edge)
    visualize(edges)

if __name__ == '__main__':
    main()