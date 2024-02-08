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
        self.source = policy_json["source"]
        self.read_policy = policy_json["read_policy"]
        self.sink = policy_json["sink"]
        self.write_policy = policy_json["write_policy"]

    def __str__(self) -> str:
        return f"EdgePolicy({self.source}, {self.read_policy}, {self.sink}, {self.write_policy})"
    
    def __repr__(self) -> str:
        return f"EdgePolicy({self.source}, {self.read_policy}, {self.sink}, {self.write_policy})"