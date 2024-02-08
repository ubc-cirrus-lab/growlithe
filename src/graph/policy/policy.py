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
        self.start = policy_json["flow_from"]
        self.read_policy = policy_json["flow_from_policy"]
        self.end = policy_json["flow_to"]
        self.write_policy = policy_json["flow_to_policy"]

    def __str__(self) -> str:
        return f"EdgePolicy({self.start}, {self.read_policy}, {self.end}, {self.write_policy})"
    
    def __repr__(self) -> str:
        return f"EdgePolicy({self.start}, {self.read_policy}, {self.end}, {self.write_policy})"