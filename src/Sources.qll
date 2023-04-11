import utils.Calls
import utils.Config
import utils.Boto3

module Sources {
  DataFlow::Node get_sources(string name) {
    (
      result = get_parameter_sources(name)
      or result = get_boto3_sources(name)
    ) and
    Config::restrict_analysis(result)
  }

  DataFlow::Node get_parameter_sources(string name) { result instanceof DataFlow::ParameterNode
    and name =  result.(DataFlow::ParameterNode).getParameter().getName()
  }

  DataFlow::Node get_boto3_sources(string name) {
    exists(Call boto3_calls |
      boto3_calls = Boto3::get_boto3_resources(name) and
      boto3_calls.getAChildNode().(Attribute).getName().matches("%download%") and
      result.asCfgNode() = boto3_calls.getAnArg().getAFlowNode()
    )
  }
}
