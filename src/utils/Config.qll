import python
import semmle.python.dataflow.new.DataFlow

module Config {
  string getFunctionName() { result = "lambda_handler" }

  string getRelativePath() { result = "LambdaFunctions/ImageProcessingFlip/lambda_function.py" }

  predicate restrict_analysis(DataFlow::Node node) {
    node.getLocation().getFile().getRelativePath() = getRelativePath()
  }
}
