from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional
import json

RUN_METADATA: Dict[str, Any] = {}
RUN_EVENTS: List[Dict[str, Any]] = []

LOG_DIR = Path("simulation_logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)


def reset() -> None:
    RUN_METADATA.clear()
    RUN_EVENTS.clear()


def start_run(metadata: Dict[str, Any]) -> None:
    """Initialise logging for a new simulation run."""
    reset()
    RUN_METADATA.update(metadata)
    log_event("run_started", {"metadata": metadata})


def log_event(event_type: str, payload: Dict[str, Any]) -> None:
    """Append an arbitrary event payload to the log."""
    entry = {"event": event_type}
    entry.update(payload)
    RUN_EVENTS.append(entry)


def log_tick(
    *,
    turn: int,
    game_time: int,
    elapsed: int,
    scheduled_delay: int,
    passive_candidates: List[int],
    player_candidates: List[int],
) -> None:
    """Record summary information for a single scheduler tick."""
    log_event(
        "tick",
        {
            "turn": turn,
            "game_time": game_time,
            "elapsed": elapsed,
            "scheduled_delay": scheduled_delay,
            "passive_candidates": list(passive_candidates),
            "player_candidates": list(player_candidates),
        },
    )


def log_action(
    *,
    player: str,
    village_location: Optional[str],
    action_type: str,
    target: Optional[str],
    wait_time: Optional[int],
    reason: Optional[str] = None,
    population: Optional[int] = None,
    culture_rate: Optional[float] = None,
    culture_total: Optional[float] = None,
    total_yield: Optional[float] = None,
) -> None:
    """Record the action (or inaction) chosen by a controller."""
    payload: Dict[str, Any] = {
        "player": player,
        "village": village_location,
        "action_type": action_type,
        "target": target,
        "wait_time": wait_time,
    }
    if reason is not None:
        payload["reason"] = reason
    if population is not None:
        payload["population"] = population
    if culture_rate is not None:
        payload["culture_rate"] = culture_rate
    if culture_total is not None:
        payload["culture_total"] = culture_total
    if total_yield is not None:
        payload["total_yield"] = total_yield
    log_event("action", payload)


def log_completion(
    *,
    player: str,
    village_location: Optional[str],
    job_type: str,
    target: str,
    population: Optional[int] = None,
    culture_rate: Optional[float] = None,
    culture_total: Optional[float] = None,
    total_yield: Optional[float] = None,
) -> None:
    """Record completion of a queued job."""
    payload: Dict[str, Any] = {
        "player": player,
        "village": village_location,
        "job_type": job_type,
        "target": target,
    }
    if population is not None:
        payload["population"] = population
    if culture_rate is not None:
        payload["culture_rate"] = culture_rate
    if culture_total is not None:
        payload["culture_total"] = culture_total
    if total_yield is not None:
        payload["total_yield"] = total_yield
    log_event("completion", payload)


# [ISS-021] Resource snapshots are deferred until completion events are explicit.


def finalise_run(summary: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Close out the run and return the collected log."""
    # [ISS-022] scoreboard aggregation should summarise per-player/village metrics for quick reference.
    if summary is not None:
        log_event("run_summary", summary)
    payload = {"metadata": RUN_METADATA.copy(), "events": list(RUN_EVENTS)}
    _write_log_to_disk(payload)
    return payload


def _write_log_to_disk(payload: Dict[str, Any]) -> None:
    run_id = payload["metadata"].get("run_id")
    if run_id is None:
        existing = sorted(LOG_DIR.glob("run_*.json"))
        next_id = len(existing) + 1
        run_id = f"{next_id:05d}"
        payload["metadata"]["run_id"] = run_id
    log_path = LOG_DIR / f"run_{run_id}.json"
    with log_path.open("w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2)


def get_events() -> List[Dict[str, Any]]:
    """Expose a shallow copy of the accumulated events."""
    return list(RUN_EVENTS)
