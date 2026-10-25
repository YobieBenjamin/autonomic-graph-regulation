# EXPERIMENT-REALTIME-RACE specification notes (committed before any EXPERIMENT-REALTIME-RACE monitor run or analysis)

Details the pre-registration left open, fixed now:
1. **Prefix construction.** Prefix at checkpoint f = first floor(f * final_start) generated tokens, obtained by
   re-tokenizing the recorded generation text (token boundaries may differ slightly from generation time).
2. **EXPERIMENT-SELF-CONSISTENCY-MONITOR at a prefix.** The eventual answer is unknown at the checkpoint, so EXPERIMENT-SELF-CONSISTENCY-MONITOR's prefix score = 1 if its 2 continuations
   (temperature 0.8, fixed seeds) reach different final answers, else 0.
3. **EXPERIMENT-LLM-JUDGE-MONITOR at a prefix.** gpt-oss-120b sees the question and the unfinished reasoning; outputs P(eventual answer wrong).
4. **Quiet machine for timing.** EXPERIMENT-LLM-JUDGE-MONITOR runs alone (patient and recorder idle), then EXPERIMENT-SELF-CONSISTENCY-MONITOR runs alone with the 120b unloaded,
   so measured compute times are not inflated by other work. Timings come from this M4 Max (128 GB); a hardware
   biobrain or a faster serving stack would change absolute numbers for every monitor.
5. **Clock.** The deadline and checkpoint times use the per-token wall-clock latencies of the original seed-1 recording.
6. **Organism compute time** is measured at analysis time (scoring each prefix) and added in the same way.
