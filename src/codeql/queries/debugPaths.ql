/**
 * @kind problem
 * @id py/dataFlows
 */

import modules.Growlithe.TaintAnalysis
import semmle.python.dataflow.new.DataFlow

// Query to find possible flows
from DataFlow::Node source, DataFlow::Node sink, TaintAnalysis::Tracker config, string filepath
where
  config.isSource(source) and //and config.isSink(sink, sink_name)
  //  source instanceof DataFlow::ParameterNode and
  //  config.hasFlow(source, sink) and
  source.hasLocationInfo(filepath, _, _, _, _) and
  filepath.matches("%/test.py")
select source
