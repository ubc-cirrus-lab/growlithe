import python
import semmle.python.dataflow.new.DataFlow
import modules.growlithe_dfa.Utils

module Core {
  abstract class Node extends DataFlow::Node {
    // Resource string in the form of ResourceType:ExprType:ResourceName. E.g: S3_BUCKET:STATIC:raw_images
    // abstract string getResource();
    DataFlow::Node getMetadataSink() { none() }
  }

  abstract class Source extends Core::Node {
    abstract string getResource();

    abstract string getObjectPath();

    abstract Utils::ShareType getShareType();

    Utils::InterfaceType getInterfaceType() { result = "SOURCE" }

    string getFlowState() {
      result =
        getInterfaceType() + ", " + getShareType() + ", " + getResource() + ", " + getObjectPath()
    }
  }

  abstract class Sink extends Core::Node {
    abstract string getResource();

    abstract string getObjectPath();

    abstract Utils::ShareType getShareType();

    Utils::InterfaceType getInterfaceType() { result = "SINK" }

    string getFlowState() {
      result =
        getInterfaceType() + ", " + getShareType() + ", " + getResource() + ", " + getObjectPath()
    }
  }
}
