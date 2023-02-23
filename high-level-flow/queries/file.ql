/**
 * @kind problem
 * @id py/file
 */

import python
import semmle.python.filters.GeneratedCode
import semmle.python.ApiGraphs

from Module m, API::CallNode call
where 
  exists(m.getFile().getRelativePath()) and 
  not m.getFile() instanceof GeneratedFile and
  API::builtin("open").getACall() = call and 
  call.getLocation().getFile() = m.getFile()
select call, "file is opened at $@", call.getLocation(), "here"
