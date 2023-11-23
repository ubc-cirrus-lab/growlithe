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

    override string getResource() { result = "RETURN:STATIC:SourceCode" }
  }

  class S3BucketDownloadSink extends Core::Sink, S3Bucket::S3BucketDownload {
    override Utils::ShareType getShareType() { result = "CONTAINER" }

    override string getObjectPath() { result = Utils::strRepr(super.getLocalPath()) }

    override string getResource() { result = Utils::localFileResource() }
  }

  class S3BucketUploadSink extends Core::Sink, S3Bucket::S3BucketUpload {
    override Utils::ShareType getShareType() { result = "GLOBAL" }

    override string getObjectPath() { result = Utils::strRepr(super.getRemotePath()) }

    override string getResource() { result = super.getBucketNameAsResource() }
  }

  class ImageSaveSink extends Core::Sink, Image::ImageSave {
    override Utils::ShareType getShareType() { result = "CONTAINER" }

    override string getObjectPath() { result = Utils::strRepr(super.getArg(0)) }

    override string getResource() { result = Utils::localFileResource() }
  }
}