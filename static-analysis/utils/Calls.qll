import python
import semmle.python.filters.GeneratedCode
import semmle.python.dataflow.new.DataFlow
import semmle.python.ApiGraphs

module Calls {
  Call has_zero_level_call(PythonFunctionValue target, Function main) {
    target.getACall().getNode() = result and
    result.getScope() = main.getScope()
  }

  API::CallNode has_zero_level_file_call(API::Node target, Function main) {
    target.getACall() = result and
    result.getScope() = main.getScope()
  }
  
  API::CallNode has_first_level_file_call(API::Node target, Function main) {
    target.getACall() = result and
    result.getScope() = main
  }
  
  API::CallNode has_second_level_file_call(API::Node target, Function main) {
    exists(PythonFunctionValue f, Call icall |
        target.getACall() = result and
        result.getScope() = f.getScope() and 
        f.getACall().getNode() = icall and
        icall.getScope() = main
    )
  }

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
}
