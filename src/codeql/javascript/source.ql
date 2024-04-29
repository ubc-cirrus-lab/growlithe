import javascript
import DataFlow

from DataFlow::ParameterNode parameter, Function f
where
  f.getFile().getBaseName() = "add_to_cart.js" and
  f.getName() = "handler" and
  parameter = f.getAParameter().flow()
select parameter, "Parameter node in " + parameter.getFile()