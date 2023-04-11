import utils.Calls
import utils.Config
import utils.Boto3

module Sinks {
  DataFlow::Node get_sinks(string name) {
    result = get_boto3_sinks(name) and
    Config::restrict_analysis(result)
  }

  DataFlow::Node get_boto3_sinks(string name) {
    exists(Call boto3_calls |
      boto3_calls = Boto3::get_boto3_resources(name) and
      boto3_calls.getAChildNode().(Attribute).getName().matches("%upload%") and
      result.asCfgNode() = boto3_calls.getAnArg().getAFlowNode()
    )
  }
}
