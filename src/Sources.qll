import utils.Calls
import utils.Config

module Sources {
  DataFlow::Node get_sources() {
    result = get_parameter_sources() and
    Config::restrict_analysis(result)
  }

  DataFlow::Node get_parameter_sources() { result instanceof DataFlow::ParameterNode }
}
