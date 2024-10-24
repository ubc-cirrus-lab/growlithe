import python
import semmle.python.dataflow.new.DataFlow
import semmle.python.ApiGraphs
import modules.growlithe_dfa.Core
import modules.growlithe_dfa.Utils
import modules.concepts.File

module FirestoreDB {
  class FirestoreClient extends DataFlow::CallCfgNode {
    API::Node apiNode;

    FirestoreClient() {
      apiNode =
        API::moduleImport("google").getMember("cloud").getMember("firestore").getMember("Client") and
      this = apiNode.getACall()
    }

    API::Node getAPIMemberReturn() { result = apiNode.getReturn() }
  }

  class FirestoreCollection extends DataFlow::CallCfgNode {
    FirestoreClient client;
    API::Node apiNode;

    FirestoreCollection() {
      client = any(FirestoreClient c) and
      apiNode = client.getAPIMemberReturn().getMember("collection") and
      this = apiNode.getACall()
    }

    DataFlow::Node getDocumentReference() { result = this.getArg(0) }

    FirestoreClient getClient() { result = client }

    DataFlow::Node getCollectionName() { result = this.getArg(0) }

    string getCollectionNameAsResource() {
      result = "FIRESTORE_COLLECTION:" + Utils::strRepr(getCollectionName())
    }

    override string toString() { result = getCollectionNameAsResource() }

    API::Node getAPIMemberReturn() { result = apiNode.getReturn() }
  }

  class FirestoreQuery extends DataFlow::CallCfgNode {
    FirestoreCollection collection;
    API::Node apiNode;

    FirestoreQuery() {
      collection = any(FirestoreCollection c) and
      apiNode = collection.getAPIMemberReturn().getMember("where") and
      // .getReturn().getMember("where") and
      this = apiNode.getACall()
    }

    FirestoreCollection getCollection() { result = collection }

    DataFlow::Node getField() { result = this.getArg(0) }

    DataFlow::Node getOperator() { result = this.getArg(1) }

    DataFlow::Node getValue() { result = this.getArg(2) }

    string getCollectionNameAsResource() { result = collection.getCollectionNameAsResource() }

    API::Node getAPIMemberReturn() { result = apiNode.getReturn() }
  }

  class FirestoreStream extends DataFlow::CallCfgNode {
    FirestoreQuery query;
    API::Node apiNode;

    FirestoreStream() {
      query = any(FirestoreQuery q) and
      apiNode = query.getAPIMemberReturn().getMember("stream") and
      this = apiNode.getACall()
    }

    FirestoreQuery getQuery() { result = query }

    string getCollectionNameAsResource() { result = query.getCollectionNameAsResource() }
  }

  class FirestoreDocumentReference extends DataFlow::CallCfgNode {
    FirestoreCollection collection;
    API::Node apiNode;

    FirestoreDocumentReference() {
      collection = any(FirestoreCollection c) and
      apiNode = collection.getAPIMemberReturn().getMember("document") and
      this = apiNode.getACall()
    }

    FirestoreCollection getCollection() { result = collection }

    DataFlow::Node getDocumentId() { result = this.getArg(0) }

    API::Node getAPIMemberReturn() { result = apiNode.getReturn() }
  }

  class FirestoreBatch extends DataFlow::CallCfgNode {
    FirestoreClient client;
    API::Node apiNode;

    FirestoreBatch() {
      client = any(FirestoreClient c) and
      apiNode = client.getAPIMemberReturn().getMember("batch") and
      this = apiNode.getACall()
    }

    FirestoreClient getClient() { result = client }

    API::Node getAPIMemberReturn() { result = apiNode.getReturn() }
  }

  class FirestoreBatchDelete extends DataFlow::CallCfgNode {
    FirestoreBatch batch;
    API::Node apiNode;

    FirestoreBatchDelete() {
      batch = any(FirestoreBatch b) and
      apiNode = batch.getAPIMemberReturn().getMember("delete") and
      this = apiNode.getACall()
    }

    FirestoreBatch getBatch() { result = batch }

    DataFlow::Node getDocumentReference() { result = this.getArg(0) }

    FirestoreCollection getCollection() {
      exists(FirestoreDocumentReference docRef |
        docRef.getAPIMemberReturn().getAValueReachableFromSource() =
          this.getArg(0).getALocalSource()
      |
        result = docRef.getCollection()
      )
    }

    string getCollectionNameAsResource() {
      exists(FirestoreCollection coll | coll = this.getCollection() |
        result = coll.getCollectionNameAsResource()
      )
    }
  }
}
