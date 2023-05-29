import Calls

module Boto3 {
  Call get_boto3_resources(string resource_name) {
    exists(
      PythonFunctionValue method, Call call, Module mod, Function main, Variable client,
      Variable resource, Call resource_calls, Call client_calls
    |
      //   exists(mod.getFile().getRelativePath()) and
      //   not mod.getFile() instanceof GeneratedFile and
      method.getName() in ["client", "resource"] and
      method.getScope().getScope*().(Module).getPackageName() = "boto3" and
      main.getName() = "lambda_handler" and
      main.getLocation().getFile() = mod.getFile() and
      (
        Calls::has_second_level_call(method, main) = call or
        Calls::has_first_level_call(method, main) = call or
        Calls::has_zero_level_call(method, main) = call
      ) and
      call.getParentNode().(AssignStmt).getATarget().defines(client) and
      (
        if client.getALoad().getParentNode*() instanceof AssignStmt
        then client.getALoad().getParentNode*().(AssignStmt).getATarget().defines(resource)
        else resource = client
      ) and
      resource.getALoad().getParentNode*().(Call) = resource_calls and
      client.getALoad().getParentNode*().(Call) = client_calls and
      result = resource_calls and
      resource_name = client_calls.getAnArg().getAFlowNode().getNode().(StrConst).getS() + ":BOTO3"
    )
  }
}
