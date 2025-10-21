# Issues Log

## 2025-10-21 13:17:02

- **ISS-001** — `Specific_Functions/map_creation.py`: Coordinate string format (`locval = [x,"/",y]`) may break downstream consumers that expect numeric pairs. Evaluate representation and adjust callers accordingly.
- **ISS-002** — `Classes/habitable.py`: `next_update` uses placeholder sleep handling and should be replaced with a proper interaction model.
- **ISS-003** — `Classes/oasis.py`: `next_update` placeholder keeps oases non-interactable; needs a cleaner mechanism.
