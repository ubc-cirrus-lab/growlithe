import modules.Growlithe.TaintAnalysis
import modules.Growlithe.Sources
import modules.Growlithe.Sinks
import modules.Growlithe.AdditionalTaints
import queries.Config
import semmle.python.dataflow.new.DataFlow
import DataFlow::PathGraph
 
 
// Query to get valid paths for these dataflows
// from TaintAnalysis::Tracker config, DataFlow::PathNode edgeSource, DataFlow::PathNode edgeSink
// where
// config.hasFlowPath(edgeSource, edgeSink)
// select edgeSink.getNode(), edgeSource, edgeSink, "FlowPath"

// from
// TaintAnalysis::Tracker config, DataFlow::PathNode source, DataFlow::PathNode sink,
//   DataFlow::PathNode pred, DataFlow::PathNode succ
// where
// //   config.hasFlowPath(source, sink) and
//   DataFlow::PathGraph::edges(pred, succ, _, _) or config.isAdditionalTaintStep(pred.getNode(), succ.getNode())
// select pred, succ

from DataFlow::Node n1, DataFlow::Node n2, AdditionalTaints::MethodArgToMethodReturnStep ms
where
    ms.step(n1, n2) and
    n1.getLocation().getFile().getBaseName() = "assignAdjuster.py"
select n1, n2, "MethodArgToMethodReturnStep"