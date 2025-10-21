## Rewrite Guidance Priorities

1. **Deterministic simulation plumbing.**  
   - Route all randomness through an injected RNG that is seeded once per run.  
   - Audit modules currently using `random` directly (`legacy_travian/Classes/Habitable.py`, `Specific_Functions/Village_Creation.py`, `Classes/Village.py`, etc.) and refactor them to accept an RNG parameter or deterministic inputs.  
   - Determinism makes bugs reproducible, enables regression tests, and allows comparison between legacy and rewritten outputs.

2. **Automated regression checks.**  
   - Stand up a minimal pytest suite that boots a small world, advances simulated time, and asserts invariants around resources, storage caps, and upgrade queues.  
   - Add fixtures for map generation and player/village seeding so behaviour stays locked even after refactors.  
   - Without tests you cannot trust timing, accrual math, or agent logic; small changes will silently break the simulation.

3. **Eliminate shared mutable defaults and global singletons.**  
   - Replace default arguments like `villages=[]` with constructor-time copies; pass explicit state containers instead of mutating module-level dicts.  
   - Provide a clean reset path (factory function or world object) so simulations do not leak state between runs.  
   - This prevents cross-run contamination, allows multiple simulations in one process, and keeps debugging sane.

4. **Structured logging and repo hygiene.**  
   - Swap `print` statements for the `logging` module (or a thin adapter) so you can control levels, formats, and outputs.  
   - Add project scaffolding: `.gitignore`, dependency metadata (`pyproject.toml`/`requirements.txt`), and basic run scripts.  
   - Proper logging turns playtest sessions into actionable traces; a clean repo keeps noise out of commits and onboarding painless.
