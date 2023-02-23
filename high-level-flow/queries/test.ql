import python
import semmle.python.ApiGraphs
import semmle.python.filters.GeneratedCode


from Module m, API::CallNode call, API::Node n
where 
  exists(m.getFile().getRelativePath()) and 
  not m.getFile() instanceof GeneratedFile and
  API::moduleImport("socket").getMember("socket") = n and
  n.getACall() = call and
  call.getLocation().getFile() = m.getFile()
select n, call
