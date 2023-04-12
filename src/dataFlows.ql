/**
 * @kind problem
 * @id py/dataFlows
 */

import utils.TaintTracker

// Query to find possible flows
from DataFlow::Node source, DataFlow::Node sink, TaintTracker::Tracker config, string source_name, string sink_name
where config.isSource(source, source_name) and config.isSink(sink, sink_name)
and config.hasFlow(source, sink)
select source.getLocation().getFile().getAbsolutePath(), "Taint from $@ ==> $@", source,
  source_name, sink, sink_name
