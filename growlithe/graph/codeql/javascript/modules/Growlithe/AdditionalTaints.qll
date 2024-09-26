import javascript
import DataFlow
import modules.Concepts.DynamoDB
import modules.Concepts.FirestoreDB
import modules.Growlithe.Core
import queries.Config

module AdditionalTaints {
  class MethodArgToMethodCall extends Core::AdditionalTaintStep {
    override predicate step(DataFlow::Node nodeFrom, DataFlow::Node nodeTo) {
      exists(DataFlow::MethodCallNode methodCall |
        methodCall.getAnArgument() = nodeFrom and
        methodCall = nodeTo
        and Config::constrainLocation2(nodeFrom)
        and Config::constrainLocation2(nodeTo)
      )
    }
  }

  class FirestoreIncrementKeyToVal extends Core::AdditionalTaintStep {
    override predicate step(DataFlow::Node nodeFrom, DataFlow::Node nodeTo) {
      exists(Firestore::FirestoreFieldValue fieldVal |
        nodeFrom = fieldVal.getIncrementKey() and
        nodeTo = fieldVal
      )
    }
  }

  class ObjectPropToObject extends Core::AdditionalTaintStep {
    override predicate step(DataFlow::Node nodeFrom, DataFlow::Node nodeTo) {
      exists(DataFlow::ObjectLiteralNode objNode | 
        objNode.getAPropertySource() = nodeFrom and
        objNode = nodeTo
        and Config::constrainLocation2(nodeFrom)
        and Config::constrainLocation2(nodeTo)
      )
    }
  }

  class DynamoDBPayloadToCall extends Core::AdditionalTaintStep {
    override predicate step(DataFlow::Node nodeFrom, DataFlow::Node nodeTo) {
      exists(DynamoDB::DynamoDBTableUpdateItem dynamoDBUpdate |
        nodeFrom = dynamoDBUpdate.getUpdateExpression() and
        nodeTo = dynamoDBUpdate
      )
    }
    override string toString() { result = "DynamoDBPayloadToCall" }
  }
}
