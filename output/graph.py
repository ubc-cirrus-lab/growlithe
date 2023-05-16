import networkx as nx
import matplotlib.pyplot as plt
import argparse
import boto3
import json
from enum import Enum
import re

class Node_Type(Enum):
    FUNCTION = 1
    RESOURCE = 2

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

            edge_styles = {edge: G.edges[edge]["style"] for edge in G.edges}

            pos = nx.spring_layout(G, seed=5)
            nx.draw_networkx(G, pos=pos, with_labels=True, arrows=True, node_size=[node_sizes[n] for n in nodes], node_color=[node_colors[n] for n in nodes], style=[edge_styles[edge] for edge in G.edges])

            legend_handles = []
            legend_handles.append(plt.Line2D([], [], color="blue", marker='o', linestyle='None', markersize=10, label="resource"))
            legend_handles.append(plt.Line2D([], [], color="green", marker='o', linestyle='None', markersize=10, label="function"))
            legend_handles.append(plt.Line2D([], [], color="red", marker='o', linestyle='None', markersize=10, label="end"))

            legend_handles.append(plt.Line2D([], [], color="black", linestyle="solid", label="Function edge"))
            legend_handles.append(plt.Line2D([], [], color="black", linestyle="dashed", label="Resource edge"))
            plt.legend(handles=legend_handles, loc="lower right")
            plt.show()
        else:
            for node in self.nodes:
                if node.children == []:
                    print(f"{node.name} ({node.parent_function.name if node.parent_function else 'None'}) -> End")
                for child in node.children:
                    print(f"{node.name} ({node.parent_function.name if node.parent_function else 'None'}) -> {child.name}")
    


class Node:
    def __init__(self, name):
        self.name = name
        self.children = []
        self.type = None
        self.parent_function = None
    
    def add_child(self, child):
        self.children.append(child)



def get_children(value):
    children = []
    if 'Resource' in value and 'lambda' in value['Resource']:
        if value['Resource'] == 'arn:aws:states:::lambda:invoke':
            handler = value['Parameters']['FunctionName']
        else:
            handler = value['Resource']
    if 'Next' in value:
        children.append(value['Next'])
    if 'Choices' in value:
        for choice in value['Choices']:
            children.append(choice['Next'])
    if 'Catch' in value:
        for catch in value['Catch']:
            children.append(catch['Next'])
    return handler, children

def get_lambda_handler_name(arn):
    client = boto3.client('lambda')
    response = client.get_function(FunctionName=arn)
    return response['Configuration']['Handler']

def step_function_handler_extractor(state_machine_arn):
    client = boto3.client('stepfunctions')
    response = client.describe_state_machine(stateMachineArn=state_machine_arn)
    states = json.loads(response['definition'])['States']
    handlers = []
    graph = Graph()
    for key, value in states.items():
        if 'Resource' in value and 'lambda' in value['Resource']:
            handler, children = get_children(value)
            handlers.append(f"{key}.{get_lambda_handler_name(handler)}.{children}")
            node = graph.find_node_or_create(key)
            node.type = Node_Type.FUNCTION
            for child in children:
                child_node = graph.find_node_or_create(child)
                child_node.type = Node_Type.FUNCTION
                node.add_child(child_node)
    return graph

def get_results(results_file):
    with open(results_file, 'r') as f:
        sarif_log = json.load(f)
    results = sarif_log['runs'][0]['results']
    return results

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

def read_variable(file_name, line_start, offset_start, line_end, offset_end):
    variable = ''
    with open(f'../src/{file_name}', 'r') as f:
        lines = f.readlines()
        if line_start == line_end:
            variable = lines[line_start-1][offset_start-1:offset_end-1]
        else:
            variable = lines[line_start-1][offset_start-1:]
            for i in range(line_start, line_end-1):
                variable += lines[i]
            variable += lines[line_end-1][:offset_end]
    return variable

def match_boto3(result, function_node, graph):
    for line in result['message']['text'].split('\n'):
        action_pattern = r"from \[(\w+)\]\((\d+)\) ==> \[(\w+)\]\((\d+)\)"
        match = re.search(action_pattern, line)
        if match:
            node = graph.find_node_or_create(match.group(1))
            node.type = Node_Type.RESOURCE
            if match.group(1) == 'event':
                node.parent_function = graph.find_node_or_create(function_node.name)
                print(f"should be {function_node.name}")
                print(f"is {node.parent_function.name}")
            child = graph.find_node_or_create(match.group(3))
            child.type = Node_Type.RESOURCE
            node.add_child(child)



def main(arn):
    graph = step_function_handler_extractor(arn)
    
    functions = graph.nodes.copy()
    for node in functions:
        result = get_results(f"ImageProcessing{node.name}.sarif")
        if len(result) > 0:
            match_boto3(result[0], node, graph)
    
    graph.visualize(graphic=True)
        

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('arn', help = 'State Machine ARN')
    args = parser.parse_args()
    main(args.arn)