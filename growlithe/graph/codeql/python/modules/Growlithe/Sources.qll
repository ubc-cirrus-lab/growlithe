import python
import modules.Growlithe.Core
import modules.Growlithe.Utils
import modules.Concepts.S3Bucket
import modules.Concepts.DynamoDB
import modules.Concepts.FireStore
import modules.Concepts.Image
import semmle.python.internal.ConceptsShared

module Sources {
  class ParameterSource extends Core::Source {
    ParameterSource() {
      exists(DataFlow::ParameterNode p |
        p = this and
        //Gets $event and ignores $context
        p.getParameter().getPosition() = 0
      )
      // this instanceof DataFlow::ParameterNode
    }

    override string getObjectPath() { result = Utils::strRepr(this) }

    override Utils::ShareType getShareType() { result = "INVOCATION" }

    override string getResource() { result = "PARAM:STATIC:SourceCode" }
  }

  class S3BucketDownloadSource extends Core::Source, S3Bucket::S3BucketDownload {
    override Utils::ShareType getShareType() { result = "GLOBAL" }

    override DataFlow::Node getMetadataSink() { result = super.getRemotePath() }

    override string getObjectPath() { result = Utils::strRepr(super.getRemotePath()) }

    override string getResource() { result = super.getBucketNameAsResource() }
  }

  class S3BucketUploadSource extends Core::Source, S3Bucket::S3BucketUpload {
    override Utils::ShareType getShareType() { result = "CONTAINER" }

    override string getObjectPath() { result = Utils::strRepr(super.getLocalPath()) }

    override string getResource() { result = Utils::localFileResource() }
  }

  class FirestoreQuery extends Core::Source, FirestoreDB::FirestoreQuery {
    override Utils::ShareType getShareType() { result = "GLOBAL" }

    override string getObjectPath() { result = "STATIC:ALL_RECORDS" }

    override string getResource() { result = super.getCollectionNameAsResource() }

    override DataFlow::Node getMetadataSink() { result = super.getValue()  }
  }

  class DynamoDBTableGetItemSource extends Core::Source, DynamoDBTable::DynamoDBTableGetItem {
    override Utils::ShareType getShareType() { result = "GLOBAL" }

    override string getObjectPath() { result = Utils::strRepr(super.getKey()) }

    override string getResource() { result = super.getTableNameAsResource() }

    override DataFlow::Node getMetadataSink() { result = super.getKey()  }
  }

  class DynamoDBTableScanSource extends Core::Source, DynamoDBTable::DynamoDBTableScan {
    override Utils::ShareType getShareType() { result = "GLOBAL" }

    override string getObjectPath() { result = "STATIC:ALL_RECORDS" }

    override string getResource() { result = super.getTableNameAsResource() }
  }

  class DynamoDBTableQuerySource extends Core::Source, DynamoDBTable::DynamoDBTableQuery {
    override Utils::ShareType getShareType() { result = "GLOBAL" }

    override string getObjectPath() { result = "DYNAMIC:Query" }

    override DataFlow::Node getMetadataSink() { result in [super.getKeyConditionExpression(), super.getExpressionAttributeValues()]  }

    override string getResource() { result = super.getTableNameAsResource() }
  }

  class ImageOpenSource extends Core::Source, Image::ImageOpen {
    override Utils::ShareType getShareType() { result = "CONTAINER" }

    override string getObjectPath() { result = Utils::strRepr(super.getArg(0)) }

    override string getResource() { result = Utils::localFileResource() }
  }

  class HttpRequest extends Core::Source {
    Http::Client::Request httpClientRequest;

    HttpRequest() { this = httpClientRequest }
    override string getObjectPath() { result = Utils::strRepr(httpClientRequest.getAUrlPart()) }
    override Utils::ShareType getShareType() { result = "GLOBAL" }
    override string getResource() { result = "API:STATIC:API" }
    override DataFlow::Node getMetadataSink() { result = httpClientRequest.getAUrlPart() }
  }
}
