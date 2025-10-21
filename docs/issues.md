# Issues Log

## 2025-10-21 13:17:02

- **ISS-001** — `Specific_Functions/map_creation.py`: Coordinate string format (`locval = [x,"/",y]`) may break downstream consumers that expect numeric pairs. Evaluate representation and adjust callers accordingly.
- **ISS-002** — `Classes/habitable.py`: `next_update` uses placeholder sleep handling and should be replaced with a proper interaction model.
- **ISS-003** — `Classes/oasis.py`: `next_update` placeholder keeps oases non-interactable; needs a cleaner mechanism.

## 2025-10-21 16:11:53

- **ISS-004** — `Classes/player.py`: `next_update` still relies on the temporary boolean sentinel approach; replace with real scheduling logic to align with the eventual event loop.
