/**
 * @kind problem
 * @id py/file
 */

import python
import semmle.python.filters.GeneratedCode
import semmle.python.ApiGraphs


API::CallNode has_zero_level_call(API::Node target, Function main) {
  target.getACall() = result and
  result.getScope() = main.getScope()
}

API::CallNode has_first_level_call(API::Node target, Function main) {
  target.getACall() = result and
  result.getScope() = main
}

API::CallNode has_second_level_call(API::Node target, Function main) {
  exists(PythonFunctionValue f, Call icall |
      target.getACall() = result and
      result.getScope() = f.getScope() and 
      f.getACall().getNode() = icall and
      icall.getScope() = main
  )
}

from Module m, API::CallNode call, string msg, Function main
where 
  exists(m.getFile().getRelativePath()) and 
  not m.getFile() instanceof GeneratedFile and
  API::builtin("open").getACall() = call and 
  call.getLocation().getFile() = m.getFile() and
  main.getName() = "main" and
  main.getLocation().getFile() = m.getFile() and
  (has_second_level_call(API::builtin("open"), main) = call or
  has_first_level_call(API::builtin("open"), main) = call or
  has_zero_level_call(API::builtin("open"), main) = call) and 
  if call.getNumArgument() >= 2 then
    if call.getArg(1).asExpr().(Str).getS().regexpMatch(".*(?:[aw]|r\\+).*")
    then msg = "write"
    else msg = "read"
  else msg = "read"
select call.getArg(0), msg
