/**
 * @kind problem
 * @id py/dataFlows
 */

import modules.growlithe_dfa.TaintAnalysis
import queries.Config
import semmle.python.dataflow.new.DataFlow
import modules.growlithe_dfa.Core

from
  DataFlow::Node source, DataFlow::Node sink, string sourceState, string sinkState,
  TaintAnalysis::MetadataTracker config
where
  config.isSource(source, sourceState) and
  config.isSink(sink, sinkState) and
  config.hasFlow(source, sink)
select sink, "$@==>$@", source, sourceState, sink, sinkState
