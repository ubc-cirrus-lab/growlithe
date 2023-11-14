/**
 * @kind path-problem
 * @id py/test
 */

import modules.Growlithe.TaintAnalysis
import DataFlow::PathGraph
import queries.Config

// Query to get valid paths for these dataflows
from TaintAnalysis::Tracker config, DataFlow::PathNode edgeSource, DataFlow::PathNode edgeSink, string sourceState, string sinkState
where
  config.hasFlowPath(edgeSource, edgeSink) and
  config.isSource(edgeSource.getNode(), sourceState) and
  config.isSink(edgeSink.getNode(), sinkState)
select edgeSource, edgeSource, edgeSink, "Flow path from $@ to $@", edgeSource, sourceState, edgeSink, sinkState

