import json
import pathlib
from enum import Enum
from typing import Tuple, List

from src.graph.node import Node
from src.policy import allow_filters
from src import utility
from src.logger import logger


class PERM(Enum):
    READ = 1
    WRITE = 2
    EXECUTE = 3

    def __str__(self) -> str:
        return self.name


filters_config = json.loads(open(f'{pathlib.Path(__file__).parent.resolve()}/filtersConfig.json').read())


class Policy:
    def __init__(self, subject, object, perm):
        # Missing subject, object, perm means deny
        self.subject: Node = subject
        self.object: Node = object
        self.perm: PERM = perm

        # OR Separated policy groups, empty set means allow
        self.policy_groups: set[PolicyGroup] = set()

    def __repr__(self):
        return f"Policy({self.subject.__repr__()}, {self.object.__repr__()}, {self.perm.__repr__()})"

    def __str__(self):
        msg = f"{self.subject.policy_str}, {self.object.policy_str}, {self.perm}: "
        if len(self.policy_groups) == 0:
            msg += "ALLOW"
        else:
            for policyGroup in self.policy_groups:
                msg += f"{policyGroup.allow_filters}"
        return msg

    def eval(self):
        if len(self.policy_groups) == 0:
            return True
        else:
            # TODO: Update based on interface of allowFilters
            missing_subject_attributes = set()
            missing_object_attributes = set()
            environment_attributes = set()

            for policyGroup in self.policy_groups:
                policy_group_result = True
                missing_subject_attributes_in_policy_group = set()
                missing_object_attributes_in_policy_group = set()
                environment_attributes_in_policy_group = set()

                for allow_filter in policyGroup.allow_filters:
                    missing_subject_attributes_in_policy_group.update(
                        Policy.get_missing_node_attributes(self.subject,
                                                           filters_config[allow_filter[0]]['subject_attributes']))
                    missing_object_attributes_in_policy_group.update(
                        Policy.get_missing_node_attributes(
                            self.object, filters_config[allow_filter[0]]['object_attributes']))
                    # TODO: Check assumption if all environment attributes are available only at runtime
                    environment_attributes_in_policy_group.update(
                        filters_config[allow_filter[0]]['environment_attributes'])

                    if len(missing_subject_attributes_in_policy_group) == 0 and \
                            len(missing_object_attributes_in_policy_group) == 0 and \
                            len(environment_attributes_in_policy_group) == 0:
                        # TODO: environment attributes
                        if not getattr(allow_filters, allow_filter[0])(self.subject.attributes,
                                                                       self.object.attributes, [], allow_filter[1]):
                            policy_group_result = False
                            # TODO: Flag if other allowFilters exists
                    else:
                        policy_group_result = False

                if policy_group_result:
                    # TODO: Flag if other policy groups exists
                    return True
                else:
                    missing_subject_attributes.update(missing_subject_attributes_in_policy_group)
                    missing_object_attributes.update(missing_object_attributes_in_policy_group)
                    environment_attributes.update(environment_attributes_in_policy_group)
            return missing_subject_attributes, missing_object_attributes, environment_attributes

    @staticmethod
    def get_missing_node_attributes(node, attribute_list):
        missing_attributes = []
        for attribute in attribute_list:
            if attribute not in node.attributes.keys():
                missing_attributes.append(attribute)
        return missing_attributes

    def is_as_restrictive(self, policy2):
        # If policy1 has more policy groups, it allows in more cases as
        # policy groups are OR separated
        if len(self.policy_groups) > len(policy2.policy_groups):
            return False

        for pg in self.policy_groups:
            found_equivalent = False
            for pg2 in policy2.policy_groups:
                if pg.get_hash() == pg2.get_hash():
                    found_equivalent = True
                    break
            if not found_equivalent:
                logger.debug(f"Did not find equivalent policy group for {pg}")
                return False

        return True

    def add_runtime_checks(self, idh_node):
        if self.perm == PERM.READ:
            python_parseable_policy = self.to_python()
            utility.add_assertion(self.subject.file_path, idh_node.physical_location, python_parseable_policy)

    def to_python(self):
        # TODO: handle parantheses and order of evaluation
        policy = ""
        for group in self.policy_groups:
            for allow_filter in group.allow_filters:
                arguments = ""
                filter = allow_filter[0]
                constants = allow_filter[1]
                constant_attributes = filters_config[filter]['policy_constants']
                for carg, arg in zip(constant_attributes, constants):
                    arguments += f"{carg}=event['{arg}'], "

                subject_attributes = filters_config[filter]['subject_attributes']
                for attr in [s for s in subject_attributes if s not in constant_attributes]:
                    arguments += f"{attr}=event['{attr}'], "
                arguments = arguments[:-2]  # remove the extra " ," at the end
                policy += f"{filter}({arguments}) and "
            policy = policy[:-4]  # remove the extra " or " at the end
            policy += " or "
        return policy[:-5]


class PolicyGroup:
    def __init__(self) -> None:
        # AND Separated filters as tuple of (func_name, policy_constants_array)
        self.allow_filters: List[Tuple[str, List]] = list()
        self.hash = None

    def get_hash(self):
        return self.hash
        # return ",".join([filter for (filter, _) in self.allow_filters].sort())

    def add_filter(self, function, params):
        filter = (function, params)
        self.allow_filters.append(filter)
        # TODO: Fix and set policy hash. Discuss if we should compare prefixes of filters instead
        # self.hash = utility.get_sorted_array_hash(self.allow_filters)
