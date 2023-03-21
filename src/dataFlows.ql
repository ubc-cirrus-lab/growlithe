import Sinks
import utils.TaintTracker

// Query to find possible flows
from DataFlow::Node source, DataFlow::Node node, TaintTracker::Tracker config
where config.hasFlow(source, node)
select source, node
