import boto3
import argparse
import json
import csv
import networkx as nx
import matplotlib.pyplot as plt

class GraphVisualization:
   
    def __init__(self):
        self.visual = []

    def addEdge(self, a, b):
        self.visual.append([a, b])

    def visualize(self):
        G = nx.DiGraph()
        G.add_edges_from(self.visual)
        pos = nx.spring_layout(G, seed=1)
        nx.draw_networkx(G, pos=pos, node_shape="s", node_color="None", node_size=1000)
        plt.show()

class Graph:
    def __init__(self, nodes):
        self.nodes = nodes
    
    @property
    def root(self):
        return self.nodes[0]


    def get_node(self, name):
        for node in self.nodes:
            if node.name == name:
                return node
        return None
    
    def plot_graph(self):
        graph = GraphVisualization()
        graph.addEdge('Start', self.root.name)
        for node in self.nodes:
            if node.children == []:
                graph.addEdge(node.name, 'End')
            for child in node.children:
                graph.addEdge(node.name, child.name)
        graph.visualize()

class Node:
    def __init__(self, name, handler, children):
        self.name = name
        self.handler = handler
        self.children = children
    
    def __repr__(self):
        return self.name
    
    def __str__(self):
        return self.name
    

def get_lambda_handler_name(arn):
    client = boto3.client('lambda')
    response = client.get_function(FunctionName=arn)
    return response['Configuration']['Handler']

def str_to_node(graph):
    for node in graph.nodes:
        children = []
        for child in node.children:
            children.append(graph.get_node(child))
        node.children = children

def create_graph(states):
    nodes = []
    for key, value in states.items():
        name = key
        handler = None
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
        nodes.append(Node(name, handler, children))
    graph = Graph(nodes)
    str_to_node(graph)
    graph.plot_graph()


def step_function_handler_extractor(state_machine_arn, output_file):
    client = boto3.client('stepfunctions')
    response = client.describe_state_machine(stateMachineArn=state_machine_arn)
    states = json.loads(response['definition'])['States']
    create_graph(states)
    handlers = []
    for key, value in states.items():
        if 'Resource' in value and 'lambda' in value['Resource']:
            if value['Resource'] == 'arn:aws:states:::lambda:invoke':
                handler = value['Parameters']['FunctionName']
            else:
                handler = value['Resource']
            handlers.append(f"{key}.{get_lambda_handler_name(handler)}")
    if output_file:
        with open(output_file, 'w') as f:
            writer = csv.writer(f)
            for handler in handlers:
                writer.writerow(handler.split('.'))
    for handler in handlers:
        print(handler)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('arn', help = 'State Machine ARN')
    parser.add_argument('-o', '--output', help = 'Output file name')
    args = parser.parse_args()

    step_function_handler_extractor(args.arn, args.output)