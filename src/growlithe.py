from src import sarif_extractor
from src.codeql.codeql import CodeQL
from src.graph.node import NodeType, DataflowType
from src.logger import logger


class Growlithe:
    def __init__(self, app_path):
        self.app_path = app_path
        self.resource_extractor = None
        self.template_path = None
        self.graph = None

    def run(self):
        # =================================== Build Dependency Graph ========================================== #
        # Stage 1: Extract resources from state machine or CloudFormation template
        logger.info("Extracting functions and resources from the template...")
        self.graph = self.resource_extractor(self.template_path)
        logger.debug("Initial graph extracted from the template:")
        self.graph.print()

        CodeQL.analyze(self.app_path)

        # Stage 2, 3: Extract sources and sinks within each function from SARIF files & add internal edges
        self.source_and_sink_extractor()

        # Stage 4: Connect internal nodes to external nodes
        # TODO: Refactor for other kinds of invocations
        self.graph.connect_nodes_across_functions(self.graph.nodes[0])

        logger.debug("Graph after adding internal nodes and edges:")
        self.graph.print()

        # =================================== Policy Initialization ========================================== #
        # Stage 5: Suggest direct policies to developer
        self.graph.init_policies()
        # =================================== Taint Set Generation ========================================== #
        self.graph.generate_taints()
        # ============================== Edge Annotation (Static Enforcement) ================================ #
        self.graph.annotate_edges()
        # graph.init_security_labels(f"{QUERY_RESULTS_PATH}{APP_NAME}_security_labels.json")
        # graph.find_violations()

        logger.debug("Final graph:")
        self.graph.print()

        # FIXME: Update for new graph representation
        # graph.visualize(vis_out_path=f"{QUERY_RESULTS_PATH}Graph.png", graphic=True)

    def source_and_sink_extractor(self):
        # Iterate on a copy of the nodes as they are modified later
        functions = self.graph.nodes.copy()
        sarif_output = f"{self.app_path}/output"
        function_nodes = [node for node in functions if node.node_type == NodeType.FUNCTION]
        for node in function_nodes:
            logger.debug(f"Expanding internal graph for {node.name}")
            sarif_extractor.add_internal_nodes(
                f"{sarif_output}/{node.name}_getSources.sarif",
                node, self.graph, DataflowType.SOURCE)
            sarif_extractor.add_internal_nodes(
                f"{sarif_output}/{node.name}_getSinks.sarif",
                node, self.graph, DataflowType.SINK)
            sarif_extractor.add_internal_edges(
                f"{sarif_output}/{node.name}_flowPaths.sarif", self.graph)
            sarif_extractor.add_node_conditions(
                f"{sarif_output}/{node.name}_sinkConditions.sarif", self.graph, self.app_path)

