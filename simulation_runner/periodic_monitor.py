from __future__ import annotations

from pathlib import Path
from typing import Dict, Iterable, List, Optional, Set, Tuple

SNAPSHOT_INTERVAL_DEFAULT = 900  # seconds

_snapshots: List[Dict[str, object]] = []
_snapshot_interval: int = SNAPSHOT_INTERVAL_DEFAULT
_next_snapshot_due: Optional[int] = None
_current_variant: Optional[str] = None
_current_metadata: Dict[str, object] = {}
_snapshot_keys: Set[Tuple[object, object, object]] = set()


def reset(interval: int = SNAPSHOT_INTERVAL_DEFAULT, variant: Optional[str] = None, metadata: Optional[Dict[str, object]] = None) -> None:
    """Prepare snapshot storage for a new simulation run."""
    global _snapshots, _snapshot_interval, _next_snapshot_due, _current_variant, _current_metadata, _snapshot_keys
    _snapshots = []
    _snapshot_interval = max(1, int(interval))
    _next_snapshot_due = _snapshot_interval
    _current_variant = variant
    _current_metadata = metadata or {}
    _snapshot_keys.clear()


def _iter_villages(player_dict: Dict[str, object]):
    """Yield (controller, player, ai_label, village) tuples from the controller dictionary."""
    for controller in player_dict.values():
        ai_label = getattr(controller, "ai_label", "Unknown")
        player_name = getattr(controller, "name", None)
        villages = getattr(controller, "villages", [])
        for village in villages:
            yield controller, player_name, ai_label, village


def _serialise_village_record(player_name: str, ai_label: str, village, game_time: int, controller: Optional[object] = None) -> Dict[str, object]:
    """Convert a single village state into a snapshot record."""
    stored = list(getattr(village, "stored", [0, 0, 0, 0]))
    location = getattr(village, "location", None)
    population = getattr(village, "population", 0)
    culture_total = getattr(village, "culture_points_total", 0.0)
    culture_rate = getattr(village, "culture_points_rate", 0.0)
    total_yield = getattr(village, "total_yield", 0.0)
    try:
        yield_values = list(village.yield_calc())
    except Exception:  # pragma: no cover - defensive; yield_calc should not raise.
        yield_values = [0.0, 0.0, 0.0, 0.0]
    # convert per-second yield to per-hour for readability
    wood_yield = yield_values[0] * 3600 if len(yield_values) > 0 else 0.0
    clay_yield = yield_values[1] * 3600 if len(yield_values) > 1 else 0.0
    iron_yield = yield_values[2] * 3600 if len(yield_values) > 2 else 0.0
    crop_yield = yield_values[3] * 3600 if len(yield_values) > 3 else 0.0
    crop_stock = stored[3] if len(stored) > 3 else 0.0
    controller_ref = controller or getattr(village, "owner", None)
    settlers_built = getattr(controller_ref, "settlers_built", 0)
    settle_points = getattr(controller_ref, "settle_points", 0)
    return {
        "time": int(game_time),
        "minutes": game_time / 60.0,
        "player": player_name,
        "ai_label": ai_label,
        "village_location": location,
        "wood_yield": wood_yield,
        "clay_yield": clay_yield,
        "iron_yield": iron_yield,
        "crop_yield": crop_yield,
        "crop_stock": crop_stock,
        "population": population,
        "total_yield": total_yield,
        "culture_total": culture_total,
        "culture_rate": culture_rate,
        "settlers_built": settlers_built,
        "settle_points": settle_points,
        "run_variant": _current_variant,
        **_current_metadata,
    }


def capture_snapshot(game_time: int, player_dict: Dict[str, object]) -> None:
    """Persist the current village state for every controller."""
    for controller, player_name, ai_label, village in _iter_villages(player_dict):
        location = getattr(village, "location", None)
        key = (game_time, player_name, location)
        if key in _snapshot_keys:
            continue
        _snapshot_keys.add(key)
        _snapshots.append(_serialise_village_record(player_name, ai_label, village, game_time, controller))


def capture_initial(game_time: int, player_dict: Dict[str, object]) -> None:
    """Take an initial snapshot before the first tick."""
    capture_snapshot(game_time, player_dict)


