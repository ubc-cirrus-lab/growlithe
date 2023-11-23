/**
 * @kind problem
 * @id py/dataFlows
 */

import modules.Growlithe.TaintAnalysis
import queries.Config
import semmle.python.dataflow.new.DataFlow

predicate sourceWithoutFlows(
  DataFlow::Node source, DataFlow::Node sink, string sourceState, string sinkState
) {
  exists(TaintAnalysis::Tracker config |
    config.isSource(source, sourceState) and
    not config.hasFlow(source, _) and
    source = sink and
    sinkState = "None"
  )
}

predicate sinkWithoutFlows(
  DataFlow::Node source, DataFlow::Node sink, string sourceState, string sinkState
) {
  exists(TaintAnalysis::Tracker config |
    config.isSink(sink, sinkState) and
    not config.hasFlow(_, sink) and
    sink.getALocalSource() = source and
    sourceState = "None"
  )
}

predicate readAfterWriteEdges(
  DataFlow::Node source, DataFlow::Node sink, string sourceState, string sinkState
) {
  exists(File::LocalFile read, File::LocalFile write |
    Config::constrainLocation2(read) and
    Config::constrainLocation2(write) and
    read.localFileOperation() = "READ" and
    write.localFileOperation() = "WRITE" and
    read.getFilePath() = write.getFilePath() and
    write.asCfgNode().dominates(read.asCfgNode()) and
    source = write and
    sink = read and
    write.(Core::Sink).getFlowState() = sourceState and
    read.(Core::Source).getFlowState() = sinkState
  )
}

predicate taintFlowEdges(
  DataFlow::Node source, DataFlow::Node sink, string sourceState, string sinkState
) {
  exists(TaintAnalysis::Tracker config |
    config.hasFlow(source, sink) and
    config.isSource(source, sourceState) and
    config.isSink(sink, sinkState)
  )
}

// Query to get valid paths for these dataflows
from DataFlow::Node source, DataFlow::Node sink, string sourceState, string sinkState
where
  taintFlowEdges(source, sink, sourceState, sinkState) or
  readAfterWriteEdges(source, sink, sourceState, sinkState) or
  sourceWithoutFlows(source, sink, sourceState, sinkState) or
  sinkWithoutFlows(source, sink, sourceState, sinkState)
select sink, "$@==>$@", source, sourceState, sink, sinkState
// select "Detected Source", sourceState
// select "Detected Sink", sinkState
