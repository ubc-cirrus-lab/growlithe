import utils.Calls
import utils.Config
import utils.Boto3

module Sources {
  DataFlow::Node get_sources() {
    (
      result = get_parameter_sources() or
      result = get_boto3_sources()
    ) and
    Config::restrict_analysis(result)
  }

  DataFlow::Node get_parameter_sources() { result instanceof DataFlow::ParameterNode }

  DataFlow::Node get_boto3_sources() {
    exists(Call boto3_calls |
      boto3_calls = Boto3::get_boto3_resources() and
      boto3_calls.getAChildNode().(Attribute).getName().matches("%download%") and
      result.asCfgNode() = boto3_calls.getAnArg().getAFlowNode()
    )
  }
}
