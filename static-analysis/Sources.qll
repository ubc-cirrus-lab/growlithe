import utils.Calls
import utils.Config
import utils.Boto3
import utils.File

module Sources {
  DataFlow::Node get_sources(string name) {
    (
      result = get_parameter_sources(name) or
      result = get_boto3_sources(name) or
      result = get_DYNAMODB_TABLE_sources(name) or
      result = get_file_sources(name)
    ) and
    Config::restrict_analysis(result)
  }

  DataFlow::Node get_parameter_sources(string name) { result instanceof DataFlow::ParameterNode
    and name =  result.(DataFlow::ParameterNode).getParameter().getName() + ":PARAMETER"
  }

  DataFlow::Node get_boto3_sources(string name) {
    exists(Call boto3_calls |
      boto3_calls = Boto3::get_boto3_resources(name) and
      boto3_calls.getAChildNode().(Attribute).getName().matches("%download%") and
      result.asCfgNode() = boto3_calls.getAnArg().getAFlowNode()
    )
  }

  DataFlow::Node get_DYNAMODB_TABLE_sources(string name) {
    exists(API::Node api_node |
      api_node = API::moduleImport("boto3").getMember("client").getReturn().getMember("get_item") and
      result = api_node.getReturn().asSource() and
      name = api_node.getKeywordParameter("TableName").getAValueReachingSink().getALocalSource().asExpr().(Str).getS() + ":DYNAMODB_TABLE"
    )
  }

  DataFlow::Node get_file_sources(string name) {
    exists(API::CallNode call |
      call = File::get_file_resources(name) and
      call.getNumArgument() >= 2 and
      not call.getArg(1).asExpr().(Str).getS().regexpMatch(".*(?:[aw]|r\\+).*") and
      result.asCfgNode() = call.asCfgNode()
    )
  }
}
