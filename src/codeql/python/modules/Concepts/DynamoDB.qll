import python
import semmle.python.dataflow.new.DataFlow
import semmle.python.ApiGraphs
import modules.Growlithe.Core
import modules.Growlithe.Utils
import modules.Concepts.File

module DynamoDBTable {
  class DynamoDBTable extends DataFlow::CallCfgNode {
    API::Node apiNode;

    DynamoDBTable() {
      apiNode = API::moduleImport("boto3").getMember("resource").getReturn().getMember("Table") and
      this = apiNode.getACall()
    }

    API::Node getAPIMemberReturn() { result = apiNode.getReturn() }

    DataFlow::Node getTableName() { result = this.getArg(0) }

    string getTableNameAsResource() { result = "DYNAMODB_TABLE:" + Utils::strRepr(getTableName()) }

    override string toString() { result = getTableNameAsResource() }
  }

  class DynamoDBTableGetItem extends DataFlow::CallCfgNode {
    DynamoDBTable table;
    API::Node apiNode;
    // API::Node item;

    DynamoDBTableGetItem() {
      table = any(DynamoDBTable b) and
      apiNode = table.getAPIMemberReturn().getMember("get_item") and
      this = apiNode.getACall()
    }

    DynamoDBTable getTable() { result = table }

    DataFlow::Node getKey() { result in [this.getArg(0), this.getArgByName("Key")] }

    string getTableNameAsResource() { result = table.getTableNameAsResource() }
  }

  
  class DynamoDBTableUpdateItem extends DataFlow::CallCfgNode {
    DynamoDBTable table;
    API::Node apiNode;

    DynamoDBTableUpdateItem() {
      table = any(DynamoDBTable b) and
      apiNode = table.getAPIMemberReturn().getMember("update_item") and
      this = apiNode.getACall()
    }

    DynamoDBTable getTable() { result = table }

    DataFlow::Node getKey() { result in [this.getArg(0), this.getArgByName("Key")] }

    DataFlow::Node getUpdateExpression() { result in [this.getArg(2), this.getArgByName("ExpressionAttributeValues")] }
    string getTableNameAsResource() { result = table.getTableNameAsResource() }
  }

  class DynamoDBTableScan extends DataFlow::CallCfgNode {
    DynamoDBTable table;
    API::Node apiNode;

    DynamoDBTableScan() {
      table = any(DynamoDBTable b) and
      apiNode = table.getAPIMemberReturn().getMember("scan") and
      this = apiNode.getACall()
    }

    DynamoDBTable getTable() { result = table }

    string getTableNameAsResource() { result = table.getTableNameAsResource() }
  }
    
  class DynamoDBTableQuery extends DataFlow::CallCfgNode {
    DynamoDBTable table;
    API::Node apiNode;

    DynamoDBTableQuery() {
      table = any(DynamoDBTable b) and
      apiNode = table.getAPIMemberReturn().getMember("query") and
      this = apiNode.getACall()
    }

    DynamoDBTable getTable() { result = table }

    DataFlow::Node getKeyConditionExpression() { result in [this.getArg(0), this.getArgByName("KeyConditionExpression")] }

    // DataFlow::Node getUpdateExpression() { result in [this.getArg(2), this.getArgByName("ExpressionAttributeValues")] }
    string getTableNameAsResource() { result = table.getTableNameAsResource() }
  }
}
