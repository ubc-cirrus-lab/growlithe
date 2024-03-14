import python
import semmle.python.dataflow.new.DataFlow
import modules.Concepts.Image
import modules.Concepts.S3Bucket
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

  class DynamoDBPayloadToCall extends AdditionalTaintStep {
    override predicate step(DataFlow::Node nodeFrom, DataFlow::Node nodeTo) {
      exists(DynamoDBTable::DynamoDBTableUpdateItem dynamoDBUpdate |
        nodeFrom = dynamoDBUpdate.getUpdateExpression() and
        nodeTo = dynamoDBUpdate
      )
    }
  }

  class FunctionArgToFunctionReturnStep extends AdditionalTaintStep {
    override predicate step(DataFlow::Node nodeFrom, DataFlow::Node nodeTo) {
      exists(DataFlow::CallCfgNode callNode, int argIndex |
        nodeFrom = callNode.getArg(argIndex) and
        nodeTo = callNode.getACall()
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
  
  class DictToDictSubscript extends AdditionalTaintStep {
    override predicate step(DataFlow::Node nodeFrom, DataFlow::Node nodeTo) {
      exists(SubscriptNode subscript |
            subscript.getObject() = nodeFrom.asCfgNode() and
            nodeTo.asCfgNode() = subscript)
      }
    }

  class S3BucketOperationAdditionalTaintStep extends AdditionalTaintStep {
    override predicate step(DataFlow::Node nodeFrom, DataFlow::Node nodeTo) {
      nodeFrom = any(Core::Source s) and
      nodeTo = any(Core::Sink s) and
      nodeFrom = nodeTo
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
}
