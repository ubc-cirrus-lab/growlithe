/**
 * @kind problem
 * @id js/dataFlows
 */

import javascript
import modules.Growlithe.TaintAnalysis

// from TaintAnalysis::Tracker config, DataFlow::PathNode edgeSource, DataFlow::PathNode edgeSink
// where
// config.hasFlowPath(edgeSource, edgeSink)
// select edgeSink.getNode(), edgeSource, edgeSink, "FlowPath"
predicate sourceWithoutFlows(
  DataFlow::Node source, DataFlow::Node sink, string sourceState, string sinkState
) {
  exists(TaintAnalysis::Tracker config |
    config.isGrowlitheSource(source, sourceState) and
    not config.hasFlow(source, _) and
    source = sink and
    sinkState = "None"
  )
}

predicate sinkWithoutFlows(
  DataFlow::Node source, DataFlow::Node sink, string sourceState, string sinkState
) {
  exists(TaintAnalysis::Tracker config |
    config.isGrowlitheSink(sink, sinkState) and
    not config.hasFlow(_, sink) and
    sink.getALocalSource() = source and
    sourceState = "None"
  )
}

predicate taintFlowEdges(
  DataFlow::Node source, DataFlow::Node sink, string sourceState, string sinkState
) {
  exists(TaintAnalysis::Tracker config |
    config.hasFlow(source, sink) and
    config.isGrowlitheSource(source, sourceState) and
    config.isGrowlitheSink(sink, sinkState)
  )
}

// Query to get valid paths for these dataflows
from DataFlow::Node source, DataFlow::Node sink, string sourceState, string sinkState
where
  taintFlowEdges(source, sink, sourceState, sinkState) or
  sourceWithoutFlows(source, sink, sourceState, sinkState) or
  sinkWithoutFlows(source, sink, sourceState, sinkState)
select sink, "$@==>$@", source, sourceState, sink, sinkState
// from TaintAnalysis::Tracker config, DataFlow::Node source, DataFlow::Node sink
// where
//   config.isSource(source) and
//   config.isSink(sink) and
//   config.hasFlow(source, sink)
// select sink, source, sink, "FlowPath"
// from TaintAnalysis::Tracker config, DataFlow::Node source, DataFlow::Node sink
// where
//   config.isGrowlitheSource(source, _) and
//   config.isGrowlitheSink(sink, _) and
//   config.hasFlow(source, sink)
// select sink, source, sink, "FlowPath"
