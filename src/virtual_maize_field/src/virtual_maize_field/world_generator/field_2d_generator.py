from __future__ import annotations

import importlib.resources
from typing import Any

import cv2
import jinja2
import numpy as np
from matplotlib import pyplot as plt
from shapely.geometry import LineString, Point, Polygon

from virtual_maize_field import world_generator
from virtual_maize_field.world_generator.models import (
    COTTON_MODELS,
    LITTER_MODELS,
    MARKER_MODELS,
    PUMPKIN_MODELS,
    WEED_MODELS,
    GazeboModel,
    to_gazebo_models,
)

from virtual_maize_field.world_generator.world_description import WorldDescription


class Field2DGenerator:
    def __init__(
        self,
        world_description: WorldDescription = WorldDescription(),
    ) -> None:
        self.wd = world_description

        self.weed_models = None
        self.pumpkin_models = None
        self.cotton_models = None
        self.litter_models = None
        self.marker_models = None

    def gather_available_models(self) -> None:
        if self.wd.structure["params"]["weeds"] > 0:
            self.weed_models = to_gazebo_models(
                WEED_MODELS,
                self.wd.structure["params"]["weed_types"],
            )

        if self.wd.structure["params"]["pumpkins"] > 0:
            self.pumpkin_models = to_gazebo_models(
                PUMPKIN_MODELS,
                self.wd.structure["params"]["pumpkin_types"],
            )

        if self.wd.structure["params"]["cottons"] > 0:
            self.cotton_models = to_gazebo_models(
                COTTON_MODELS,
                self.wd.structure["params"]["cotton_types"],
            )

        if self.wd.structure["params"]["litters"] > 0:
            self.litter_models = to_gazebo_models(
                LITTER_MODELS, self.wd.structure["params"]["litter_types"]
            )

        self.marker_models = MARKER_MODELS



    def plot_field(self):
        plt.plot()
        plt.figure(figsize=(10, 10))
        plt.gca().axis("equal")
        labels = []

        # crops
        # crops removed
        # weeds
        if self.weed_placements.shape[0] > 0:
            plt.scatter(
                self.weed_placements[:, 0],
                self.weed_placements[:, 1],
                color="r",
                marker=".",
                s=100,
                alpha=0.5,
            )
            labels.append("weeds")

        # pumpkins
        if self.pumpkin_placements.shape[0] > 0:
            plt.scatter(
                self.pumpkin_placements[:, 0],
                self.pumpkin_placements[:, 1],
                color="orange",
                marker="o",
                s=150,
                alpha=0.5,
            )
            labels.append("pumpkins")

        # cottons
        if self.cotton_placements.shape[0] > 0:
            plt.scatter(
                self.cotton_placements[:, 0],
                self.cotton_placements[:, 1],
                color="lightgray",
                marker="o",
                s=100,
                alpha=0.5,
            )
            labels.append("cottons")

        # litter
        if self.litter_placements.shape[0] > 0:
            plt.scatter(
                self.litter_placements[:, 0],
                self.litter_placements[:, 1],
                color="b",
                marker=".",
                s=100,
                alpha=0.5,
            )
            labels.append("litter")

        # start
        plt.scatter(
            self.start_loc[:, 0], self.start_loc[:, 1], color="g", marker=".", alpha=0
        )  # just to extend the axis of the plot
        plt.text(
            self.start_loc[:, 0],
            self.start_loc[:, 1],
            "START",
            bbox={"facecolor": "green", "alpha": 0.5, "pad": 10},
            ha="center",
            va="center",
        )

        # Axis
        plt.xlabel("x")
        plt.ylabel("y")

        plt.legend(labels)
        self.minimap = plt

    def generate(self, cache_dir: str) -> tuple[str, np.ndarray]:
        self.gather_available_models()
        self.setup_field_bounds()
        self.place_objects()
        self.generate_ground()
        self.fix_gazebo()
        self.render_to_template(cache_dir)
        self.plot_field()
        return self.sdf, self.heightmap

    def setup_field_bounds(self) -> None:

        length = self.wd.row_length
        width = length  # Make it square
        
        x_min = -width / 2
        x_max = width / 2
        y_min = -length / 2
        y_max = length / 2
        
        # CCW order
        self.boundary_points = np.array([
            [x_min, y_min],
            [x_max, y_min],
            [x_max, y_max],
            [x_min, y_max]
        ])
        
        # No crops in this mode
        
        # No rows to track
        self.rows = []

    # The function calculates the placements of the weed plants and
    def place_objects(self) -> None:
        def random_points_within(poly: Polygon, num_points: int) -> np.ndarray:
            min_x, min_y, max_x, max_y = poly.bounds

            points = []

            while len(points) < num_points:
                np_point = [
                    self.wd.rng.uniform(min_x, max_x),
                    self.wd.rng.uniform(min_y, max_y),
                ]
                random_point = Point(np_point)
                if random_point.within(poly):
                    points.append(np_point)

            return np.array(points)

        # Use the simple boundary defined earlier
        self.field_poly = Polygon(self.boundary_points)

        # place x_nr of weeds within the field area
        if self.wd.structure["params"]["weeds"] > 0:
            self.weed_placements = random_points_within(
                self.field_poly, self.wd.structure["params"]["weeds"]
            )
            random_weed_models = self.wd.rng.choice(
                list(self.weed_models.values()),
                self.wd.structure["params"]["weeds"],
            )
        else:
            self.weed_placements = np.array([]).reshape(0, 2)
            random_weed_models = []

        # place z_nr of pumpkins within the field area
        if self.wd.structure["params"]["pumpkins"] > 0:
            self.pumpkin_placements = random_points_within(
                self.field_poly, self.wd.structure["params"]["pumpkins"]
            )
            random_pumpkin_models = self.wd.rng.choice(
                list(self.pumpkin_models.values()),
                self.wd.structure["params"]["pumpkins"],
            )
        else:
            self.pumpkin_placements = np.array([]).reshape(0, 2)
            random_pumpkin_models = []

        # place w_nr of cottons within the field area
        if self.wd.structure["params"]["cottons"] > 0:
            self.cotton_placements = random_points_within(
                self.field_poly, self.wd.structure["params"]["cottons"]
            )
            random_cotton_models = self.wd.rng.choice(
                list(self.cotton_models.values()),
                self.wd.structure["params"]["cottons"],
            )
        else:
            self.cotton_placements = np.array([]).reshape(0, 2)
            random_cotton_models = []

        # place y_nr of litter within the field area
        if self.wd.structure["params"]["litters"] > 0:
            self.litter_placements = random_points_within(
                self.field_poly, self.wd.structure["params"]["litters"]
            )
            random_litter_models = self.wd.rng.choice(
                list(self.litter_models.values()),
                self.wd.structure["params"]["litters"],
            )

        else:
            self.litter_placements = np.array([]).reshape(0, 2)
            random_litter_models = []

        # place start marker at the beginning of the field
        # Start at bottom center
        p_start_center = np.array([
            (self.boundary_points[0,0] + self.boundary_points[1,0])/2, 
            (self.boundary_points[0,1] + self.boundary_points[1,1])/2
        ])
        # Offset slightly down
        self.start_loc = np.array([[p_start_center[0], p_start_center[1] - 1.0]])
        # self.start_loc is set above

        # place location markers at the desginated locations
        # place location markers at the desginated locations
        if self.wd.structure["params"]["location_markers"]:
            # Marker A: Right side middle
            p_right_mid = np.array([
                (self.boundary_points[1,0] + self.boundary_points[2,0])/2, 
                (self.boundary_points[1,1] + self.boundary_points[2,1])/2
            ])
            self.marker_a_loc = np.array([[p_right_mid[0] + 1.0, p_right_mid[1]]])

            # Marker B: Left side middle
            p_left_mid = np.array([
                (self.boundary_points[0,0] + self.boundary_points[3,0])/2, 
                (self.boundary_points[0,1] + self.boundary_points[3,1])/2
            ])
            self.marker_b_loc = np.array([[p_left_mid[0] - 1.0, p_left_mid[1]]])

            added_marker_models = [
                self.marker_models["location_marker_a"],
                self.marker_models["location_marker_b"],
            ]
        else:
            self.marker_a_loc = np.array([]).reshape(0, 2)
            self.marker_b_loc = np.array([]).reshape(0, 2)
            added_marker_models = []

        self.object_placements = np.concatenate(
            (
                self.weed_placements,
                self.pumpkin_placements,
                self.cotton_placements,
                self.litter_placements,
                self.marker_a_loc,
                self.marker_b_loc,
            )
        )

        self.object_types = [
            *random_weed_models,
            *random_pumpkin_models,
            *random_cotton_models,
            *random_litter_models,
            *added_marker_models,
        ]

    def generate_ground(self) -> None:
        ditch_depth = self.wd.structure["params"]["ground_ditch_depth"]
        ditch_distance = self.wd.structure["params"]["ground_headland"]

        self.placements = self.object_placements
        self.placements_ground_height = [0.0 for _ in self.placements]
        
        metric_x_min = self.boundary_points[:, 0].min()
        metric_x_max = self.boundary_points[:, 0].max()
        metric_y_min = self.boundary_points[:, 1].min()
        metric_y_max = self.boundary_points[:, 1].max()

        metric_width = metric_x_max - metric_x_min + 2 * ditch_distance + 1
        metric_height = metric_y_max - metric_y_min + 2 * ditch_distance + 1
        min_resolution = self.wd.structure["params"]["ground_resolution"]
        min_image_size = int(np.ceil(max(metric_width / min_resolution, metric_height / min_resolution)))
        image_size = int(2 ** np.ceil(np.log2(min_image_size))) + 1

        self.resolution = min_resolution * (min_image_size / image_size)
        self.metric_size = image_size * self.resolution
        self.heightmap_position = [0.0, 0.0]
        self.heightmap_elevation = 1.0
        
        # Here is the true flat terrain! Completely flat zeroes instead of Gaussian noise.
        self.heightmap = np.zeros((image_size, image_size), dtype=np.uint8)

    def fix_gazebo(self) -> None:
        # move the plants to the center of the flat circles
        # self.crop_placements -= self.resolution / 2
        self.object_placements -= self.resolution / 2

        # set heightmap position to origin
        self.heightmap_position = [0, 0]

    def render_to_template(self, cache_dir: str) -> None:
        def into_dict(
            xy: np.ndarray,
            ground_height: float,
            radius: float,
            height: float,
            mass: float,
            model: GazeboModel,
            index: int,
            ghost: bool = False,
        ) -> dict[str, Any]:
            coordinate = dict()
            coordinate["type"] = model.model_name
            coordinate["name"] = f"{model.model_name}_{index:04d}"
            coordinate["static"] = str(model.static).lower()

            if ghost and model.ghostable:
                coordinate["ghost"] = ghost
                coordinate["custom_visual"] = model.get_model_visual()

            # Model mass
            inertia = dict()
            inertia["ixx"] = (mass * (3 * radius**2 + height**2)) / 12.0
            inertia["iyy"] = (mass * (3 * radius**2 + height**2)) / 12.0
            inertia["izz"] = (mass * radius**2) / 2.0
            coordinate["inertia"] = inertia
            coordinate["mass"] = mass

            # Model pose
            coordinate["x"] = model.default_x + xy[0]
            coordinate["y"] = model.default_y + xy[1]
            coordinate["z"] = model.default_z + ground_height
            coordinate["roll"] = model.default_roll
            coordinate["pitch"] = model.default_pitch
            coordinate["yaw"] = model.default_yaw
            if model.random_yaw:
                coordinate["yaw"] += self.wd.rng.random() * 2.0 * np.pi

            coordinate["radius"] = (
                radius
                + (2 * self.wd.rng.random() - 1)
                * self.wd.structure["params"]["plant_radius_noise"]
            )
            if coordinate["type"] == "cylinder":
                coordinate["height"] = height

            return coordinate

        # plant crops
        # plant crops removed
        coordinates = []


        # place objects
        object_coordinates = [
            into_dict(
                plant,
                self.placements_ground_height[i] + 0.005,
                self.wd.structure["params"]["plant_radius"],
                self.wd.structure["params"]["plant_height_min"],
                self.wd.structure["params"]["plant_mass"],
                self.object_types[i],
                i,
                ghost=self.wd.structure["params"]["ghost_objects"],
            )
            for i, plant in enumerate(self.object_placements)
        ]

        # BRUTE FORCE: Always make objects static and ghost-like
        for coord in object_coordinates:
             coord["static"] = "true"
             coord["ghost"] = True


        coordinates.extend(object_coordinates)

        template = importlib.resources.read_text(
            world_generator, "field.world.template"
        )
        template = jinja2.Template(template)
        self.sdf = template.render(
            coordinates=coordinates,
            seed=self.wd.structure["params"]["seed"],
            heightmap={
                "size": self.metric_size,
                "pos": {
                    "x": self.heightmap_position[0],
                    "y": self.heightmap_position[1],
                },
                "max_elevation": self.wd.structure["params"]["ground_elevation_max"],
                "ditch_depth": self.wd.structure["params"]["ground_ditch_depth"],
                "total_height": self.heightmap_elevation,
                "cache_dir": cache_dir,
            },
        )
