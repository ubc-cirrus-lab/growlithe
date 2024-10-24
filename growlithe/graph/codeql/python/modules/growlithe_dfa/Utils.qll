import python
import semmle.python.dataflow.new.DataFlow

module Utils {
  class ShareType extends string {
    ShareType() { this in ["GLOBAL", "CONTAINER", "INVOCATION"] }
  }

  class ExprType extends string {
    ExprType() { this in ["STATIC", "DYNAMIC"] }
  }

  ExprType staticExprType() { result = "STATIC" }

  ExprType dynamicExprType() { result = "DYNAMIC" }

  class InterfaceType extends string {
    InterfaceType() { this in ["SOURCE", "SINK"] }
  }

  string strRepr(DataFlow::Node expNode) {
    exists(string strConst |
      strConst = expNode.getALocalSource().asExpr().(Str).getS() and
      result = staticExprType() + ":" + strConst
    )
    or
    not exists(string strConst | strConst = expNode.getALocalSource().asExpr().(Str).getS()) and
    result = dynamicExprType() + ":" + expNode.asExpr().toString()
  }

  string localFileResource() { result = "LOCAL_FILE:STATIC:tempfs" }
}
