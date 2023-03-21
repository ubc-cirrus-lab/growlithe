import python
import semmle.python.dataflow.new.DataFlow

module Config {
  string getFunctionName() { result = "lambda_handler" }

  string getAbsolutePath() {
    result = "D:/Code/serverless-compliance/benchmarks/ImageProcessingStateMachine/LambdaFunctions/ImageProcessingFlip/lambda_function.py"
  }

  predicate restrict_analysis(DataFlow::Node node) {
    node.getLocation().getFile().getAbsolutePath() = getAbsolutePath()
  }
}
