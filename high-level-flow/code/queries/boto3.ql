/**
 * @kind problem
 * @id py/boto3-ID
 */

 import python
 import semmle.python.filters.GeneratedCode
 
 
 Call has_zero_level_call(PythonFunctionValue target, Function main) {
   target.getACall().getNode() = result and
   result.getScope() = main.getScope()
 }
 
 Call has_first_level_call(PythonFunctionValue target, Function main) {
   target.getACall().getNode() = result and
   result.getScope() = main
 }
 
 Call has_second_level_call(PythonFunctionValue target, Function main) {
   exists(PythonFunctionValue f, Call icall |
       target.getACall().getNode() = result and
       result.getScope() = f.getScope() and 
       f.getACall().getNode() = icall and
       icall.getScope() = main
   )
 }
 
 from PythonFunctionValue method, Call call, Module m, Function main, Variable v, Variable inter, Call intc, Call intv
 where
   exists(m.getFile().getRelativePath()) and 
   not m.getFile() instanceof GeneratedFile and
   method.getName() in ["client", "resource"] and
   (method.getScope().getScope().(Module).getPackageName() = "boto3" or
   method.getScope().getScope().getScope().(Module).getPackageName() = "boto3") and
   main.getName() = "FUNCTION_NAME" and
   main.getLocation().getFile() = m.getFile() and
   main.getEnclosingModule().getFile().getAbsolutePath() = "SCRIPT_PATH" and
   (has_second_level_call(method, main) = call or
   has_first_level_call(method, main) = call or
   has_zero_level_call(method, main) = call) and
   call.getParentNode().(AssignStmt).getATarget().defines(v) and
   if v.getALoad().getParentNode*() instanceof AssignStmt
   then (v.getALoad().getParentNode*().(AssignStmt).getATarget().defines(inter))
   else inter = v and
   inter.getALoad().getParentNode*().(Call) = intc and
   v.getALoad().getParentNode*().(Call) = intv
 select call.getArg(0), method.getName().toString() + " uses: $@ action: $@", intv.getAnArg(), intv.getFunc().(Attribute).getAttr(), intc.getAnArg(), intc.getFunc().(Attribute).getAttr()
 