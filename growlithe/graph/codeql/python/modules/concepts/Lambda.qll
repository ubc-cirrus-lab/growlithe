import python
import semmle.python.dataflow.new.DataFlow
import semmle.python.ApiGraphs
import modules.growlithe_dfa.Core
import modules.growlithe_dfa.Utils
import modules.concepts.File

module LambdaInvoke {
  class LambdaInvoke extends DataFlow::CallCfgNode {
    API::Node apiNode;

    LambdaInvoke() {
      apiNode = API::moduleImport("boto3").getMember("client").getReturn().getMember("invoke") and
      this = apiNode.getACall()
    }

    API::Node getAPIMemberReturn() { result = apiNode.getReturn() }

    DataFlow::Node getFunctionName() {
      result in [this.getArg(0), this.getArgByName("FunctionName")]
    }

    DataFlow::Node getPayload() { result in [this.getArg(2), this.getArgByName("Payload")] }

    string getFunctionNameAsResource() {
      result = "LAMBDA_INVOKE:" + Utils::strRepr(getFunctionName())
    }

    override string toString() { result = getFunctionNameAsResource() }
  }
}
