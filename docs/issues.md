# Issues Log

## 2025-10-21 13:17:02

- **ISS-001** — `Specific_Functions/map_creation.py`: Coordinate string format (`locval = [x,"/",y]`) may break downstream consumers that expect numeric pairs. Evaluate representation and adjust callers accordingly.
- **ISS-002** — `Classes/habitable.py`: `next_update` uses placeholder sleep handling and should be replaced with a proper interaction model.
- **ISS-003** — `Classes/oasis.py`: `next_update` placeholder keeps oases non-interactable; needs a cleaner mechanism.

## 2025-10-21 16:11:53

- **ISS-004** — `Classes/player.py`: `next_update` still relies on the temporary boolean sentinel approach; replace with real scheduling logic to align with the eventual event loop.

## 2025-10-25 09:44:10

- **ISS-005** — `Classes/village.py`: `possible_buildings` still depends on `len(upgrade_cost) > 1` to detect the legacy `[False]` sentinel instead of using the field’s `upgradeable` flag. Swap to an explicit attribute check to decouple the helper from data-table quirks.
- **ISS-006** — `Classes/village.py`: `possible_buildings` returns building entries as `[slot_id, name]` but field entries as `[field_id]`. Normalise the payload shape (for example, tagged dicts) so consumers don’t need special cases.

## 2025-10-25 14:24:49

- **ISS-007** — `Classes/village.py`: `upgrade_building` and `upgrade_field` still ignore main-building speed modifiers when converting build times; the duration helper needs to incorporate the main-building level to match Travian timing.
- **ISS-008** — `Classes/village.py`: Completion handlers (`building_upgraded`, `field_upgraded`) clear `currently_upgrading` wholesale. Replace with removal of just the finished job so Romans (or future multi-queue logic) can upgrade in parallel.
- **ISS-009** — `Classes/village.py`: `building_upgraded` relies on the `[False]` sentinel in `b_data.building_dict` to detect terminal levels; add explicit guards or helper accessors so missing entries don’t raise unexpectedly.
