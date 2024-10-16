import python
import semmle.python.dataflow.new.DataFlow
import modules.Concepts.Image
import modules.Concepts.S3Bucket
import modules.Concepts.DynamoDB
import modules.Concepts.FireStore
import modules.Concepts.File
import modules.Growlithe.Sources
import modules.Growlithe.Sinks
import modules.Growlithe.Core
import semmle.python.ApiGraphs

module AdditionalTaints {
  abstract class AdditionalTaintStep extends Unit {
    string toString() { result = "AdditionalTaintStep" }

    abstract predicate step(DataFlow::Node nodeFrom, DataFlow::Node nodeTo);
  }

  class ImageTransformAdditionalTaintStep extends AdditionalTaintStep {
    override predicate step(DataFlow::Node nodeFrom, DataFlow::Node nodeTo) {
      exists(Image::ImageTransform imgTransform |
        nodeFrom = imgTransform.getObject() and
        nodeTo = imgTransform
      )
    }
  }

  class LambdaPayloadToLambdaInvoke extends AdditionalTaintStep {
    override predicate step(DataFlow::Node nodeFrom, DataFlow::Node nodeTo) {
      exists(LambdaInvoke::LambdaInvoke lambdaInvoke |
        nodeFrom = lambdaInvoke.getPayload() and
        nodeTo = lambdaInvoke
      )
    }
  }

  class DynamoDBKeyToCall extends AdditionalTaintStep {
    override predicate step(DataFlow::Node nodeFrom, DataFlow::Node nodeTo) {
      exists(DynamoDBTable::DynamoDBTableUpdateItem dynamoDBUpdate |
        nodeFrom = dynamoDBUpdate.getKey() and
        nodeTo = dynamoDBUpdate
      )
      or
      exists(DynamoDBTable::DynamoDBTableGetItem dynamoDBGet |
        nodeFrom = dynamoDBGet.getKey() and
        nodeTo = dynamoDBGet
      )
      or
      exists(DynamoDBTable::DynamoDBTableDelete dynamoDBDelete |
        nodeFrom = dynamoDBDelete.getKey() and
        nodeTo = dynamoDBDelete
      )
    }
  }

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

  class FirestoreDBKeyToCallStep extends AdditionalTaintStep {
    override predicate step(DataFlow::Node nodeFrom, DataFlow::Node nodeTo) {
      exists(FirestoreDB::FirestoreDocumentReference docRef |
        nodeFrom = docRef.getDocumentId() and
        nodeTo = docRef
      )
    }
  }

  class FirestoreQueryToStreamStep extends AdditionalTaintStep {
    override predicate step(DataFlow::Node nodeFrom, DataFlow::Node nodeTo) {
      exists(FirestoreDB::FirestoreStream stream |
        nodeFrom = stream.getQuery() and
        stream = nodeTo
      )
    }
  }

  // Propagate taint labels from list element to the list
  class ListElementToList extends AdditionalTaintStep {
    override predicate step(DataFlow::Node nodeFrom, DataFlow::Node nodeTo) {
      exists(List list |
        nodeFrom.asCfgNode() = list.getAnElt().getAFlowNode() and
        nodeTo.asCfgNode() = list.getAFlowNode()
      )
    }
  }
  // class FirestoreDBDocumentToCall extends AdditionalTaintStep {
  //   override predicate step(DataFlow::Node nodeFrom, DataFlow::Node nodeTo) {
  //     exists(Image::ImageTransform imgTransform |
  //       nodeFrom = imgTransform.getObject() and
  //       nodeTo = imgTransform
  //     )
  //   }
  // }
  class FunctionArgToFunctionReturnStep extends AdditionalTaintStep {
    override predicate step(DataFlow::Node nodeFrom, DataFlow::Node nodeTo) {
      exists(DataFlow::CallCfgNode callNode |
        nodeFrom = callNode.getArg(_) and
        nodeTo = callNode
      )
    }
  }

