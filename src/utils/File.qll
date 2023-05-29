import Calls
import semmle.python.ApiGraphs

module File {
  API::CallNode get_file_resources(string resource_name) {
    exists(API::CallNode call, Module mod, Function main |
      main.getName() = "lambda_handler" and
      main.getLocation().getFile() = mod.getFile() and
      (
        Calls::has_second_level_file_call(API::builtin("open"), main) = call or
        Calls::has_first_level_file_call(API::builtin("open"), main) = call or
        Calls::has_zero_level_file_call(API::builtin("open"), main) = call
      ) and
      result = call and resource_name = "TBD:FILE"
    )
  }
}
