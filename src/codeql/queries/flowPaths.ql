/**
 * @kind path-problem
 * @id py/test
 */

import modules.Growlithe.TaintAnalysis
import DataFlow::PathGraph
import queries.Config

// Query to get valid paths for these dataflows
from TaintAnalysis::Tracker config, DataFlow::PathNode edgeSource, DataFlow::PathNode edgeSink
where config.hasFlowPath(edgeSource, edgeSink)
select edgeSink.getNode(), edgeSource, edgeSink, "Flow path from source to sink"
