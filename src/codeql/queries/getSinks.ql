/**
 * @kind problem
 * @id py/getSinks
 */

import modules.Growlithe.TaintAnalysis
import queries.Config

// Query to find possible flows
from DataFlow::Node sink, TaintAnalysis::Tracker config
where
  Config::constrainLocation(sink.getLocation()) and
  config.isSink(sink)
select sink, "Taint sink $@", sink
