import javascript
import semmle.javascript.dataflow.DataFlow
import modules.Growlithe.Core
import modules.Growlithe.Utils

module Firestore {
  class FirestoreClient extends DataFlow::InvokeNode {
    FirestoreClient() {
      this = DataFlow::moduleMember("@google-cloud/firestore", "Firestore").getAnInvocation()
    }
  }

  class FirestoreCollection extends DataFlow::CallNode {
    FirestoreClient client;

    FirestoreCollection() {
      client = any(FirestoreClient f) and
      this = client.getAMethodCall("collection")
    }

    DataFlow::Node getCollectionName() { result = this.getArgument(0) }
    
  }

  class FirestoreDocument extends DataFlow::CallNode {
    FirestoreCollection collection;

    FirestoreDocument() {
      collection = any(FirestoreCollection c) and
      this = collection.getAMethodCall("doc")
    }

    DataFlow::Node getDocumentId() { result = this.getArgument(0) }
    FirestoreCollection getFirestoreCollection() { result = collection }
  }

  class FirestoreSet extends DataFlow::CallNode {
    FirestoreDocument document;

    FirestoreSet() {
      document = any(FirestoreDocument d) and
      this = document.getAMethodCall("set")
    }

    DataFlow::Node getData() { result = this.getArgument(0) }
    DataFlow::Node getOptions() { result = this.getArgument(1) }
    FirestoreCollection getFirestoreCollection() { result = document.getFirestoreCollection() }
  }

  class FirestoreUpdate extends DataFlow::CallNode {
    FirestoreDocument document;

    FirestoreUpdate() {
      document = any(FirestoreDocument d) and
      this = document.getAMethodCall("update")
    }

    DataFlow::Node getData() { result = this.getArgument(0) }
    FirestoreCollection getFirestoreCollection() { result = document.getFirestoreCollection() }
  }

  class FirestoreGet extends DataFlow::CallNode {
    FirestoreDocument document;

    FirestoreGet() {
      document = any(FirestoreDocument d) and
      this = document.getAMethodCall("get")
    }
  }

  class FirestoreFieldValue extends DataFlow::CallNode {
    FirestoreFieldValue() {
      this = DataFlow::moduleMember("@google-cloud/firestore", "Firestore").getAPropertyRead("FieldValue").getAMemberCall("increment")
    }

    DataFlow::Node getIncrementKey() { result = this.getArgument(0) }
  }
}