import python
import semmle.python.dataflow.new.DataFlow
import modules.Concepts.Image
import modules.Concepts.S3Bucket
import modules.Concepts.File
import modules.Growlithe.Sources
import modules.Growlithe.Sinks
import modules.Growlithe.Core
import semmle.python.ApiGraphs

// module AdditionalMetaTaints {
//   abstract class AdditionalMetaTaintStep extends Unit {
//     string toString() { result = "AdditionalTaintStep" }

//     abstract predicate step(DataFlow::Node nodeFrom, DataFlow::Node nodeTo);
//   }
  
// }
class DynamoDBPayloadToCall extends AdditionalTaintStep {
    override predicate step(DataFlow::Node nodeFrom, DataFlow::Node nodeTo) {
      exists(DynamoDBTable::DynamoDBTableUpdateItem dynamoDBUpdate |
        nodeFrom = dynamoDBUpdate.getUpdateExpression() and
        nodeTo = dynamoDBUpdate
      )
      or
      exists(DynamoDBTable::DynamoDBTablePutItem dynamoDBPut |
        nodeFrom = dynamoDBPut.getItem() and
        nodeTo = dynamoDBPut
      )
    }
  }

  
class DynamoDBTableGetItemSink extends Core::Sink, DynamoDBTable::DynamoDBTableGetItem {
    override Utils::ShareType getShareType() { result = "GLOBAL" }

    override string getObjectPath() { result = Utils::strRepr(super.getKey()) }

    override string getResource() { result = super.getTableNameAsResource() }
  }
