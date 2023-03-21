import Sinks
import Sources
import python
import semmle.python.dataflow.new.DataFlow
import semmle.python.dataflow.new.TaintTracking

module TaintTracker {
  class Tracker extends TaintTracking::Configuration {
    Tracker() { this = "TaintTracker" }

    override predicate isSource(DataFlow::Node source) { source = Sources::get_sources() }

    override predicate isSink(DataFlow::Node sink) { sink = Sinks::get_sinks() }
  }
}
