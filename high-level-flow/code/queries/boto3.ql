/**
 * @kind problem
 * @id py/boto3
 */

import python
import semmle.python.filters.GeneratedCode

from PythonFunctionValue method, Call call, Module m
where
  exists(m.getFile().getRelativePath()) and 
  not m.getFile() instanceof GeneratedFile and
  method.getName() in ["client", "resource"] and
  method.getACall().getNode() = call and
  (method.getScope().getScope().(Module).getPackageName() = "boto3" or
  method.getScope().getScope().getScope().(Module).getPackageName() = "boto3") and
  call.getLocation().getFile() = m.getFile()
select call.getArg(0), method.getName().toString()
