import python
import semmle.python.dataflow.new.DataFlow

module Core {
  class ShareType extends string {
    ShareType() { this in ["GLOBAL", "CONTAINER", "INVOCATION"] }
  }

  abstract class Node extends DataFlow::Node {
    abstract Expr getResource();

    abstract string getResourceType();
  }

  abstract class Source extends Core::Node {
    abstract Expr getReferenceExpression();

    abstract ShareType getShareType();

    abstract string getGrowlitheOperationType();
  }

  abstract class Sink extends Core::Node {
    abstract Expr getReferenceExpression();

    abstract ShareType getShareType();

    abstract string getGrowlitheOperationType();
  }
}
