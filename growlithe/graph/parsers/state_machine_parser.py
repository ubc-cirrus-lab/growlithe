"""
Parses an AWS SAM template file to give a list of resource and their properties like events
"""

from typing import List
from growlithe.common.utils import profiler_decorator
from growlithe.graph.adg.resource import Resource
from growlithe.graph.adg.function import Function
from growlithe.config import Config


class StepFunctionParser:
    def __init__(self, sam_file, config):
        self.sam_file = sam_file
        self.resources = self.parse_step_function_config()
        self.config: Config = config

    @profiler_decorator
    def parse_step_function_config(self):
        benchmark_name = self.config.benchmark_name
        if benchmark_name == "Benchmark2":
            transform = Function(
                "Transform",
                "AWS::Serverless::Function",
                "python3.10",
                "src/transform_image/",
                {},
            )
            filter = Function(
                "Filter",
                "AWS::Serverless::Function",
                "python3.10",
                "src/filter_image/",
                {},
            )
            blur = Function(
                "Blur",
                "AWS::Serverless::Function",
                "python3.10",
                "src/blur_image/",
                {},
            )
            tag_store = Function(
                "Tag_Store",
                "AWS::Serverless::Function",
                "python3.10",
                "src/tag_store_image/",
                {},
            )

            transform.add_dependency(filter)
            filter.add_dependency(blur)
            filter.add_dependency(tag_store)
            blur.add_dependency(tag_store)

            funcs = [transform, filter, blur, tag_store]
        elif benchmark_name == "Benchmark3":
            add_to_cart = Function(
                "AddCart",
                "AWS::Serverless::Function",
                "python3.10",
                "src/add_to_cart/",
                {},
            )
            checkout_cart = Function(
                "CheckoutCart",
                "AWS::Serverless::Function",
                "python3.10",
                "src/checkout_cart/",
                {},
            )
            funcs = [add_to_cart, checkout_cart]
        return funcs

    def get_functions(self) -> List[Function]:
        return [
            resource for resource in self.resources if isinstance(resource, Function)
        ]

    def get_resources(self) -> List[Resource]:
        return self.resources

    def get_events(self):
        pass
