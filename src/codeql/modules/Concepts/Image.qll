import semmle.python.ApiGraphs
import modules.Growlithe.Core
import modules.Concepts.File

module Image {
  abstract class Range extends DataFlow::Node {
    abstract API::Node getAPIMemberReturn();
  }

  class Image extends DataFlow::Node {
    Image::Range range;

    Image() { this = range }

    API::Node getAPIMemberReturn() { result = range.getAPIMemberReturn() }
  }

  class ImageOpen extends DataFlow::CallCfgNode, Image::Range, Core::Node, File::LocalFile {
    API::Node apiNode;

    ImageOpen() {
      apiNode = API::moduleImport("PIL").getMember("Image").getMember("open") and
      this = apiNode.getACall()
    }

    override API::Node getAPIMemberReturn() { result = apiNode.getReturn() }

    override string toString() { result = "Image" }

    // FIXME: Temp hack, wrong val
    override Expr getResource() { result = this.getArg(0).getALocalSource().asExpr() }

    override string getResourceType() { result = "LOCAL_FILE" }

    override File::LocalFileOperation localFileOperation() { result = "READ" }

    override Expr getFilePathExpr() { result = this.getArg(0).getALocalSource().asExpr() }
  }

  class ImageTranformMethod extends string {
    ImageTranformMethod() { this in ["rotate", "resize", "crop", "filter", "convert", "save"] }
  }

  class ImageTranform extends DataFlow::CallCfgNode, Image::Range {
    API::Node apiNode;
    ImageTranformMethod imgTransformMethod;

    ImageTranform() {
      imgTransformMethod = any(ImageTranformMethod m) and
      apiNode = any(Image::Range r).getAPIMemberReturn().getMember(imgTransformMethod) and
      this = apiNode.getACall()
    }

    ImageTranformMethod getImageTranformMethod() { result = imgTransformMethod }

    DataFlow::Node getObject() { result = this.(DataFlow::MethodCallNode).getObject() }

    override API::Node getAPIMemberReturn() { result = apiNode.getReturn() }
  }

  class ImageSave extends DataFlow::CallCfgNode, Core::Node, File::LocalFile {
    API::Node apiNode;

    ImageSave() {
      apiNode = any(Image::Range r).getAPIMemberReturn().getMember("save") and
      this = apiNode.getACall()
    }

    // FIXME: Temp hack, wrong val
    override Expr getResource() { result = this.getArg(0).getALocalSource().asExpr() }

    override string getResourceType() { result = "LOCAL_FILE" }

    override File::LocalFileOperation localFileOperation() { result = "WRITE" }

    override Expr getFilePathExpr() { result = this.getArg(0).getALocalSource().asExpr() }
  }
}
