import javascript
import DataFlow

module Config {
  string getFileEndingPattern() {
    result = []
  }

  string getFunctionName() { result = "handler" }

  predicate constrainLocation2(DataFlow::Node node) {
    node.getLocation().getFile().getAbsolutePath().matches("%" + getFileEndingPattern())
    // and node.getScope().getName() = getFunctionName()
  }

  predicate constrainLocation(Location loc) {
    loc.getFile().getAbsolutePath().matches("%" + getFileEndingPattern())
  }
}
