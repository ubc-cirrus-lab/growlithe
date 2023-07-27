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

filtersConfig = json.loads(open(utility.get_rel_path('filtersConfig.json')).read())

class Policy:
    def __init__(self, subject, object, perm):
        # Missing subject, object, perm means deny
        self.subject: Node = subject
        self.object: Node = object
        self.perm: PERM = perm

        # OR Separated policy groups, empty set means allow
        self.policyGroups: set(PolicyGroup) = set()
    
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
            missingSubjectAttributes = set()
            missingObjectAttributes = set()
            environmentAttributes = set()

            for policyGroup in self.policyGroups:
                policyGroupResult = True
                missingSubjectAttributesInPolicyGroup = set()
                missingObjectAttributesInPolicyGroup = set()
                environmentAttributesInPolicyGroup = set()

                for allowFilter in policyGroup.allow_filters:
                    print(filtersConfig[allowFilter[0]]['subject_attributes'])
                    missingSubjectAttributesInPolicyGroup.update(\
                        self.getMissingNodeAttributes(self.subject, filtersConfig[allowFilter[0]]['subject_attributes']))
                    missingObjectAttributesInPolicyGroup.update(\
                        self.getMissingNodeAttributes(self.object, filtersConfig[allowFilter[0]]['object_attributes']))
                    # TODO: Check assumption if all environment attributes are avaiable only at runtime
                    environmentAttributesInPolicyGroup.update(filtersConfig[allowFilter[0]]['environment_attributes'])

                    if len(missingSubjectAttributesInPolicyGroup) == 0 and\
                          len(missingObjectAttributesInPolicyGroup) == 0 and\
                              len(environmentAttributesInPolicyGroup) == 0:
                        # TODO: environment attributes
                        if not getattr(allowFilters, allowFilter[0])(self.subject.attributes,
                            self.object.attributes, [], allowFilter[1]):
                            policyGroupResult = False
                            # TODO: Flag if other allowFilters exists
                    else:
                        policyGroupResult = False
                        
                if policyGroupResult:
                    # TODO: Flag if other policy groups exists
                    return True
                else:
                    missingSubjectAttributes.update(missingSubjectAttributesInPolicyGroup)
                    missingObjectAttributes.update(missingObjectAttributesInPolicyGroup)
                    environmentAttributes.update(environmentAttributesInPolicyGroup)
            return missingSubjectAttributes, missingObjectAttributes, environmentAttributes

    def getMissingNodeAttributes(self, node, attributeList):
        missingAttributes = []
        for attribute in attributeList:
            if attribute not in node.attributes.keys():
                missingAttributes.append(attribute)
        return missingAttributes

    def isAsRestrictive(self, incomingPolicy):
        incomingPolicyGroups = incomingPolicy.policyGroups.copy()
        policyGroups = self.policyGroups.copy()
        if len(policyGroups) > len(incomingPolicyGroups):
            return False

        for incomingPolicyGroup in incomingPolicyGroups:
            for policyGroup in policyGroups:
                if policyGroup.get_hash() == incomingPolicyGroup.get_hash():
                    policyGroups.remove(policyGroup)
                    incomingPolicyGroups.remove(incomingPolicyGroup)

        return policyGroups == set()

class PolicyGroup:
    def __init__(self) -> None:
        # AND Separated filters as typle of (func_name, policy_constants_array)
        self.allow_filters: List(Tuple(str, List)) = list()
    
    def get_hash(self):
        return ",".join([filter for (filter, _) in self.allow_filters].sort())

    def add_filter(self, function, params):
        filter = (function, params)
        self.allow_filters.append(filter)
