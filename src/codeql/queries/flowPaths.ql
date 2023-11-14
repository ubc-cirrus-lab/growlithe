/**
 * @kind path-problem
 * @id py/test
 */

import modules.Growlithe.TaintAnalysis
import DataFlow::PathGraph
import queries.Config

// Query to get valid paths for these dataflows
from TaintAnalysis::Tracker config, DataFlow::PathNode edgeSource, DataFlow::PathNode edgeSink
where
  Config::constrainLocation(edgeSource.getNode().asCfgNode().getLocation()) and
  config.hasFlowPath(edgeSource, edgeSink)
select edgeSink.getNode(), edgeSource, edgeSink, "Exists a flow from $@"
