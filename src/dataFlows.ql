/**
 * @kind problem
 * @id py/dataFlows
 */

import utils.TaintTracker

// Query to find possible flows
from DataFlow::Node source, DataFlow::Node sink, TaintTracker::Tracker config
where config.hasFlow(source, sink)
select source.getLocation().getFile().getAbsolutePath(), "Taint from $@ ==> $@", source,
  "FlowSource", sink, "FlowSink"
