import python
import semmle.python.dataflow.new.DataFlow
import semmle.python.ApiGraphs
import modules.growlithe_dfa.Core
import modules.growlithe_dfa.Utils
import modules.concepts.File

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

    DataFlow::Node getUpdateExpression() {
      result in [this.getArg(2), this.getArgByName("ExpressionAttributeValues")]
    }

    string getTableNameAsResource() { result = table.getTableNameAsResource() }
  }

  class DynamoDBTablePutItem extends DataFlow::CallCfgNode {
    DynamoDBTable table;
    API::Node apiNode;

    DynamoDBTablePutItem() {
      table = any(DynamoDBTable b) and
      apiNode = table.getAPIMemberReturn().getMember("put_item") and
      this = apiNode.getACall()
    }

    DynamoDBTable getTable() { result = table }

    DataFlow::Node getItem() { result in [this.getArg(0), this.getArgByName("Item")] }

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

    DataFlow::Node getKeyConditionExpression() {
      result in [this.getArg(0), this.getArgByName("KeyConditionExpression")]
    }

    DataFlow::Node getExpressionAttributeValues() {
      result in [this.getArgByName("ExpressionAttributeValues")]
    }

    // DataFlow::Node getUpdateExpression() { result in [this.getArg(2), this.getArgByName("ExpressionAttributeValues")] }
    string getTableNameAsResource() { result = table.getTableNameAsResource() }
  }

  class DynamoDBTableDelete extends DataFlow::CallCfgNode {
    DynamoDBTable table;
    API::Node apiNode;

    DynamoDBTableDelete() {
      table = any(DynamoDBTable b) and
      apiNode =
        table.getAPIMemberReturn().getMember("batch_writer").getReturn().getMember("delete_item") and
      this = apiNode.getACall()
    }

    DynamoDBTable getTable() { result = table }

    DataFlow::Node getKey() { result in [this.getArg(0), this.getArgByName("Key")] }

    // DataFlow::Node getUpdateExpression() { result in [this.getArg(2), this.getArgByName("ExpressionAttributeValues")] }
    string getTableNameAsResource() { result = table.getTableNameAsResource() }
  }
}
