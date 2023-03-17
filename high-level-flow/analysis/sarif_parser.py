import json
import argparse
import csv
import networkx as nx
import matplotlib.pyplot as plt
import ast
import re


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

class Handler:
    def __init__(self, name, script, function, children):
        self.name = name
        self.script = script
        self.function = function
        self.children = children
        self.results = []

def read_variable(file_name, line_start, offset_start, line_end, offset_end):
    variable = ''
    with open(f'src/{file_name}', 'r') as f:
        lines = f.readlines()
        if line_start == line_end:
            variable = lines[line_start-1][offset_start-1:offset_end-1]
        else:
            variable = lines[line_start-1][offset_start-1:]
            for i in range(line_start, line_end-1):
                variable += lines[i]
            variable += lines[line_end-1][:offset_end]
    return variable

def get_results(results_file):
    with open(results_file, 'r') as f:
        sarif_log = json.load(f)

    results = sarif_log['runs'][0]['results']
    return results


def get_handlers(handler_file):
    handlers = []
    with open(handler_file, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            handlers.append(Handler(row[0], row[1], row[2], ast.literal_eval(row[3])))
    return handlers


def match_results(results, handlers):
    for result in results:
        for handler in handlers:
            if handler.name in result['ruleId']:
                if 'resource' in result['message']['text']:
                    match_boto3(result, handler)
                break

def match_boto3(result, handler):
    reources = {}
    for line in result['message']['text'].split('\n'):
        action_pattern = r"uses: \[(\w+)\]\((\d+)\)"
        match = re.search(action_pattern, line)
        if match:
            if match.group(1) not in reources:
                reources[match.group(1)] = []
            reources[match.group(1)].append(int(match.group(2)))
    for resource, ids in reources.items():
        location = result['locations'][0]
        variable = f"{get_variable(location)} ({resource}): "
        for loc in result['relatedLocations']:
            if loc['id'] in ids:
                variable += f"{get_variable(loc)}, "
        msg = ''
        actions = {}
        for line in result['message']['text'].split('\n'):
            action_pattern = r"uses: \[\w+\]\((\d+)\) action: \[(\w+)\]\((\d+)\)"
            match = re.search(action_pattern, line)
            if match:
                for loc in result['relatedLocations']:
                    if loc['id'] == int(match.group(3)):
                        if match.group(2) not in actions:
                            actions[match.group(2)] = []
                        actions[match.group(2)] += [get_variable(loc)]
                        break
        for action, variables in actions.items():
            msg += f"{action}: {', '.join(variables)}\n"
        handler.results.append({f"""{variable}""": msg})

def get_variable(location):
    file_name = location['physicalLocation']['artifactLocation']['uri']
    start_line = location['physicalLocation']['region']['startLine']
    start_column = location['physicalLocation']['region']['startColumn']
    if 'endLine' in location['physicalLocation']['region']:
        end_line = location['physicalLocation']['region']['endLine']
    else:
        end_line = start_line
    end_column = location['physicalLocation']['region']['endColumn']
    variable = read_variable(file_name, start_line, start_column, end_line, end_column)
    return variable

def draw_graph(handlers):
    edges = []
    for handler in handlers:
        for child in handler.children:
            edges.append(Edge(handler.name, child, "", child))
        for result in handler.results:
            for variable, message in result.items():
                if message in ['write', 'post', 'put']:
                    start = handler.name
                    end = variable
                else:
                    start = variable
                    end = handler.name
                edges.append(Edge(start, end, message, handler.name))
    visualize(edges)

def main(results_file, handler_file):
    results = get_results(results_file)
    handlers = get_handlers(handler_file)
    match_results(results, handlers)
    draw_graph(handlers)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('results_file', help = 'SARIF file containing results')
    parser.add_argument('handler_file', help = 'CSV file containing handlers')
    args = parser.parse_args()
    

    main(args.results_file, args.handler_file)