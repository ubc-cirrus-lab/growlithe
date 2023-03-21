import python
import semmle.python.filters.GeneratedCode
import semmle.python.dataflow.new.DataFlow

module Calls {
  Call has_zero_level_call(PythonFunctionValue target, Function main) {
    target.getACall().getNode() = result and
    result.getScope() = main.getScope()
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
