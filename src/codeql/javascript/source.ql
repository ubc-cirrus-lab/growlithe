import javascript
import DataFlow

from DataFlow::ParameterNode parameter, Function f
where
  f.getFile().getBaseName() = "add.js" and 
  f.getName() = "handler" and
  parameter = f.getAParameter().flow()
select parameter, "Parameter node in " + parameter.getFile()