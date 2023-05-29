/**
 * @kind path-problem
 * @id py/flowPaths
 */

import TaintTracker
import DataFlow::PathGraph

// Query to get valid paths for these dataflows
from TaintTracker::Tracker config, DataFlow::PathNode edgeSource, DataFlow::PathNode edgeSink
where config.hasFlowPath(edgeSource, edgeSink)
select edgeSink.getNode(), edgeSource, edgeSink, "FlowPath"