  class MethodArgToMethodReturnStep extends AdditionalTaintStep {
    override predicate step(DataFlow::Node nodeFrom, DataFlow::Node nodeTo) {
      exists(DataFlow::MethodCallNode callNode, int argIndex |
        nodeFrom = callNode.getArg(argIndex) and
        nodeTo = callNode.getACall()
      )
    }
  }

  class ObjectToMethodCall extends AdditionalTaintStep {
    override predicate step(DataFlow::Node nodeFrom, DataFlow::Node nodeTo) {
      exists(DataFlow::MethodCallNode callNode |
        nodeFrom = callNode.getObject().getALocalSource() and
        nodeTo = callNode
      )
    }
  }

  class DictToDictSubscript extends AdditionalTaintStep {
    override predicate step(DataFlow::Node nodeFrom, DataFlow::Node nodeTo) {
      exists(SubscriptNode subscript |
        subscript.getObject() = nodeFrom.asCfgNode() and
        nodeTo.asCfgNode() = subscript
      )
    }
  }

  class S3BucketOperationAdditionalTaintStep extends AdditionalTaintStep {
    override predicate step(DataFlow::Node nodeFrom, DataFlow::Node nodeTo) {
      nodeFrom = any(Core::Source s) and
      nodeTo = any(Core::Sink s) and
      nodeFrom = nodeTo
    }
  }

  // class FirestoreQueryToStreamStep extends AdditionalTaintStep {
  //   override predicate step(DataFlow::Node nodeFrom, DataFlow::Node nodeTo) {
  //     exists(FirestoreDB::FirestoreQuery query |
  //       nodeFrom = query and
  //       query.getAPIMemberReturn().getMember("stream").getACall() = nodeTo
  //     )
  //   }
  // }
  class StreamMethodTaintStep extends AdditionalTaintStep {
    override predicate step(DataFlow::Node nodeFrom, DataFlow::Node nodeTo) {
      exists(DataFlow::MethodCallNode call |
        call.getMethodName() = "stream" and
        nodeFrom = call.getObject() and
        nodeTo = call
      )
    }
  }

  class ToDictMethodTaintStep extends AdditionalTaintStep {
    override predicate step(DataFlow::Node nodeFrom, DataFlow::Node nodeTo) {
      exists(DataFlow::MethodCallNode call |
        call.getMethodName() = "to_dict" and
        nodeFrom = call.getObject() and
        nodeTo = call
      )
    }
  }

  class AppendMethodTaintStep extends AdditionalTaintStep {
    override predicate step(DataFlow::Node nodeFrom, DataFlow::Node nodeTo) {
      exists(DataFlow::MethodCallNode call |
        call.getMethodName() = "append" and
        nodeFrom = call.getArg(0) and
        nodeTo = call.getObject()
      )
    }
  }

  // class JSONDumpAdditionalTaintStep extends AdditionalTaintStep {
  //   override predicate step(DataFlow::Node nodeFrom, DataFlow::Node nodeTo) {
  //     exists(API::Node jsonDumps |
  //       jsonDumps = API::moduleImport("json").getMember("dumps") and
  //       nodeTo = jsonDumps.getACall() and
  //       nodeFrom = jsonDumps.getACall().getArg(0)
  //     )
  //   }
  // }
  // Moved out of taint analysis and concatenating with the taint analysis in dataflow.ql
  // class FileReadAfterWrite extends AdditionalTaintStep {
  //   override predicate step(DataFlow::Node nodeFrom, DataFlow::Node nodeTo) {
  //     exists(File::LocalFile read, File::LocalFile write |
  //       nodeTo = read and
  //       nodeFrom = write and
  //       read.localFileOperation() = "READ" and
  //       write.localFileOperation() = "WRITE" and
  //       read.getFilePath() = write.getFilePath() and
  //       write.asCfgNode().dominates(read.asCfgNode())
  //     )
  //   }
  // }

  class ObjectToAttributeTaintStep extends AdditionalTaintStep {
    override predicate step(DataFlow::Node nodeFrom, DataFlow::Node nodeTo) {
      exists(DataFlow::AttrRead attr |
        attr.getObject() = nodeFrom and
        nodeTo = attr
      )
    }
  }
}
