import python
import semmle.python.dataflow.new.DataFlow

module Config {
  string getFileEndingPattern() {
    result = ["src/tag_store_image/app.py",
		"src/blur_image/app.py",
		"src/filter_image/app.py",
		"src/transform_image/app.py"]
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
