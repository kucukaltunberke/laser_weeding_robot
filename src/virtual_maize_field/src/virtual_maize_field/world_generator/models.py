from __future__ import annotations

import re
from dataclasses import dataclass, fields
from pathlib import Path
from xml.etree import ElementTree

VIRTUAL_MAIZE_FIELD_MODELS_FOLDER = models_folder = Path(__file__).parents[3] / "models"


@dataclass
class GazeboModel:
    model_name: str = "maize_01"
    default_x: float = 0.0
    default_y: float = 0.0
    default_z: float = 0.0
    default_roll: float = 0.0
    default_pitch: float = 0.0
    default_yaw: float = 0.0
    static: bool = False
    ghostable: bool = True
    random_yaw: bool = True

    __model_visual: str | None = None

    def get_model_visual(self) -> str:
        if self.__model_visual is None:
            model_folder = VIRTUAL_MAIZE_FIELD_MODELS_FOLDER / self.model_name
            assert model_folder.is_dir(), f"Cannot find model {self.model_name}!"

            root = ElementTree.parse(model_folder / "model.sdf").getroot()

            self.__model_visual = ""
            for visual in root.findall(".//visual"):
                self.__model_visual += ElementTree.tostring(visual).decode("utf-8")

        return self.__model_visual

    def __repr__(self) -> str:
        return f"GazeboModel: {self.model_name}"





def to_gazebo_models(
    models: dict[str, GazeboModel],
    model_names: list[str],
) -> dict[str, GazeboModel]:
    """
    Converts dict of different types of Gazebo models to dict with only Gazebo models.
    """
    output_dict = {}

    for model_name, model in models.items():
        if model_name in model_names:
            if isinstance(model, GazeboModel):
                output_dict[model.model_name] = model

            else:
                print(f"ERROR: unknown instance {type(model)}!")

    return output_dict




WEED_MODELS = {
    "weed1": GazeboModel(model_name="weed1"),
    "weed2": GazeboModel(model_name="weed2"),
    "weed3": GazeboModel(model_name="weed3"),
    "weed4": GazeboModel(model_name="weed4"),
    "weed5": GazeboModel(model_name="weed5"),
    "weed6": GazeboModel(model_name="weed6"),
}

PUMPKIN_MODELS = {
    "pumpkin1": GazeboModel(model_name="pumpkin1"),
    "pumpkin2": GazeboModel(model_name="pumpkin2"),
    "pumpkin3": GazeboModel(model_name="pumpkin3"),
    "pumpkin4": GazeboModel(model_name="pumpkin4"),
    "pumpkin5": GazeboModel(model_name="pumpkin5"),
}

COTTON_MODELS = {
    "cotton1": GazeboModel(model_name="cotton1"),
    "cotton2": GazeboModel(model_name="cotton2"),
    "cotton3": GazeboModel(model_name="cotton3"),
    "cotton4": GazeboModel(model_name="cotton4"),
    "cotton5": GazeboModel(model_name="cotton5"),
    "cotton6": GazeboModel(model_name="cotton6"),
}

LITTER_MODELS = {
    "ale": GazeboModel(model_name="ale", default_roll=1.5707963267948966),
    "beer": GazeboModel(model_name="beer", default_roll=1.5707963267948966),
    "coke_can": GazeboModel(
        model_name="coke_can", default_roll=1.5707963267948966, default_z=0.025
    ),
    "retro_pepsi_can": GazeboModel(
        model_name="retro_pepsi_can",
        default_roll=1.5707963267948966,
        default_z=0.025,
    ),
}

OBSTACLE_MODELS = {
    "box": GazeboModel(model_name="box"),
    "stone_01": GazeboModel(model_name="stone_01"),
    "stone_02": GazeboModel(model_name="stone_02"),
}

MARKER_MODELS = {
    "location_marker_a": GazeboModel(
        model_name="location_marker_a", static=True, ghostable=False, random_yaw=False
    ),
    "location_marker_b": GazeboModel(
        model_name="location_marker_b", static=True, ghostable=False, random_yaw=False
    ),
}

AVAILABLE_MODELS = {
    **WEED_MODELS,
    **PUMPKIN_MODELS,
    **COTTON_MODELS,
    **LITTER_MODELS,
    **OBSTACLE_MODELS,
    **MARKER_MODELS,
}
