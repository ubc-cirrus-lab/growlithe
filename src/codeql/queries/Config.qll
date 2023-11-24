import python
import semmle.python.dataflow.new.DataFlow

module Config {
  string getFileEndingPattern() {
    result =
      [
        "LambdaFunctions/ImageProcessingFilter/lambda_function.py",
        "LambdaFunctions/ImageProcessingFlip/lambda_function.py",
        "LambdaFunctions/ImageProcessingGetInput/lambda_function.py",
        "LambdaFunctions/ImageProcessingGrayScale/lambda_function.py",
        "LambdaFunctions/ImageProcessingResize/lambda_function.py",
        "LambdaFunctions/ImageProcessingRotate/lambda_function.py"
      ]
  }

  string getFunctionName() { result = "lambda_handler" }

  predicate constrainLocation2(DataFlow::Node node) {
    node.getLocation().getFile().getAbsolutePath().matches("%" + getFileEndingPattern()) and
    node.getScope().getName() = getFunctionName()
  }

  predicate constrainLocation(Location loc) {
    loc.getFile().getAbsolutePath().matches("%" + getFileEndingPattern())
  }
}
