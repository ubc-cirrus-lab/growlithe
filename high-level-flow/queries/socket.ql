/**
 * @kind problem
 * @id py/socket
 */

import python
import semmle.python.filters.GeneratedCode


from ClassValue cls, Module m, Call call
where
  exists(m.getFile().getRelativePath()) and 
  not m.getFile() instanceof GeneratedFile and
  cls.getName() = "socket" and
  cls.getACall().getNode() = call and
  call.getLocation().getFile() = m.getFile()
select call, "opening socket at $@", call.getLocation(), "here"
