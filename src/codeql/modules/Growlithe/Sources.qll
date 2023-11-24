import python
import modules.Growlithe.Core
import modules.Growlithe.Utils
import modules.Concepts.S3Bucket
import modules.Concepts.Image

module Sources {
  class ParameterSource extends Core::Source {
    ParameterSource() { this instanceof DataFlow::ParameterNode }

    override string getObjectPath() { result = Utils::strRepr(this) }

    override Utils::ShareType getShareType() { result = "INVOCATION" }

    override string getResource() { result = "PARAM:STATIC:SourceCode" }
  }

  class S3BucketDownloadSource extends Core::Source, S3Bucket::S3BucketDownload {
    override Utils::ShareType getShareType() { result = "GLOBAL" }

    override string getObjectPath() { result = Utils::strRepr(super.getRemotePath()) }

    override string getResource() { result = super.getBucketNameAsResource() }
  }

  class S3BucketUploadSource extends Core::Source, S3Bucket::S3BucketUpload {
    override Utils::ShareType getShareType() { result = "CONTAINER" }

    override string getObjectPath() { result = Utils::strRepr(super.getLocalPath()) }

    override string getResource() { result = Utils::localFileResource() }
  }

  class ImageOpenSource extends Core::Source, Image::ImageOpen {
    override Utils::ShareType getShareType() { result = "CONTAINER" }

    override string getObjectPath() { result = Utils::strRepr(super.getArg(0)) }

    override string getResource() { result = Utils::localFileResource() }
  }
}
