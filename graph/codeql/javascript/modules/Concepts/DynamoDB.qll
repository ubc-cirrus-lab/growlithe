import javascript
import semmle.javascript.dataflow.DataFlow
import modules.Growlithe.Core
import modules.Growlithe.Utils

module DynamoDB {
  // select DataFlow::moduleMember("aws-sdk", "DynamoDB").getAConstructorInvocation("DocumentClient").getAMethodCall()
  class DynamoDBClient extends DataFlow::NewNode {
    //     API::Node apiNode;
    DynamoDBClient() {
      this =
        DataFlow::moduleMember("aws-sdk", "DynamoDB").getAConstructorInvocation("DocumentClient")
    }
    //     API::Node getAPIMemberReturn() { result = apiNode.getReturn() }
    //     DataFlow::Node getTableName() { result = this.getArg(0) }
    //     string getTableNameAsResource() { result = "DYNAMODB_TABLE:" + Utils::strRepr(getTableName()) }
    //     override string toString() { result = getTableNameAsResource() }
  }

  class DynamoDBTableUpdateItem extends DataFlow::CallNode {
    DynamoDBClient client;

    DynamoDBTableUpdateItem() {
      client = any(DynamoDBClient d) and
      this = client.getAMethodCall("update")
    }

    DataFlow::Node getTable() {
      result = Utils::getObjectProperty(this.getArgument(0), "TableName")
    }

    DataFlow::Node getKey() { result = Utils::getObjectProperty(this.getArgument(0), "Key") }

    DataFlow::Node getUpdateExpression() {
      result = Utils::getObjectProperty(this.getArgument(0), "ExpressionAttributeValues")
    }
    //     DataFlow::Node getKey() { result in [this.getArg(0), this.getArgByName("Key")] }
    //     DataFlow::Node getUpdateExpression() { result in [this.getArg(2), this.getArgByName("ExpressionAttributeValues")] }
    //     string getTableNameAsResource() { result = table.getTableNameAsResource() }
  }
  //   class DynamoDBTableGetItem extends DataFlow::CallCfgNode {
  //     DynamoDBTable table;
  //     API::Node apiNode;
  //     // API::Node item;
  //     DynamoDBTableGetItem() {
  //       table = any(DynamoDBTable b) and
  //       apiNode = table.getAPIMemberReturn().getMember("get_item") and
  //       this = apiNode.getACall()
  //     }
  //     DynamoDBTable getTable() { result = table }
  //     DataFlow::Node getKey() { result in [this.getArg(0), this.getArgByName("Key")] }
  //     string getTableNameAsResource() { result = table.getTableNameAsResource() }
  //   }
  //   class DynamoDBTableScan extends DataFlow::CallCfgNode {
  //     DynamoDBTable table;
  //     API::Node apiNode;
  //     DynamoDBTableScan() {
  //       table = any(DynamoDBTable b) and
  //       apiNode = table.getAPIMemberReturn().getMember("scan") and
  //       this = apiNode.getACall()
  //     }
  //     DynamoDBTable getTable() { result = table }
  //     string getTableNameAsResource() { result = table.getTableNameAsResource() }
  //   }
  //   class DynamoDBTableQuery extends DataFlow::CallCfgNode {
  //     DynamoDBTable table;
  //     API::Node apiNode;
  //     DynamoDBTableQuery() {
  //       table = any(DynamoDBTable b) and
  //       apiNode = table.getAPIMemberReturn().getMember("query") and
  //       this = apiNode.getACall()
  //     }
  //     DynamoDBTable getTable() { result = table }
  //     DataFlow::Node getKeyConditionExpression() { result in [this.getArg(0), this.getArgByName("KeyConditionExpression")] }
  //     // DataFlow::Node getUpdateExpression() { result in [this.getArg(2), this.getArgByName("ExpressionAttributeValues")] }
  //     string getTableNameAsResource() { result = table.getTableNameAsResource() }
  //   }
}
