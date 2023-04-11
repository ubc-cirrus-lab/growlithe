import utils.Calls
import utils.Config
import utils.Boto3
import utils.File

module Sinks {
  DataFlow::Node get_sinks() {
    (
      result = get_boto3_sinks() or
      result = get_file_sinks()
    ) and
    Config::restrict_analysis(result)
  }

  DataFlow::Node get_boto3_sinks() {
    exists(Call boto3_calls |
      boto3_calls = Boto3::get_boto3_resources() and
      boto3_calls.getAChildNode().(Attribute).getName().matches("%upload%") and
      result.asCfgNode() = boto3_calls.getAnArg().getAFlowNode()
    )
  }

  DataFlow::Node get_file_sinks() {
    exists(API::CallNode call |
      call = File::get_file_resources() and
      call.getNumArgument() >= 2 and
      call.getArg(1).asExpr().(Str).getS().regexpMatch(".*(?:[aw]|r\\+).*") and
      result.asCfgNode() = call.asCfgNode()
    )
  }
}
