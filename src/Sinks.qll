import utils.Calls
import utils.Config

module Sinks {
  DataFlow::Node get_sinks() {
    result = get_boto3_sinks() and
    Config::restrict_analysis(result)
  }

  DataFlow::Node get_boto3_sinks() {
    exists(
      PythonFunctionValue method, Call call, Module m, Function main, Variable v, Variable inter,
      Call intc, Call intv
    |
      exists(m.getFile().getRelativePath()) and
      not m.getFile() instanceof GeneratedFile and
      method.getName() in ["client", "resource"] and
      (
        method.getScope().getScope().(Module).getPackageName() = "boto3" or
        method.getScope().getScope().getScope().(Module).getPackageName() = "boto3"
      ) and
      main.getName() = "lambda_handler" and
      main.getLocation().getFile() = m.getFile() and
      // main.getEnclosingModule().getFile().getAbsolutePath() =
      //   "/Users/arshia/repos/compliance/serverless-compliance/high-level-flow/analysis/tmp/src/LambdaFunctions/ImageProcessingFilter/lambda_function.py" and
      (
        Calls::has_second_level_call(method, main) = call or
        Calls::has_first_level_call(method, main) = call or
        Calls::has_zero_level_call(method, main) = call
      ) and
      call.getParentNode().(AssignStmt).getATarget().defines(v) and
      (
        if v.getALoad().getParentNode*() instanceof AssignStmt
        then v.getALoad().getParentNode*().(AssignStmt).getATarget().defines(inter)
        else inter = v
      ) and
      inter.getALoad().getParentNode*().(Call) = intc and
      v.getALoad().getParentNode*().(Call) = intv and
      result.asCfgNode() = intc.getAnArg().getAFlowNode()
    )
  }
}
