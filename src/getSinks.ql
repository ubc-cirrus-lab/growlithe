/**
 * @kind problem
 * @id py/getSinks
 */

 import TaintTracker

 // Query to find possible flows
 from DataFlow::Node sink, TaintTracker::Tracker config, string sink_name
 where config.isSink(sink, sink_name)
 select sink, "Taint sink $@", sink, sink_name
 