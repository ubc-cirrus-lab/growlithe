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
    then msg = "file is opened for write $@"
    else msg = "file is opened for read $@"
  else msg = "file is opened for read $@"
select call, msg, call.getLocation(), "here"
