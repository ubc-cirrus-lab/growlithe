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
            missingSubjectAttributes = []
            missingObjectAttributes = []
            environmentAttributes = []

            for policyGroup in self.policyGroups:
                policyGroupResult = True
                missingSubjectAttributesInPolicyGroup = []
                missingObjectAttributesInPolicyGroup = []
                environmentAttributesInPolicyGroup = []

                for allowFilter in policyGroup.allowFilters:
                    missingSubjectAttributesInPolicyGroup.append(\
                        self.getMissingNodeAttributes(self.subject, filtersConfig[allowFilter]['subject']))
                    missingObjectAttributesInPolicyGroup.append(\
                        self.getMissingNodeAttributes(self.object, filtersConfig[allowFilter]['object']))
                    # TODO: Check assumption if all environment attributes are avaiable only at runtime
                    environmentAttributesInPolicyGroup.append(filtersConfig[allowFilter]['environment'])

                    if len(missingSubjectAttributesInPolicyGroup) != 0 and\
                          len(missingObjectAttributesInPolicyGroup) != 0 and\
                              len(environmentAttributesInPolicyGroup) != 0:
                        if not getattr(allowFilters, allowFilter[0])(self.subject.attributes,
                            self.object.attributes, filtersConfig[allowFilter]['policyConstants']):
                            policyGroupResult = False
                            # TODO: Flag if other allowFilters exists
                    else:
                        policyGroupResult = False
                        
                if policyGroupResult:
                    # TODO: Flag if other policy groups exists
                    return True
                else:
                    missingSubjectAttributes.append(missingSubjectAttributesInPolicyGroup)
                    missingObjectAttributes.append(missingObjectAttributesInPolicyGroup)
                    environmentAttributes.append(environmentAttributesInPolicyGroup)
            return missingSubjectAttributes, missingObjectAttributes, environmentAttributes

    def getMissingNodeAttributes(node, attributeList):
        missingAttributes = []
        for attribute in attributeList:
            if attribute not in node.attributes.keys():
                missingAttributes.append(attribute)
        return missingAttributes

class PolicyGroup:
    def __init__(self, allow_filters) -> None:
        # AND Separated filters as typle of (func_name, policy_constants_array)
        self.allow_filters: Set(Tuple(str, List)) = set(allow_filters)

