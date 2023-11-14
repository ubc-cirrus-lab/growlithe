/**
 * @kind problem
 * @id py/getSinks
 */

import modules.Growlithe.TaintAnalysis
import modules.Growlithe.Core
import modules.Growlithe.Sinks
import queries.Config

// Query to find possible flows
from DataFlow::Node sink, TaintAnalysis::Tracker config, string flowState
where
  Config::constrainLocation(sink.getLocation()) and
  config.isSink(sink, flowState)
select sink, "Taint sink $@", sink, flowState
