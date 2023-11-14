import python
import modules.Growlithe.Core
import modules.Concepts.S3Bucket
import modules.Concepts.Image

module Sinks {
  class ReturnExpression extends Core::Sink {
    ReturnExpression() {
      exists(Return ret | this.asCfgNode() = ret.getASubExpression().getAFlowNode())
    }

    override Utils::ShareType getShareType() { result = "INVOCATION" }

    override string getObjectPath() { result = Utils::strRepr(this) }

    override string getResource() { result = "RETURN" }
  }

  class S3BucketDownloadSink extends S3Bucket::S3BucketDownload, Core::Sink {
    override Utils::ShareType getShareType() { result = "CONTAINER" }

    override string getObjectPath() { result = Utils::strRepr(this.getLocalPath()) }

    override string getResource() { result = Utils::localFileResource() }
  }

  class S3BucketUploadSink extends S3Bucket::S3BucketUpload, Core::Sink {
    override Utils::ShareType getShareType() { result = "GLOBAL" }

    override string getObjectPath() { result = Utils::strRepr(this.getRemotePath()) }
  }

  class ImageSaveSink extends Image::ImageSave, Core::Sink {
    override Utils::ShareType getShareType() { result = "CONTAINER" }

    override string getObjectPath() { result = Utils::strRepr(this.getArg(0)) }
  }
}
