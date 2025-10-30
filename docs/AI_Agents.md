# AI Agents Roadmap

## Legacy Line-Up
1. Generic Random - *completed* - Randomly picks any valid upgrade option; always builds when possible.
2. Field Focus - *completed* - Always upgrades a field when available (random choice); otherwise builds any available structure.
3. Field Focus - Lowest Level - *completed* - Prioritises the lowest-level field; if none, picks the lowest-level building.
4. Field Focus - Weighted Preference - Applies configurable weights across each field type and buildings before choosing.
5. Field Focus - Weighted + Lowest Level - Same weighting scheme as #4 but selects the lowest-level candidate within the preferred field type.
6. Main Building Bias - *completed* - Always upgrades the main building when possible; falls back to random choices otherwise.
7. Early Field Focus - Levels all fields to 5, then pushes the main building to 10, then switches to random.
8. Early Field Focus - Weighted - Same as #7 but uses weighted field preferences during the early phase.

## Proposed Additions
9. Building Focus - *completed* - Mirror to #2: upgrade any available building first (random or lowest-level); fall back to fields when none remain.
10. Storage First - *completed* - Hard-coded priority queue: Warehouse -> Granary -> other buildings -> fields; ensures expansion capacity before production.
11. Balanced Lowest Level - *completed* - Global equality seeker: always choose the lowest-level option across both fields and buildings, tie-breaking randomly.
12. Resource Specialist: Crop Hoarder - *completed* - Single hard-coded weighting profile that favours crop fields first, then other upgrades.
13. Resource Specialist: Wood Worker - *completed* - Prioritises wood fields heavily while allowing other upgrades when wood is capped.
14. Resource Specialist: Clay Crafter - *completed* - Clay-first variant mirroring the wood specialist.
15. Resource Specialist: Iron Miner - *completed* - Iron-first variant to cover the remaining resource bias.
16. Storage & Support Blend - *completed* - Hybrid of Storage First and Building Focus: maintain warehouses/granaries, then support buildings (e.g., Smithy, Barracks), finally fields.
