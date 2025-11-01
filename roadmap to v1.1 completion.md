# Roadmap to v1.1 Completion

Steps to deliver Settling v1 (points race) and supporting scaffolding for AI experimentation. Order chosen for smooth integration; adjust as needed.

1. Define objectives & stop condition  
   - Win rule: each completed settle job grants 1 point to the executing player.  
   - Terminate run when `global_settles_completed >= round(num_players / 10)`.  
   - Record the rule in run metadata for post-run analysis.

2. Centralise tunables  
   - Add constants (`SETTLER_COST`, `SETTLER_TIME`, `SETTLE_COST`, `SETTLE_TIME`, optional `CP_THRESHOLD`) in a single module (e.g., `game_rules.py` or `simulation_constraints`).  
   - Expose them so experiments can tweak parameters without touching core logic.

3. Extend player/global state  
   - Player: add `settlers_built` and `settle_points` counters.  
  - Global: add `global_settles_completed` counter in the simulation runner.  
   - No new village-level structures needed; leverage existing job queue.

4. Implement new job types  
   - `train_settler`: consumes settler cost, waits settler time, increments `player.settlers_built`.  
   - `settle`: requires `player.settlers_built >= 3`, consumes settle cost/time, decrements settlers by 3, increments `settle_points`, increments global counter.  
   - Add helper methods on `Village` (e.g., `start_train_settler`, `start_settle`) to enqueue these jobs via `_register_upgrade_job`.

5. Handle completions in controller loop  
   - Extend completion processing in `base_controller.will_i_act` to recognise `train_settler` and `settle`, updating player/global counters and logging completion events.  
   - Ensure multiple completions per tick remain safe (already true with structured jobs).

6. Minimal AI policy enhancements  
   - Heuristic: if `settlers_built < 3`, prioritise training settlers when resources allow; otherwise prioritise the `settle` job.  
   - Make weights configurable (single module) to allow future parameter search or GA tuning.  
   - Optionally gate on CP threshold to avoid ultra-early settlers.

7. Resource feasibility checks  
   - Use existing “enough resources” logic for both new jobs; if requirements fail, skip gracefully so normal upgrades proceed.  
   - Ensure costs deduct from the village just like other jobs.

8. Logging & monitoring updates  
   - Log new action types (`train_settler`, `settle`) and completion events (`settler_trained`, `settle_completed`) with wait times and updated counters.  
   - Periodic monitor: include `settlers_built` and `settle_points` per player (duplicated per village is acceptable for now).

9. Scoreboard & run summary enhancements  
   - Surface `settle_points` in scoreboard entries.  
   - `finalise_run`: emit winner(s), points tally, and timestamp when threshold was hit.  
   - Confirm last action type reflects settlement jobs for debugging.

10. Run loop termination hook  
    - After each tick, check the global counter relative to the threshold.  
    - If met, finalise immediately, write logs/scoreboard, and exit cleanly.

11. Optional shell buildings (cheap win)  
    - Add CP/pop-only shells (Residence, Embassy, Town Hall, etc.) to `building_dict`.  
    - Integrate into `available_buildings` so they can be constructed in empty slots (pre-req trees can wait).

12. Tests (lean but focused)  
    - Settler training consumes resources and increments `settlers_built` on completion.  
    - Settle job requires 3 settlers, decrements correctly, increments `settle_points`.  
    - Simulated global threshold ends the run and records winners in the summary.

13. (Nice-to-have) Marketplace v1  
    - Intra-player transfers only: `send_resources` job with travel time based on distance.  
    - Helps pool resources at the settlement village; sets the stage for later inter-player trade.

14. AI parameter surface  
    - Centralise settlement-related weights/toggles for easy tuning.  
    - Document defaults and expose them so future experiments/GA runs can explore the space.

15. Future-facing note  
    - Later versions can replace “settle point” with real village placement, tie settlers to Residence levels, and add richer AI coordination once v1.1 stabilises.

