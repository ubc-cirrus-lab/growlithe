import semmle.python.ApiGraphs
import modules.growlithe_dfa.Core
import modules.growlithe_dfa.Utils
import modules.concepts.File

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

    override string toString() { result = "ImageOpen" }

    override File::LocalFileOperation localFileOperation() { result = "READ" }

    override DataFlow::Node getFilePath() { result = this.getArg(0).getALocalSource() }
  }

  class ImageTransformMethod extends string {
    ImageTransformMethod() {
      this in ["rotate", "resize", "crop", "filter", "convert", "save", "transpose"]
    }
  }

  class ImageTransform extends DataFlow::CallCfgNode, Image::Range {
    API::Node apiNode;
    ImageTransformMethod imgTransformMethod;

    ImageTransform() {
      imgTransformMethod = any(ImageTransformMethod m) and
      apiNode = any(Image::Range r).getAPIMemberReturn().getMember(imgTransformMethod) and
      this = apiNode.getACall()
    }

    ImageTransformMethod getImageTransformMethod() { result = imgTransformMethod }

    DataFlow::Node getObject() { result = this.(DataFlow::MethodCallNode).getObject() }

    override API::Node getAPIMemberReturn() { result = apiNode.getReturn() }
  }

  class ImageSave extends DataFlow::CallCfgNode, Core::Node, File::LocalFile {
    API::Node apiNode;

    ImageSave() {
      apiNode = any(Image::Range r).getAPIMemberReturn().getMember("save") and
      this = apiNode.getACall()
    }

    override string toString() { result = "ImageSave" }

    override File::LocalFileOperation localFileOperation() { result = "WRITE" }

    override DataFlow::Node getFilePath() { result = this.getArg(0).getALocalSource() }
  }
}
