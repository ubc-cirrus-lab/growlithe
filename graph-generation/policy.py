from node import Node
from enum import Enum
from typing import Tuple, Set, List
import json
import allowFilters
import utility


class PERM(Enum):
    READ = 1
    WRITE = 2
    EXECUTE = 3

    def __str__(self) -> str:
        return self.name


filters_config = json.loads(open(utility.get_rel_path('filtersConfig.json')).read())


class Policy:
    def __init__(self, subject, object, perm):
        # Missing subject, object, perm means deny
        self.subject: Node = subject
        self.object: Node = object
        self.perm: PERM = perm

        # OR Separated policy groups, empty set means allow
        self.policyGroups: set[PolicyGroup] = set()

    def __repr__(self):
        msg = f"{self.subject}, {self.object}, {self.perm}: "
        if len(self.policyGroups) == 0:
            msg += "ALLOW"
        else:
            for policyGroup in self.policyGroups:
                msg += f"{policyGroup.allow_filters}"
        return msg

    def eval(self):
        if len(self.policyGroups) == 0:
            return True
        else:
            # TODO: Update based on interface of allowFilters
            missing_subject_attributes = set()
            missing_object_attributes = set()
            environment_attributes = set()

            for policyGroup in self.policyGroups:
                policy_group_result = True
                missing_subject_attributes_in_policy_group = set()
                missing_object_attributes_in_policy_group = set()
                environment_attributes_in_policy_group = set()

                for allowFilter in policyGroup.allow_filters:
                    print(filters_config[allowFilter[0]]['subject_attributes'])
                    missing_subject_attributes_in_policy_group.update(
                        Policy.get_missing_node_attributes(self.subject,
                                                           filters_config[allowFilter[0]]['subject_attributes']))
                    missing_object_attributes_in_policy_group.update(
                        Policy.get_missing_node_attributes(
                            self.object, filters_config[allowFilter[0]]['object_attributes']))
                    # TODO: Check assumption if all environment attributes are available only at runtime
                    environment_attributes_in_policy_group.update(
                        filters_config[allowFilter[0]]['environment_attributes'])

                    if len(missing_subject_attributes_in_policy_group) == 0 and \
                            len(missing_object_attributes_in_policy_group) == 0 and \
                            len(environment_attributes_in_policy_group) == 0:
                        # TODO: environment attributes
                        if not getattr(allowFilters, allowFilter[0])(self.subject.attributes,
                                                                     self.object.attributes, [], allowFilter[1]):
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


    def isAsRestrictive(self, policy2):

        # If policy1 has more policy groups, it allows in more cases as
        # policy groups are OR separated
        if len(self.policyGroups) > len(policy2.policyGroups):
            return False

        for pg in self.policyGroups:
            foundEquivalent = False
            for pg2 in policy2.policyGroups:
                if pg.get_hash() == pg2.get_hash():
                    # policyGroups1.remove(pg)
                    # policyGroups2.remove(pg2)
                    foundEquivalent = True
                    break
            if not foundEquivalent:
                print("Did not find equivalent policy group for ", pg)
                return False

        return True

class PolicyGroup:
    def __init__(self) -> None:
        # AND Separated filters as typle of (func_name, policy_constants_array)
        self.allow_filters: List(Tuple(str, List)) = list()
    
    def get_hash(self):
        return ",".join([filter for (filter, _) in self.allow_filters].sort())

    def add_filter(self, function, params):
        filter = (function, params)
        self.allow_filters.append(filter)
