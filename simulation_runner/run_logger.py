from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional
import json

RUN_METADATA: Dict[str, Any] = {}
RUN_EVENTS: List[Dict[str, Any]] = []

LOG_DIR = Path("simulation_logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)
SCOREBOARD_DIR = LOG_DIR / "scoreboards"
SCOREBOARD_DIR.mkdir(parents=True, exist_ok=True)


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


def _serialise_location(location: Optional[Any]) -> Optional[Any]:
    if isinstance(location, tuple):
        return list(location)
    if isinstance(location, list):
        return list(location)
    return location


def log_action(
    *,
    player: str,
    village_location: Optional[Any],
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
        "village": _serialise_location(village_location),
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
    village_location: Optional[Any],
    job_type: str,
    target: str,
    population: Optional[int] = None,
    culture_rate: Optional[float] = None,
    culture_total: Optional[float] = None,
    total_yield: Optional[float] = None,
    resources: Optional[List[float]] = None,
    storage_cap: Optional[List[float]] = None,
) -> None:
    """Record completion of a queued job."""
    payload: Dict[str, Any] = {
        "player": player,
        "village": _serialise_location(village_location),
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
    if resources is not None:
        payload["resources"] = list(resources)
    if storage_cap is not None:
        payload["storage_cap"] = list(storage_cap)
    log_event("completion", payload)



def finalise_run(summary: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Close out the run and return the collected log."""
    if summary is not None:
        log_event("run_summary", summary)
    payload = {"metadata": RUN_METADATA.copy(), "events": list(RUN_EVENTS)}
    scoreboard = _build_scoreboard()
    payload["scoreboard"] = {"players": scoreboard}
    run_id = _write_log_to_disk(payload)
    scoreboard_path = _write_scoreboard_to_disk(run_id, scoreboard)
    payload["metadata"]["scoreboard_path"] = str(scoreboard_path)
    return payload


def _write_log_to_disk(payload: Dict[str, Any]) -> str:
    run_id = payload["metadata"].get("run_id")
    if run_id is None:
        existing = sorted(LOG_DIR.glob("run_*.json"))
        next_id = len(existing) + 1
        run_id = f"{next_id:05d}"
        payload["metadata"]["run_id"] = run_id
    log_path = LOG_DIR / f"run_{run_id}.json"
    with log_path.open("w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2)
    return run_id


def _write_scoreboard_to_disk(run_id: str, scoreboard: List[Dict[str, Any]]) -> Path:
    scoreboard_path = SCOREBOARD_DIR / f"scoreboard_{run_id}.json"
    payload = {"run_id": run_id, "players": scoreboard}
    with scoreboard_path.open("w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2)
    return scoreboard_path


def _build_scoreboard() -> List[Dict[str, Any]]:
    per_player: Dict[str, Dict[str, Any]] = {}
    for event in RUN_EVENTS:
        player = event.get("player")
        if player is None:
            continue
        entry = per_player.setdefault(
            player,
            {"actions": 0, "completions": 0, "last_event": None},
        )
        if event.get("event") == "action":
            entry["actions"] += 1
        elif event.get("event") == "completion":
            entry["completions"] += 1
        entry["last_event"] = event

    scoreboard: List[Dict[str, Any]] = []
    for player, stats in per_player.items():
        last_event = stats.get("last_event") or {}
        scoreboard.append(
            {
                "player": player,
                "actions": stats["actions"],
                "completions": stats["completions"],
                "population": last_event.get("population"),
                "culture_rate": last_event.get("culture_rate"),
                "culture_total": last_event.get("culture_total"),
                "total_yield": last_event.get("total_yield"),
                "resources": last_event.get("resources"),
                "storage_cap": last_event.get("storage_cap"),
                "last_village": _serialise_location(last_event.get("village")),
                "last_event_type": last_event.get("event"),
                "last_action_type": last_event.get("action_type") or last_event.get("job_type"),
                "last_target": last_event.get("target"),
                "last_wait_time": last_event.get("wait_time"),
            }
        )
    scoreboard.sort(
        key=lambda item: (
            -(item.get("population") or 0),
            -(item.get("culture_total") or 0.0),
        )
    )
    return scoreboard


def get_events() -> List[Dict[str, Any]]:
    """Expose a shallow copy of the accumulated events."""
    return list(RUN_EVENTS)
