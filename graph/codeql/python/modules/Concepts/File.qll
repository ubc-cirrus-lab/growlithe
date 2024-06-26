import python
import semmle.python.dataflow.new.DataFlow
import semmle.python.ApiGraphs
import modules.Growlithe.Core

module File {
  class LocalFileOperation extends string {
    LocalFileOperation() { this in ["READ", "WRITE"] }
  }

  abstract class LocalFile extends DataFlow::Node {
    abstract DataFlow::Node getFilePath();

    abstract LocalFileOperation localFileOperation();
  }
}
