import python
import modules.Growlithe.Core
import modules.Concepts.S3Bucket
import modules.Concepts.Image

module Sinks {
  class ReturnExpression extends Core::Sink {
    ReturnExpression() {
      exists(Return ret | this.asCfgNode() = ret.getASubExpression().getAFlowNode())
    }

    // override string toString() { result = "RETURN" }

    override string getGrowlitheOperationType() { result = "RETURN" }

    override Core::ShareType getShareType() { result = "INVOCATION" }

    override Expr getReferenceExpression() { result = this.asExpr() }

    override Expr getResource() { result = this.asExpr() }

    override string getResourceType() { result = "RETURN"}
  }

  class S3BucketDownloadSink extends S3Bucket::S3BucketDownload, Core::Sink {
    // override string toString() { result = getGrowlitheOperationType() }
    override string getGrowlitheOperationType() { result = "S3BucketDownloadSink" }

    override Core::ShareType getShareType() { result = "GLOBAL" }

    override Expr getReferenceExpression() { result = this.getLocalPath().asExpr() }
  }

  class S3BucketUploadSink extends S3Bucket::S3BucketUpload, Core::Sink {
    // override string toString() { result = getGrowlitheOperationType() }
    override string getGrowlitheOperationType() { result = "S3BucketUploadSink" }

    override Core::ShareType getShareType() { result = "GLOBAL" }

    override Expr getReferenceExpression() { result = this.getRemotePath().asExpr() }
  }

  class ImageSaveSink extends Image::ImageSave, Core::Sink {
    override string toString() { result = getGrowlitheOperationType() }

    override string getGrowlitheOperationType() { result = "ImageSaveSink" }

    override Core::ShareType getShareType() { result = "GLOBAL" }

    override Expr getReferenceExpression() { result = this.getArg(0).asExpr() }
  }
}
