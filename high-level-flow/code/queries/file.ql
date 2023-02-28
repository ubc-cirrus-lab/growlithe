/**
 * @kind problem
 * @id py/file
 */

import python
import semmle.python.filters.GeneratedCode
import semmle.python.ApiGraphs

from Module m, API::CallNode call, string msg
where 
  exists(m.getFile().getRelativePath()) and 
  not m.getFile() instanceof GeneratedFile and
  API::builtin("open").getACall() = call and 
  call.getLocation().getFile() = m.getFile() and
  if call.getNumArgument() >= 2 then
    if call.getArg(1).asExpr().(Str).getS().regexpMatch(".*(?:[aw]|r\\+).*")
    then msg = "write"
    else msg = "read"
  else msg = "read"
select call.getArg(0), msg
