import python
import semmle.python.dataflow.new.DataFlow
import modules.Concepts.Image
import modules.Concepts.S3Bucket
import modules.Concepts.File
import modules.Growlithe.Sources
import modules.Growlithe.Sinks
import modules.Growlithe.Core

module AdditionalTaints {
  abstract class AdditionalTaintStep extends Unit {
    override string toString() { result = "AdditionalTaintStep" }

    abstract predicate step(DataFlow::Node nodeFrom, DataFlow::Node nodeTo);
  }

  class ImageTransformAdditionalTaintStep extends AdditionalTaintStep {
    override predicate step(DataFlow::Node nodeFrom, DataFlow::Node nodeTo) {
      exists(Image::ImageTransform imgTransform |
        // nodeFrom = img and
        nodeFrom = imgTransform.getObject() and
        nodeTo = imgTransform
      )
    }
  }

  class S3BucketDownloadAdditionalTaintStep extends AdditionalTaintStep {
    override predicate step(DataFlow::Node nodeFrom, DataFlow::Node nodeTo) {
      nodeFrom = any(Core::Source s) and
      nodeTo = any(Core::Sink s) and
      nodeFrom = nodeTo
    }
  }

  class FileReadAfterWrite extends AdditionalTaintStep {
    override predicate step(DataFlow::Node nodeFrom, DataFlow::Node nodeTo) {
      exists(File::LocalFile read, File::LocalFile write |
        nodeTo = read and
        nodeFrom = write and
        read.localFileOperation() = "READ" and
        write.localFileOperation() = "WRITE" and
        read.getFilePath() = write.getFilePath()
      )
    }
  }
}
