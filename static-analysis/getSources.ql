/**
 * @kind problem
 * @id py/getSources
 */

import TaintTracker

// Query to find possible flows
from DataFlow::Node source, TaintTracker::Tracker config, string source_name
where config.isSource(source, source_name)
select source, "Taint source $@", source, source_name
