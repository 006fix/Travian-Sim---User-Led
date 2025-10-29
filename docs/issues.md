# Issues Log

## 2025-10-21 13:17:02

- **ISS-001** — `Specific_Functions/map_creation.py`: Coordinate string format (`locval = [x,"/",y]`) may break downstream consumers that expect numeric pairs. Evaluate representation and adjust callers accordingly.
- **ISS-002** (resolved 2025-10-28) - `Classes/habitable.py`: `next_update` uses placeholder sleep handling and should be replaced with a proper interaction model.
- **ISS-003** (resolved 2025-10-28) - `Classes/oasis.py`: `next_update` placeholder keeps oases non-interactable; needs a cleaner mechanism.

## 2025-10-21 16:11:53

- **ISS-004** — `Classes/player.py`: `next_update` still relies on the temporary boolean sentinel approach; replace with real scheduling logic to align with the eventual event loop.

## 2025-10-25 09:44:10

- **ISS-005** (resolved 2025-10-28) - `Classes/village.py`: `possible_buildings` still depends on `len(upgrade_cost) > 1` to detect the legacy `[False]` sentinel instead of using the field's `upgradeable` flag. Swap to an explicit attribute check to decouple the helper from data-table quirks.
- **ISS-006** (resolved 2025-10-28) - `Classes/village.py`: `possible_buildings` returns building entries as `[slot_id, name]` but field entries as `[field_id]`. Normalise the payload shape (for example, tagged dicts) so consumers don't need special cases.

## 2025-10-25 14:24:49

- **ISS-007** (resolved 2025-10-28) - `Classes/village.py`: `upgrade_building` and `upgrade_field` still ignore main-building speed modifiers when converting build times; the duration helper needs to incorporate the main-building level to match Travian timing.
- **ISS-008** — `Classes/village.py`: Completion handlers (`building_upgraded`, `field_upgraded`) clear `currently_upgrading` wholesale. Replace with removal of just the finished job so Romans (or future multi-queue logic) can upgrade in parallel.
- **ISS-009** — `Classes/village.py`: `building_upgraded` relies on the `[False]` sentinel in `b_data.building_dict` to detect terminal levels; add explicit guards or helper accessors so missing entries don’t raise unexpectedly.

## 2025-10-26 12:05:00

- **ISS-015** — `Classes/AI_Classes/generic_running_mechanism.py`: Completion logic drops the first queued job but still relies on nested lists and manual length checks. Replace with a structured job record to avoid brittle indexing when Romans/multi-queue support lands.

## 2025-10-27 08:27:52

- **ISS-016** — `simulation_runner/game_state_progression.py`: `set_time_elapsed` writes a string sentinel into `time_will_elapse`; replace with a numeric default or queue-driven scheduler to avoid type churn.
- **ISS-017** — `simulation_runner/game_state_progression.py`: `check_passive` relies on `next_update()` returning `True` to mean “no event”; clarify the contract and swap to `None`/numeric values so the scheduler stays well-typed.
- **ISS-018** — `simulation_runner/game_state_progression.py`: Global state (`game_counter`, `time_will_elapse`, `global_last_active`) is mutated via module-level globals; encapsulate in a Kernel/GameState object and pass dependencies explicitly.
- **ISS-019** — `simulation_runner/game_state_progression.py`: Fallback `min_elapsed = 1` advances time even when no actors are pending; replace with a heartbeat event or guard to detect stalled simulations instead of silently ticking.
- **ISS-020** — `simulation_runner/game_state_progression.py`: No logging/metrics around tick decisions. Add structured logging once the kernel is formalised.
- **ISS-021** (resolved 2025-10-28) - `simulation_runner/run_logger.py`: Resource snapshot logging is blocked by the current "wake implies completion" assumption; revisit once upgrade completion events are explicit.

## 2025-10-28 09:15:00

- **ISS-022** - `simulation_runner/run_logger.py`: Logger emits per-event metrics but lacks aggregated per-player/per-village summaries; introduce a scoreboard view for quick post-run comparison.

## 2025-10-28 19:33:04

- **ISS-005** resolved - `Classes/village.py`: `possible_buildings` now checks the field's `upgradeable` flag instead of relying on the legacy cost sentinel.


## 2025-10-28 22:10:17

- **ISS-007** resolved - Classes/village.py: Upgrade durations now scale with the main building speed modifier (fallback multiplier 5 when unavailable).


## 2025-10-28 22:21:01

- **ISS-006** resolved - Classes/village.py: possible_buildings now emits unified dict payloads and controller logic consumes them consistently.


## 2025-10-28 23:25:05

- **ISS-021** resolved - simulation_runner/run_logger.py: Completion events now capture stored resources and storage caps alongside population and culture metrics.


## 2025-10-28 23:46:09

- **ISS-002** resolved - Classes/habitable.py: Habitable tiles are temporarily marked non-interactable; 
ext_update now returns None until active behaviour is introduced.
- **ISS-003** resolved - Classes/oasis.py: Oases are treated as passive tiles; 
ext_update returns None pending future interaction logic.


## 2025-10-28 23:59:50

- **ISS-009** resolved - Classes/village.py: Building helper guards terminal levels and consumers now use it to avoid [False] sentinel crashes.


## 2025-10-29 18:45:00

- **ISS-001** resolved - Map generation and downstream consumers now use tuple (x, y) coordinates instead of stringified lists.

