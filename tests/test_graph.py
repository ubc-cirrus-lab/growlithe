import os
import unittest
from growlithe.cli.analyze import analyze
from growlithe.config import get_config


class TestGraph(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        # Get the directory of the current file
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # Construct the path to the sample_app directory
        self.sample_app_dir = os.path.join(current_dir, "sample_app")
        # Construct the path to growlithe_config.yaml
        self.custom_config_path = os.path.join(
            self.sample_app_dir, "growlithe_config.yaml"
        )

        self.config = get_config(os.path.abspath(self.custom_config_path))

    def tearDown(self):
        pass

    def test_graph(self):
        graph = analyze(self.config)
        print(len(graph.nodes))
        print(len(graph.functions))

        self.assertEqual(len(graph.functions), 2)
        self.assertEqual(len(graph.edges), 7)


if __name__ == "__main__":
    unittest.main(verbosity=2)
