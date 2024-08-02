import javascript
import DataFlow
import modules.Concepts.DynamoDB
import modules.Growlithe.Core
import modules.Growlithe.Utils

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
}