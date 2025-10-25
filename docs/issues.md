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