def maybe_capture(game_time: int, player_dict: Dict[str, object]) -> None:
    """Record snapshots whenever the scheduled boundary has been reached."""
    global _next_snapshot_due
    if _next_snapshot_due is None:
        return
    while game_time >= _next_snapshot_due:
        capture_snapshot(_next_snapshot_due, player_dict)
        _next_snapshot_due += _snapshot_interval


def final_capture(game_time: int, player_dict: Dict[str, object]) -> None:
    """Force a final snapshot regardless of schedule."""
    capture_snapshot(game_time, player_dict)


def seconds_until_next_snapshot(game_time: int) -> Optional[int]:
    """Return seconds remaining until the next scheduled snapshot."""
    if _next_snapshot_due is None:
        return None
    delta = _next_snapshot_due - game_time
    if delta <= 0:
        return 0
    return delta


def get_snapshots() -> List[Dict[str, object]]:
    """Expose a shallow copy of the collected records."""
    return list(_snapshots)


def export_results(run_id: str, output_label: str, output_dir: Optional[Path] = None):
    """Write snapshot and aggregate data frames to disk and emit charts."""
    if not _snapshots:
        return None, None

    try:
        import pandas as pd  # type: ignore
    except ImportError:  # pragma: no cover - optional dependency
        raise RuntimeError("pandas is required to export monitoring snapshots.") from None

    df = pd.DataFrame(_snapshots)

    metrics = [
        "wood_yield",
        "clay_yield",
        "iron_yield",
        "crop_yield",
        "crop_stock",
        "total_yield",
        "population",
        "culture_total",
        "culture_rate",
        "settlers_built",
        "settle_points",
    ]
    grouped = (
        df.groupby(["run_variant", "ai_label", "time"])[metrics]
        .agg(["max", "min", "mean"])
        .reset_index()
    )
    flat_columns: List[str] = []
    for col in grouped.columns:
        if isinstance(col, tuple):
            pieces = [str(part) for part in col if part]
            flat_columns.append("_".join(pieces))
        else:
            flat_columns.append(str(col))
    grouped.columns = flat_columns

    reshaped_rows = []
    for _, row in grouped.iterrows():
        run_variant = row["run_variant"]
        ai_label = row["ai_label"]
        time_value = row["time"]
        for metric in metrics:
            reshaped_rows.append(
                {
                    "run_variant": run_variant,
                    "ai_label": ai_label,
                    "time": time_value,
                    "minutes": time_value / 60.0,
                    "metric": metric,
                    "best": row[f"{metric}_max"],
                    "worst": row[f"{metric}_min"],
                    "average": row[f"{metric}_mean"],
                }
            )
    aggregated = pd.DataFrame(reshaped_rows)

    if output_dir is None:
        output_dir = Path("simulation_logs") / "monitoring"
    output_dir.mkdir(parents=True, exist_ok=True)
    run_dir = output_dir / f"run_{run_id}_{output_label}"
    run_dir.mkdir(parents=True, exist_ok=True)

    df.to_csv(run_dir / "snapshots.csv", index=False)
    aggregated.to_csv(run_dir / "aggregated.csv", index=False)

    try:
        import matplotlib.pyplot as plt  # type: ignore

        plt.switch_backend("Agg")
        for metric in metrics:
            metric_df = aggregated[aggregated["metric"] == metric]
            if metric_df.empty:
                continue
            fig, ax = plt.subplots(figsize=(10, 6))
            for ai_label, series in metric_df.groupby("ai_label"):
                series = series.sort_values("minutes")
                ax.plot(series["minutes"], series["average"], label=f"{ai_label} avg")
                ax.fill_between(
                    series["minutes"],
                    series["worst"],
                    series["best"],
                    alpha=0.15,
                    label=f"{ai_label} range"
                )
            ax.set_title(f"{metric.replace('_', ' ').title()} per 15-minute interval")
            ax.set_xlabel("Time (minutes)")
            ax.set_ylabel(metric.replace("_", " ").title())
            ax.legend(loc="upper left", fontsize="small", ncol=2)
            ax.grid(True, linestyle="--", linewidth=0.5, alpha=0.5)
            fig.tight_layout()
            fig.savefig(run_dir / f"{metric}_trend.png")
            plt.close(fig)
    except ImportError:  # pragma: no cover - optional plotting
        pass

    return df, aggregated
