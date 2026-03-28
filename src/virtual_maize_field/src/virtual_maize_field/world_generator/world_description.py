#!/usr/bin/env python3
from __future__ import annotations

from argparse import ArgumentError
from datetime import datetime
from json import dump, dumps, load

import numpy as np

from virtual_maize_field.world_generator.models import (
    AVAILABLE_MODELS,
    COTTON_MODELS,
    LITTER_MODELS,
    OBSTACLE_MODELS,
    LITTER_MODELS,
    OBSTACLE_MODELS,
    PUMPKIN_MODELS,
    WEED_MODELS,
)

AVAILABLE_ILANDS = []


class WorldDescription:
    def __init__(
        self,
        row_length: float = 12.0,
        ground_resolution: float = 0.02,
        ground_elevation_max: float = 0.2,
        ground_headland: float = 2.0,
        ground_ditch_depth: float = 0.3,
        plant_spacing_min: float = 0.13,
        plant_spacing_max: float = 0.19,
        plant_height_min: float = 0.3,
        plant_height_max: float = 0.6,
        plant_radius: float = 0.3,
        plant_radius_noise: float = 0.05,
        plant_placement_error_max: float = 0.02,
        plant_mass: float = 0.3,
        litters: int = 5,
        litter_types: list[str] = list(LITTER_MODELS.keys()),
        weeds: int = 50,
        weed_types: list[str] = list(WEED_MODELS.keys()),
        pumpkins: int = 0,
        pumpkin_types: list[str] = list(PUMPKIN_MODELS.keys()),
        cottons: int = 0,
        cotton_types: list[str] = list(COTTON_MODELS.keys()),
        ghost_objects: bool = False,
        location_markers: bool = False,
        load_from_file: str | None = None,
        seed: int = -1,
        **kwargs,
    ) -> None:
        litter_types = self.unpack_model_types(litter_types)
        weed_types = self.unpack_model_types(weed_types)
        pumpkin_types = self.unpack_model_types(pumpkin_types)
        cotton_types = self.unpack_model_types(cotton_types)

        if seed == -1:
            seed = int(datetime.now().timestamp() * 1000) % 8192

        for k, v in locals().items():
            self.__setattr__(k, v)

        self.rng = np.random.default_rng(seed)

        if self.load_from_file is not None:
            self.load()
        else:
            self.random_description()

    def unpack_model_types(self, model_types: list[str]) -> list[str]:
        for mt in model_types:
            if mt not in AVAILABLE_MODELS:
                raise ArgumentError(None, f"Error: Gazebo model {mt} is not valid!")
        return model_types

    def random_description(self) -> None:
        self.structure = dict()
        self.structure["params"] = {
            "ground_resolution": self.ground_resolution,
            "ground_elevation_max": self.ground_elevation_max,
            "ground_headland": self.ground_headland,
            "ground_ditch_depth": self.ground_ditch_depth,
            "plant_spacing_min": self.plant_spacing_min,
            "plant_spacing_max": self.plant_spacing_max,
            "plant_height_min": self.plant_height_min,
            "plant_height_max": self.plant_height_max,
            "plant_radius": self.plant_radius,
            "plant_radius_noise": self.plant_radius_noise,
            "plant_placement_error_max": self.plant_placement_error_max,
            "plant_mass": self.plant_mass,
            "litter_types": self.litter_types,
            "litters": self.litters,
            "weed_types": self.weed_types,
            "weeds": self.weeds,
            "pumpkin_types": self.pumpkin_types,
            "pumpkins": self.pumpkins,
            "cotton_types": self.cotton_types,
            "cottons": self.cottons,
            "ghost_objects": self.ghost_objects,
            "location_markers": self.location_markers,
            "seed": self.seed,
        }
        
        # Segments list is empty as we don't use it anymore
        self.structure["segments"] = []

    def __str__(self) -> str:
        return dumps(self.structure, indent=2)

    def load(self) -> None:
        self.structure = load(open(self.load_from_file))

    def save(self, path: str) -> None:
        dump(self.structure, open(path, "w"), indent=2)


if __name__ == "__main__":
    from world_generator.utils import parser_from_function

    parser = parser_from_function(WorldDescription.__init__)

    # get a dict representation of the arguments and call our constructor with them as kwargs
    args = vars(parser.parse_args())
    args = {k: v for k, v in args.items() if v is not None}
    pk = WorldDescription(**args)

    print(pk)
