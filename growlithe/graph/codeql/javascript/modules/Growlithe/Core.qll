import javascript
import DataFlow
import modules.Growlithe.Utils

module Core {
  abstract class Node extends DataFlow::Node {
    // Resource string in the form of ResourceType:ExprType:ResourceName. E.g: S3_BUCKET:STATIC:raw_images
    // abstract string getResource();
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
      result = getInterfaceType() + ", " + getShareType() + ", " + getResource() + ", " + getObjectPath()
    }
  }

  abstract class AdditionalTaintStep extends Unit {
    string toString() { result = "AdditionalTaintStep" }

    abstract predicate step(DataFlow::Node nodeFrom, DataFlow::Node nodeTo);
  }
}
