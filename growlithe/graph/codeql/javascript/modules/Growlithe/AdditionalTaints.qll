import javascript
import DataFlow
import modules.Concepts.DynamoDB
import modules.Growlithe.Core
import queries.Config

module AdditionalTaints {
  // class PropRefTaintStep extends Core::AdditionalTaintStep {
  //   override predicate step(DataFlow::Node nodeFrom, DataFlow::Node nodeTo) {
  //     exists (DataFlow::PropRef ref |
  //       ref.getBase() = nodeFrom and
  //       ref = nodeTo
  //     )
  //   }
  // }

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
