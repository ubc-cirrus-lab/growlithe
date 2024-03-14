class Policy:
    """
    Class to represent a policy.
    """

    def __init__(self, policy_str):
        """
        Initialize a Policy instance.
        """
        self.policy_str = policy_str
        self.start, self.end = policy_str.split(" => ")
        self.end, self.rhs = self.end.split(" ? ")
    
    def __str__(self) -> str:
        return self.policy_str

    def __repr__(self) -> str:
        return self.policy_str

class EdgePolicy:
    """
    Class to represent an edge policy.
    """

    def __init__(self, policy_json):
        """
        Initialize an EdgePolicy instance.
        """
        self.source_function = policy_json["source_function"]
        self.source = policy_json["source"]
        self.read_policy = policy_json["read_policy"]
        self.sink_function = policy_json["sink_function"]
        self.sink = policy_json["sink"]
        self.write_policy = policy_json["write_policy"]
        self.policy_json = policy_json

    def __str__(self) -> str:
        return f"EdgePolicy({self.source}, {self.read_policy}, {self.sink}, {self.write_policy})"
    
    def __repr__(self) -> str:
        return f"EdgePolicy({self.source}, {self.read_policy}, {self.sink}, {self.write_policy})"
    
    def to_json(self) -> str:
        return self.policy_json

def generate_default_edge_policy(edge):
    """
    Convert an edge to an edge policy.
    """
    edge.edge_policy = EdgePolicy(
        {
            "source_function": edge.source_node.function,
            "source": edge.source_node.policy_id,
            "read_policy": "allow",
            "sink_function": edge.sink_node.function,
            "sink": edge.sink_node.policy_id,
            "write_policy": "allow",
        }
    )