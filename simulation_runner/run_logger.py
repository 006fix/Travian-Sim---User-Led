from __future__ import annotations

from typing import Any, Dict, List, Optional

RUN_METADATA: Dict[str, Any] = {}
RUN_EVENTS: List[Dict[str, Any]] = []


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
    log_event("action", payload)


def log_completion(
    *,
    player: str,
    village_location: Optional[str],
    job_type: str,
    target: str,
) -> None:
    """Record completion of a queued job."""
    log_event(
        "completion",
        {
            "player": player,
            "village": village_location,
            "job_type": job_type,
            "target": target,
        },
    )


# [ISS-021] Resource snapshots are deferred until completion events are explicit.


def finalise_run(summary: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Close out the run and return the collected log."""
    if summary is not None:
        log_event("run_summary", summary)
    return {"metadata": RUN_METADATA.copy(), "events": list(RUN_EVENTS)}


def get_events() -> List[Dict[str, Any]]:
    """Expose a shallow copy of the accumulated events."""
    return list(RUN_EVENTS)
