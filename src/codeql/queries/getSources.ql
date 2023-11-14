/**
 * @kind problem
 * @id py/getSources
 */

import modules.Growlithe.TaintAnalysis
import queries.Config

// Query to find possible flows
from DataFlow::Node source, TaintAnalysis::Tracker config
where
  Config::constrainLocation(source.getLocation()) and
  config.isSource(source)
select source, "Taint source $@", source
