/**
 * @kind problem
 * @id py/requests
 */

import python
import semmle.python.filters.GeneratedCode

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

from Call call, PythonFunctionValue method, Module m, Function main
where
  exists(m.getFile().getRelativePath()) and 
  not m.getFile() instanceof GeneratedFile and
  method.getQualifiedName() in ["get", "post", "put", "urlopen"] and
  method.getScope().getScope().(Module).getPackage().getName() in ["requests", "urllib"] and
  call.getLocation().getFile() = m.getFile() and
  main.getName() = "main" and
  main.getLocation().getFile() = m.getFile() and
  (has_second_level_call(method, main) = call or
  has_first_level_call(method, main) = call)
select call.getArg(0), method.getName()
