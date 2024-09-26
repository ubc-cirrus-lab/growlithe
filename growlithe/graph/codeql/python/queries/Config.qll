import python
import semmle.python.dataflow.new.DataFlow

module Config {
  string getFileEndingPattern() {
    result = ["backend/checkout_cart/main.py"]
  }

  string getFunctionName() { result = "lambda_handler" }

  predicate constrainLocation2(DataFlow::Node node) {
    node.getLocation().getFile().getAbsolutePath().matches("%" + getFileEndingPattern())
    // and node.getScope().getName() = getFunctionName()
  }

  predicate constrainLocation(Location loc) {
    loc.getFile().getAbsolutePath().matches("%" + getFileEndingPattern())
  }
}
