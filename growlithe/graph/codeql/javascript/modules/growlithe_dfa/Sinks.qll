import javascript
import DataFlow
import modules.concepts.DynamoDB
import modules.concepts.FirestoreDB
import modules.growlithe_dfa.Core
import modules.growlithe_dfa.Utils

module Sinks {
  class ReturnSink extends Core::Sink {
    Function f;

    ReturnSink() {
      f.getName() = "handler" and
      this = f.getAReturnedExpr().flow()
    }

    override Utils::ShareType getShareType() { result = "INVOCATION" }

    override string getResource() { result = "RETURN:STATIC:SourceCode" }

    override string getObjectPath() { result = Utils::strRepr(this) }
  }

  class DynamoDBTableUpdateItemSink extends Core::Sink, DynamoDB::DynamoDBTableUpdateItem {
    override Utils::ShareType getShareType() { result = "GLOBAL" }

    override string getObjectPath() { result = Utils::strRepr(super.getKey()) }

    override string getResource() { result = Utils::strRepr(super.getTable()) }
  }

  class FirestoreDBSetSink extends Core::Sink, Firestore::FirestoreSet {
    override Utils::ShareType getShareType() { result = "GLOBAL" }

    override string getObjectPath() { result = Utils::strRepr(super.getData()) }

    override string getResource() { result = Utils::strRepr(super.getFirestoreCollection()) }
  }

  class FirestoreDBUpdateSink extends Core::Sink, Firestore::FirestoreUpdate {
    override Utils::ShareType getShareType() { result = "GLOBAL" }

    override string getObjectPath() { result = Utils::strRepr(super.getData()) }

    override string getResource() { result = Utils::strRepr(super.getFirestoreCollection()) }
  }
}
