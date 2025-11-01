"""Utilities for converting structured Excel data into building dictionaries.

The Excel file is expected to expose a sheet (default: ``fixed data``) where
each row describes a single building level with the following columns:

* ``Building`` – the human readable name (e.g. ``Bakery``).
* ``lvl`` – the level index.
* ``Lumber``/``Clay``/``Iron``/``Crop`` – resource costs in the Travian order.
* ``pop`` – population cost.
* ``CP`` – culture point output.
* ``Time`` – build time in ``HH:MM:SS`` (or any pandas-compatible timedelta).
* ``Prod. increase`` (or other final metric) – the building specific value.

The resulting dictionary mirrors the structure used by
``Base_Data/Building_Data.py`` where each level entry is stored as:

``[resource_costs, culture_points, population, [days, hours, minutes], bonus]``
"""

from __future__ import annotations

import datetime as _dt

from pathlib import Path
from typing import Dict, Iterable, List, Mapping, MutableMapping, Optional

import pandas as pd

ResourceVector = List[int]
BuildTime = List[int]
LevelEntry = List[object]  # [ResourceVector, int, int, BuildTime, Any]
BuildingDict = Dict[str, Dict[int, LevelEntry]]


def _normalise_name(raw_name: str) -> str:
    """Convert the human readable building name into a dict-friendly key."""
    return raw_name.strip().lower().replace(" ", "_")


def _parse_time(value: object) -> BuildTime:
    """Convert an excel/strings duration representation to [days, hours, mins]."""
    if pd.isna(value):
        return [0, 0, 0]
    if isinstance(value, _dt.time):
        total_seconds = value.hour * 3600 + value.minute * 60 + value.second
    else:
        td = pd.to_timedelta(value)
        total_seconds = int(td.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    return [hours, minutes, seconds]


def parse_building_sheet(
    workbook: Path | str,
    sheet_name: str = "fixed data",
    *,
    name_map: Optional[Mapping[str, str]] = None,
) -> BuildingDict:
    """Parse the given Excel sheet into the building dictionary structure.

    Args:
        workbook: Path to ``Raw_Building_Data.xlsx`` (or equivalent file).
        sheet_name: Name of the worksheet that contains the building rows.
        name_map: Optional mapping to override the auto-generated keys.

    Returns:
        Dictionary suitable for merging into ``building_dict``.
    """
    df = pd.read_excel(workbook, sheet_name=sheet_name)
    expected_columns = {"Building", "lvl", "Lumber", "Clay", "Iron", "Crop", "pop", "CP", "Time"}
    missing = expected_columns - set(df.columns)
    if missing:
        raise ValueError(f"Sheet '{sheet_name}' is missing required columns: {sorted(missing)}")

    bonus_column = next(
        (col for col in df.columns if col not in expected_columns), None
    )
    if bonus_column is None:
        raise ValueError("Unable to determine the 'unique' column for building bonuses.")

    result: BuildingDict = {}
    for building_name, group in df.groupby("Building"):
        key_name = name_map.get(building_name, _normalise_name(building_name)) if name_map else _normalise_name(building_name)
        level_entries: Dict[int, LevelEntry] = {}
        for _, row in group.sort_values("lvl").iterrows():
            level = int(row["lvl"])
            resource_cost: ResourceVector = [
                int(row["Lumber"]),
                int(row["Clay"]),
                int(row["Iron"]),
                int(row["Crop"]),
            ]
            cp = int(row["CP"])
            pop = int(row["pop"])
            build_time = _parse_time(row["Time"])
            bonus = row[bonus_column]
            level_entries[level] = [resource_cost, cp, pop, build_time, bonus]
        result[key_name] = level_entries
    return result


def format_building_dict(buildings: BuildingDict) -> str:
    """Render the parsed building dict as Python source."""
    lines: List[str] = []
    for building_name in sorted(buildings.keys()):
        lines.append(f"{building_name}_dict = {{")
        for level in sorted(buildings[building_name].keys()):
            entry = buildings[building_name][level]
            resource_cost, cp, pop, time_vec, bonus = entry
            lines.append(
                f"    {level}: [{resource_cost}, {cp}, {pop}, {time_vec}, {repr(bonus)}],"
            )
        lines.append("}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


__all__ = ["parse_building_sheet", "format_building_dict"]

data = parse_building_sheet("Raw_Building_Data.xlsx")
print(format_building_dict(data))