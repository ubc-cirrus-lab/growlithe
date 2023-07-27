/**
 * @kind problem
 * @id py/sink-conditions
 */

import TaintTracker

// Query to find conditions that required for flow from a sink node in a function
from DataFlow::Node sink, TaintTracker::Tracker config, ConditionBlock cond, string sink_name, boolean required_boolean
where config.isSink(sink, sink_name)
and ((required_boolean = true and cond.controls(sink.asCfgNode().getBasicBlock(), true))
or (required_boolean = false and cond.controls(sink.asCfgNode().getBasicBlock(), false)))
select sink, "Taint sink $@ requires " + required_boolean.toString() + " for $@", sink, sink_name, cond.getLastNode(), "condition"
