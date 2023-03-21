import utils.TaintTracker

// Query to get valid paths for these dataflows
from
  TaintTracker::Tracker config, DataFlow::PathNode source, DataFlow::PathNode sink,
  DataFlow::PathNode pred, DataFlow::PathNode succ
where
  config.hasFlowPath(source, sink) and
  DataFlow::PathGraph::edges(pred, succ)
select pred, succ
