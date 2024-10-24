import javascript
import DataFlow

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
    // result = expNode.asExpr().toString()
    exists(ConstantString strConst |
      strConst = expNode.getALocalSource().asExpr() and
      result = staticExprType() + ":" + strConst
    )
    or
    (
    not exists(ConstantString strConst |
      strConst = expNode.getALocalSource().asExpr()) and
    result = dynamicExprType() + ":" + expNode.asExpr().toString())
  }

  string localFileResource() { result = "LOCAL_FILE:STATIC:tempfs" }

  DataFlow::Node getObjectProperty(DataFlow::Node node, string propertyName) {
    result = node.(DataFlow::ObjectLiteralNode).getAPropertySource(propertyName)
  }
}
