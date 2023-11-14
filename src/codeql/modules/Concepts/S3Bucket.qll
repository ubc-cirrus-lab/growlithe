import python
import semmle.python.dataflow.new.DataFlow
import semmle.python.ApiGraphs
import modules.Growlithe.Core
import modules.Concepts.File

module S3Bucket {
  class S3Bucket extends DataFlow::CallCfgNode {
    API::Node apiNode;

    S3Bucket() {
      apiNode = API::moduleImport("boto3").getMember("resource").getReturn().getMember("Bucket") and
      this = apiNode.getACall()
    }

    API::Node getAPIMemberReturn() { result = apiNode.getReturn() }

    Expr getBucketExpr() { result = this.getArg(0).getALocalSource().asExpr() }

    override string toString() { result = "S3Bucket" }
  }

  class S3BucketDownload extends DataFlow::CallCfgNode, Core::Node, File::LocalFile {
    S3Bucket bucket;
    API::Node apiNode;

    S3BucketDownload() {
      apiNode = bucket.getAPIMemberReturn().getMember("download_file") and
      this = apiNode.getACall()
    }

    DataFlow::Node getRemotePath() { result in [this.getArg(0), this.getArgByName("Key")] }

    DataFlow::Node getLocalPath() { result in [this.getArg(1), this.getArgByName("Filename")] }

    override Expr getResource() { result = bucket.getBucketExpr() }

    override string getResourceType() { result = "S3_BUCKET" }

    override File::LocalFileOperation localFileOperation() { result = "WRITE" }

    override Expr getFilePathExpr() { result = this.getLocalPath().getALocalSource().asExpr() }
  }

  class S3BucketUpload extends DataFlow::CallCfgNode, Core::Node, File::LocalFile {
    S3Bucket bucket;
    API::Node apiNode;

    S3BucketUpload() {
      apiNode = bucket.getAPIMemberReturn().getMember("upload_file") and
      this = apiNode.getACall()
    }

    DataFlow::Node getRemotePath() { result in [this.getArg(1), this.getArgByName("Key")] }

    DataFlow::Node getLocalPath() { result in [this.getArg(0), this.getArgByName("Filename")] }

    override Expr getResource() { result = bucket.getBucketExpr() }

    override string getResourceType() { result = "S3_BUCKET" }

    override File::LocalFileOperation localFileOperation() { result = "READ" }

    override Expr getFilePathExpr() { result = this.getLocalPath().getALocalSource().asExpr() }
  }
}
