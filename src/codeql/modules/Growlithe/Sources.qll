import python
import modules.Growlithe.Core
import modules.Concepts.S3Bucket
import modules.Concepts.Image

module Sources {
  class ParameterSource extends Core::Source {
    ParameterSource() {
      this instanceof DataFlow::ParameterNode
      // and this.getLocation().getFile().getAbsolutePath().matches("%/test.py")
    }

    // override string toString() { result = "PARAM" }

    override string getGrowlitheOperationType() { result = "PARAM" }

    override Core::ShareType getShareType() { result = "INVOCATION" }

    override Expr getReferenceExpression() { result = this.asExpr() }

    override Expr getResource() { result = this.asExpr() }

    override string getResourceType() { result = "PARAM"}
  }
  class S3BucketDownloadSource extends S3Bucket::S3BucketDownload, Core::Source {
    // override string toString() { result = getGrowlitheOperationType() }
    override string getGrowlitheOperationType() { result = "S3BucketDownloadSource" }

    override Core::ShareType getShareType() { result = "GLOBAL" }

    override Expr getReferenceExpression() { result = this.getRemotePath().asExpr() }
  }

  class S3BucketUploadSource extends S3Bucket::S3BucketUpload, Core::Source {
    // override string toString() { result = getGrowlitheOperationType() }
    override string getGrowlitheOperationType() { result = "S3BucketUploadSource" }

    override Core::ShareType getShareType() { result = "GLOBAL" }

    override Expr getReferenceExpression() { result = this.getLocalPath().asExpr() }
  }

  class ImageOpenSource extends Image::ImageOpen, Core::Source {
    override string toString() { result = getGrowlitheOperationType() }

    override string getGrowlitheOperationType() { result = "ImageOpenSource" }

    override Core::ShareType getShareType() { result = "CONTAINER" }

    override Expr getReferenceExpression() { result = this.getArg(0).asExpr() }
  }
}
