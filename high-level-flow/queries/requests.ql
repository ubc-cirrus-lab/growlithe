/**
 * @kind problem
 * @id py/requests
 */

import python
import semmle.python.filters.GeneratedCode

from Call call, PythonFunctionValue method, Module m
where
  exists(m.getFile().getRelativePath()) and 
  not m.getFile() instanceof GeneratedFile and
  method.getQualifiedName() in ["get", "post", "put", "urlopen"] and
  method.getACall().getNode() = call and
  method.getScope().getScope().(Module).getPackage().getName() in ["requests", "urllib"] and
  call.getLocation().getFile() = m.getFile()
select call, "calling method $@", method, method.getName()
