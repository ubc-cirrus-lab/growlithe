import utility
from node import BroadType
from policy import Policy, PERM, PolicyGroup
import json


class PolicyInterface:
    def __init__(self, graph) -> None:
        self.suggested_policies = graph.suggested_policies
        self.graph = graph

    def write_help(self, f):
        f.write("# Policies are written in the following format:\n")
        f.write("# <subject>, <object>, <permission>: <allowFilters>\n")
        f.write("#\n")
        f.write("# Available subjects and objects:\n")
        for node in self.graph.nodes:
            broad_type = node.get_broad_node_type()
            if broad_type == BroadType.COMPUTE or broad_type == BroadType.RESOURCE:
                f.write(f"#  -  {node}, \n")
        f.write("# Available permissions:\n")
        f.write("#  -  READ\n")
        f.write("#  -  WRITE\n")
        f.write("#  -  EXECUTE\n")
        f.write("# Available allowFilters:\n")
        f.write("#  -  ALLOW\n")
        f.write("#  -  DENY\n")
        with open(utility.get_rel_path("filtersConfig.json"), "r") as filters_config:
            filters_config = json.load(filters_config)
            for filter in filters_config:
                f.write(f"#  -  {filter}\n")
        f.write("\n")

    def write_policies(self, path):
        f = open(path, "w")
        self.write_help(f)
        for policy in self.suggested_policies:
            f.write(policy.__repr__())
            f.write("\n")
        f.close()

    @staticmethod
    def _validate_policy(subject, object, perm, policy):
        if subject is None:
            print(f"Invalid subject: {policy}")
            exit(1)
        if object is None:
            print(f"Invalid object: {policy}")
            exit(1)
        if perm is None:
            print(f"Invalid permission: {policy}")
            exit(1)

    def _extract_and_validate_policy(self, policy, line):
        subject, object, perm = list(map(str.strip, policy.split(",")))
        subject = self.graph.find_node_by_repr(subject)
        object = self.graph.find_node_by_repr(object)
        try:
            perm = PERM[perm.upper()]
        except KeyError:
            print(f"Invalid permission: {line}")
            exit(1)
        PolicyInterface._validate_policy(subject, object, perm, line)
        return subject, object, perm

    def parse_policies(self, path):
        policies = []
        f = open(path, "r")
        for line in f.readlines():
            if line.startswith("#") or line == "\n":
                continue
            is_denied = False
            policy = line.split(":")
            if len(policy) != 2:
                print("Invalid policy format: ", line)
                exit(1)
            subject, object, perm = self._extract_and_validate_policy(policy[0], line)
            policy_groups = list(map(str.strip, policy[1].split("OR")))
            policy = Policy(subject, object, perm)
            for policy_group in policy_groups:
                if policy_group == "ALLOW":
                    policy.policyGroups = set()
                    break
                elif policy_group == "DENY":
                    is_denied = True
                    break
                allow_filters = list(map(str.strip, policy_group.split("AND")))
                for filter in allow_filters:
                    function = filter.split("(")[0]
                    params = list(map(str.strip, filter.split("(")[1][:-1].split(",")))
                    policy_group = PolicyGroup()
                    policy_group.add_filter(function, params)
                    policy.policyGroups.add(policy_group)
            if not is_denied:
                policies.append(policy)
        f.close()
        return policies

    def get_policies(self):
        self.write_policies(utility.get_rel_path("policies.txt"))
        print("Suggested policies written to policies.txt.")
        print("Please update the policies in policies.txt and save the file.")
        input("Press Enter to continue...")
        return self.parse_policies(utility.get_rel_path("policies.txt"))
