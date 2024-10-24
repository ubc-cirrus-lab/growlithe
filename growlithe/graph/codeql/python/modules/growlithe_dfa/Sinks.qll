import python
import modules.growlithe_dfa.Core
import modules.concepts.S3Bucket
import modules.concepts.DynamoDB
import modules.concepts.FireStore
import modules.concepts.Lambda
import modules.concepts.Image

module Sinks {
  class ReturnExpression extends Core::Sink {
    ReturnExpression() {
      exists(Return ret | this.asCfgNode() = ret.getASubExpression().getAFlowNode())
    }

    override Utils::ShareType getShareType() { result = "INVOCATION" }

    override DataFlow::Node getMetadataSink() { none() }

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

    override DataFlow::Node getMetadataSink() { result = super.getRemotePath() }

    override string getObjectPath() { result = Utils::strRepr(super.getRemotePath()) }

    override string getResource() { result = super.getBucketNameAsResource() }
  }

  class DynamoDBTableUpdateItemSink extends Core::Sink, DynamoDBTable::DynamoDBTableUpdateItem {
    override Utils::ShareType getShareType() { result = "GLOBAL" }

    override string getObjectPath() { result = Utils::strRepr(super.getKey()) }

    override string getResource() { result = super.getTableNameAsResource() }

    override DataFlow::Node getMetadataSink() { result = super.getKey() }
  }

  class DynamoDBTablePutItemSink extends Core::Sink, DynamoDBTable::DynamoDBTablePutItem {
    override Utils::ShareType getShareType() { result = "GLOBAL" }

    override string getObjectPath() { result = Utils::strRepr(super.getItem()) }

    override string getResource() { result = super.getTableNameAsResource() }
  }

  class DynamoDBTableDeleteItemSink extends Core::Sink, DynamoDBTable::DynamoDBTableDelete {
    override Utils::ShareType getShareType() { result = "GLOBAL" }

    override string getObjectPath() { result = Utils::strRepr(super.getKey()) }

    override string getResource() { result = super.getTableNameAsResource() }
    // override DataFlow::Node getMetadataSink() { result = super.getKey()  }
  }

  class FirestoreBatchDelete extends Core::Sink, FirestoreDB::FirestoreBatchDelete {
    override Utils::ShareType getShareType() { result = "GLOBAL" }

    override string getObjectPath() { result = Utils::strRepr(super.getDocumentReference()) }

    override string getResource() { result = super.getCollectionNameAsResource() }
    // override DataFlow::Node getMetadataSink() { result = super.getKey()  }
  }

  class LambdaInvoke extends Core::Sink, LambdaInvoke::LambdaInvoke {
    override Utils::ShareType getShareType() { result = "GLOBAL" }

    override string getObjectPath() { result = Utils::strRepr(super.getPayload()) }

    override string getResource() { result = super.getFunctionNameAsResource() }
  }

  class ImageSaveSink extends Core::Sink, Image::ImageSave {
    override Utils::ShareType getShareType() { result = "CONTAINER" }

    override string getObjectPath() { result = Utils::strRepr(super.getArg(0)) }

    override string getResource() { result = Utils::localFileResource() }
  }
}
