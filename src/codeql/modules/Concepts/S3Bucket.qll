import python
import semmle.python.dataflow.new.DataFlow
import semmle.python.ApiGraphs
import modules.Growlithe.Core
import modules.Growlithe.Utils
import modules.Concepts.File

module S3Bucket {
  class S3Bucket extends DataFlow::CallCfgNode {
    API::Node apiNode;

    S3Bucket() {
      apiNode = API::moduleImport("boto3").getMember("resource").getReturn().getMember("Bucket") and
      this = apiNode.getACall()
    }

    API::Node getAPIMemberReturn() { result = apiNode.getReturn() }

    DataFlow::Node getBucketName() { result = this.getArg(0).getALocalSource() }

    string getBucketNameAsResource() { result = "S3_BUCKET:" + Utils::strRepr(getBucketName()) }

    override string toString() { result = getBucketNameAsResource() }
  }

  class S3BucketDownload extends DataFlow::CallCfgNode, File::LocalFile {
    S3Bucket bucket;
    API::Node apiNode;

    S3BucketDownload() {
      bucket = any(S3Bucket b) and
      apiNode = bucket.getAPIMemberReturn().getMember("download_file") and
      this = apiNode.getACall()
    }

    S3Bucket getBucket() { result = bucket }

    DataFlow::Node getRemotePath() { result in [this.getArg(0), this.getArgByName("Key")] }

    DataFlow::Node getLocalPath() { result in [this.getArg(1), this.getArgByName("Filename")] }

    override File::LocalFileOperation localFileOperation() { result = "WRITE" }

    override DataFlow::Node getFilePath() { result = this.getLocalPath().getALocalSource() }

    string getBucketNameAsResource() { result = bucket.getBucketNameAsResource() }
  }

  class S3BucketUpload extends DataFlow::CallCfgNode, File::LocalFile {
    S3Bucket bucket;
    API::Node apiNode;

    S3BucketUpload() {
      apiNode = bucket.getAPIMemberReturn().getMember("upload_file") and
      this = apiNode.getACall()
    }

    DataFlow::Node getRemotePath() { result in [this.getArg(1), this.getArgByName("Key")] }

    DataFlow::Node getLocalPath() { result in [this.getArg(0), this.getArgByName("Filename")] }

    override File::LocalFileOperation localFileOperation() { result = "READ" }

    override DataFlow::Node getFilePath() { result = this.getLocalPath().getALocalSource() }

    string getBucketNameAsResource() { result = bucket.getBucketNameAsResource() }
    // override string toString() { result = "S3BucketUpload" }
  }
}
