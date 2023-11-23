from sarif import loader
from src.graph.graph import Graph
from src.graph.parser import parse_and_add_flow
from src.logger import logger

# TODO: Move to config and make paths os independent
benchmarks_root_path = "D:\\Code\\serverless-compliance\\benchmarks"
benchmark = "ImageProcessingStateMachine"
codeql_db_path = f"{benchmarks_root_path}\\{benchmark}\\codeqldb\\"
codeql_output_path = f"{benchmarks_root_path}\\{benchmark}\\output\\"

sarif_data = loader.load_sarif_file(f"{codeql_output_path}\\dataflows.sarif")

results = sarif_data.get_results()

graph = Graph()
for result in results:
    related_locations = result["relatedLocations"]
    for flow in result["message"]["text"].split("\n"):
        # Flows are typically in form of"[SOURCE, GLOBAL, S3_BUCKET:STATIC:imageprocessingbenchmark, STATIC:sample_2.png](1)==>[SINK, CONTAINER, LOCAL_FILE:STATIC:tempfs, DYNAMIC:tempFile](2)"
        parse_and_add_flow(
            flow,
            graph,
            related_locations,
            default_function=result["locations"][0]["physicalLocation"][
                "artifactLocation"
            ]["uri"],
        )

# To debug and see intra-function
sub_graph = graph.get_sub_graph(
    "LambdaFunctions/ImageProcessingRotate/lambda_function.py"
)

logger.info("Generated Graph Successfully")
