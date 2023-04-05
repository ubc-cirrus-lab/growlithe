/**
 * @kind path-problem
 * @id py/flowPaths
 */

import utils.TaintTracker

// Query to get valid paths for these dataflows
from TaintTracker::Tracker config, DataFlow::PathNode edgeSource, DataFlow::PathNode edgeSink
where
  config.hasFlowPath(edgeSource, edgeSink) and
  DataFlow::PathGraph::edges(edgeSource, edgeSink)
select edgeSource.getNode(), edgeSource, edgeSink, "FlowPath to $@", edgeSink.getNode(), "FlowSink"
