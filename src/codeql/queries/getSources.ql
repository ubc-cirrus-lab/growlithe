/**
 * @kind problem
 * @id py/getSources
 */

import modules.Growlithe.TaintAnalysis
import queries.Config

// Query to find possible flows
from DataFlow::Node source, TaintAnalysis::Tracker config, string flowState
where
  Config::constrainLocation(source.getLocation()) and
  config.isSource(source, flowState)
select source, "Taint source $@", source, flowState
