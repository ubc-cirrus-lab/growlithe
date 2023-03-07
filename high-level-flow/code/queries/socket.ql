/**
 * @kind problem
 * @id py/socket
 */

import python
import semmle.python.filters.GeneratedCode

Call has_zero_level_call(ClassValue target, Function main) {
  target.getACall().getNode() = result and
  result.getScope() = main.getScope()
}

Call has_first_level_call(ClassValue target, Function main) {
  target.getACall().getNode() = result and
  result.getScope() = main
}

Call has_second_level_call(ClassValue target, Function main) {
  exists(PythonFunctionValue f, Call icall |
      target.getACall().getNode() = result and
      result.getScope() = f.getScope() and 
      f.getACall().getNode() = icall and
      icall.getScope() = main
  )
}

from ClassValue cls, Module m, Call call, Function main
where
  exists(m.getFile().getRelativePath()) and 
  not m.getFile() instanceof GeneratedFile and
  cls.getName() = "socket" and
  call.getLocation().getFile() = m.getFile() and
  main.getName() = "main" and
  main.getLocation().getFile() = m.getFile() and
  (has_second_level_call(cls, main) = call or
  has_first_level_call(cls, main) = call or
  has_zero_level_call(cls, main) = call)
select call, "socket"
