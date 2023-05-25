import os
import json
import numpy as np
import umap
from sentence_transformers import SentenceTransformer
import matplotlib.pyplot as plt
import yaml
# import random


class ScenarioUtils:

    def __init__(self, model_name, input_dir, output_dir, projection_file, meta_dir_path):
        self.model_name = model_name
        self.model = SentenceTransformer(self.model_name)

        self.input_dir = input_dir
        self.output_dir = output_dir

        self.projection_file = projection_file
        self.meta_dir_path = meta_dir_path

        self.colors = ["#b33dc6", "#e60049", "#0bb4ff", "#50e991", "#e6d800", "#9b19f5", "#ffa300", "#dc0ab4",
                       "#b3d4ff", "#00bfa0", "#ea5545", "#f46a9b", "#ef9b20", "#edbf33", "#ede15b", "#bdcf32",
                       "#87bc45", "#27aeef"] * 16

    def create_embeddings(self):
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

        for filename in os.listdir(self.input_dir):
            if filename.endswith('.txt'):
                with open(os.path.join(self.input_dir, filename), 'r') as f:
                    text = f.read()
                embedded = self.model.encode(text, convert_to_tensor=True)
                output_filename = os.path.join(self.output_dir, filename.replace('.txt', '.json'))
                with open(output_filename, 'w') as f:
                    json.dump(embedded.tolist(), f)

    def project_embeddings(self):
        # List all the JSON files in the directory
        file_list = os.listdir(self.output_dir)

        # Initialize an empty array to store the embeddings
        data = np.empty((len(file_list), 384))
        scenarios = []

        # Loop through each file
        for i, filename in enumerate(file_list):
            file_path = os.path.join(self.output_dir, filename)

            # Load the JSON file and extract the embedding array
            with open(file_path, 'r') as f:
                embedding = np.array(json.load(f), dtype=float)
                data[i] = embedding
                scenarios.append(filename.replace('scenario_', '').replace('.json', ''))

        umap_embeddings = umap.UMAP(n_neighbors=20,
                                    n_components=2,
                                    min_dist=0.1,
                                    metric='correlation').fit_transform(data)

        embeddings = umap_embeddings.tolist()
        projection = {scenarios[i]: embeddings[i] for i in range(len(scenarios))}

        with open(self.projection_file, 'w') as f:
            json.dump(projection, f)

    def plot_embeddings(self, group='Category'):
        with open(self.projection_file, 'r') as f:
            embeddings = json.load(f)

        attribute_data = {}
        for scenario, projection in embeddings.items():
            file_path = os.path.join(self.meta_dir_path, "scenario_%s.yaml" % scenario)
            attribute = 'Unknown'

            if os.path.isfile(file_path):
                with open(file_path, 'r') as stream:
                    metadata = yaml.safe_load(stream)
                    attribute = metadata.get(group, 'Unknown')

            if attribute not in attribute_data:
                attribute_data[attribute] = []

            attribute_data[attribute].append(scenario)

        fig, ax = plt.subplots()
        for i, (attr, scenarios) in enumerate(attribute_data.items()):
            projections = np.array([embeddings[scenario] for scenario in scenarios])
            x = projections[:, 0]
            y = projections[:, 1]
            ax.scatter(x, y, s=32, alpha=0.5, c=self.colors[i], label="%s (%d)" % (attr, len(scenarios)))

        ax.legend()
        plt.show()
