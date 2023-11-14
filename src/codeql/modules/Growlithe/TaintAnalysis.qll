import python
import semmle.python.dataflow.new.DataFlow
import semmle.python.dataflow.new.TaintTracking

import modules.Growlithe.AdditionalTaints
import modules.Growlithe.Sources
import modules.Growlithe.Sinks
import modules.Growlithe.Core

// module Config {
//   string pathConstraint() { result = "%/test.py" }
// }

module TaintAnalysis {
  class Tracker extends TaintTracking::Configuration {
    Tracker() { this = "Growlithe::TaintAnalysis" }

    override predicate isSource(DataFlow::Node source) {
      source instanceof Core::Source
      // and source.getLocation().getFile().getAbsolutePath().matches(Config::pathConstraint())
    }

    override predicate isSink(DataFlow::Node sink) {
      sink instanceof Core::Sink
      // and sink.getLocation().getFile().getAbsolutePath().matches(Config::pathConstraint())
    }

    override predicate isAdditionalTaintStep(DataFlow::Node node1, DataFlow::Node node2) {
      any(AdditionalTaints::AdditionalTaintStep s).step(node1, node2)
    }
  }
}
