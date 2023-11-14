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

    override string getResource() { result = "PARAM" }
  }

  class S3BucketDownloadSource extends S3Bucket::S3BucketDownload, Core::Source {
    override Utils::ShareType getShareType() { result = "GLOBAL" }

    override string getObjectPath() { result = Utils::strRepr(this.getRemotePath()) }
  }

  class S3BucketUploadSource extends S3Bucket::S3BucketUpload, Core::Source {
    override Utils::ShareType getShareType() { result = "CONTAINER" }

    override string getObjectPath() { result = Utils::strRepr(this.getLocalPath()) }
    override string getResource() { result = Utils::localFileResource() }
  }

  class ImageOpenSource extends Image::ImageOpen, Core::Source {
    override Utils::ShareType getShareType() { result = "CONTAINER" }

    override string getObjectPath() { result = Utils::strRepr(this.getArg(0)) }
  }
}
