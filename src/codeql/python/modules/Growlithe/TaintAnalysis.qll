import python
import semmle.python.dataflow.new.DataFlow
import semmle.python.dataflow.new.TaintTracking
import modules.Growlithe.AdditionalTaints
import modules.Growlithe.Sources
import modules.Growlithe.Sinks
import modules.Growlithe.Core
import queries.Config

module TaintAnalysis {
  // We create a custom taint tracking configuration that extends the default
  // configuration with our own sources and sinks.
  class Tracker extends TaintTracking::Configuration {
    Tracker() { this = "Growlithe::TaintAnalysis" }

    // Add our own sources by modeling them as Core::Source nodes.
    override predicate isSource(DataFlow::Node source) {
      source instanceof Core::Source and
      Config::constrainLocation2(source)
    }

    // Add our own sink by modeling them as Core::Sink nodes.
    override predicate isSink(DataFlow::Node sink) {
      sink instanceof Core::Sink and
      Config::constrainLocation2(sink)
    }

    // Add our own sources by modeling them as Core::Source nodes.
    override predicate isSource(DataFlow::Node source, string state) {
      isSource(source) and
      state = source.(Core::Source).getFlowState()
    }

    // Add our own sink by modeling them as Core::Sink nodes.
    override predicate isSink(DataFlow::Node sink, string state) {
      isSink(sink) and
      state = sink.(Core::Sink).getFlowState()
    }

    // Add additional taint steps by modeling them as
    // AdditionalTaints::AdditionalTaintStep nodes.
    override predicate isAdditionalTaintStep(DataFlow::Node node1, DataFlow::Node node2) {
      any(AdditionalTaints::AdditionalTaintStep s).step(node1, node2) and
      Config::constrainLocation2(node1) and
      Config::constrainLocation2(node2)
    }
  }
}
