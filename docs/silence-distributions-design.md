# Design: silence & floor-transfer-offset distributions for SWB-1

**Date:** 2026-07-01
**Status:** approved (pending spec review)
**Scope:** `swbd-statistics` (Switchboard-1, 2,438 conversations)

## Goal

Extend the per-conversation SWB-1 statistics pipeline
(`per_conversation_swbd.py`) from *aggregate* turn-taking numbers to the three
**distributions** the FLOOR/TURN analysis wants:

1. **Gap** — silence between one speaker's turn end and the *other* speaker's
   turn start (between-speaker, floor changes).
2. **Pause** — within-turn silence where the *same* speaker resumes (floor held).
3. **Floor-transfer offset (FTO)** — the full, **signed** distribution over every
   floor change, **including negative offsets** for overlap transitions. The
   pipeline already emits `fto_{mean,median,n}`; this adds the whole distribution.

## Definitions (grounded in the existing turn model)

The pipeline builds turns as it does today (**unchanged**): a speaker's lexical
*floor* words (backchannels excluded) merge into IPUs across gaps `≤ ipu_gap`
(0.2 s); consecutive same-speaker IPUs merge into a floor-holding **turn**; the
floor changes only when the *other* speaker takes a non-BC IPU.

For a floor change at turn *i*, `fto_i = start(turn_i) − end(turn_{i-1})`:

| Quantity | Definition | Value sign |
| --- | --- | --- |
| **FTO** | `start(next turn) − end(prev turn)`, every floor change (the existing `ftos` list) | signed |
| **Gap** | the **positive** FTOs (silence at a floor transfer) | `fto > 0` |
| **Overlap** | the **negative** FTOs (next speaker starts before prev ends) | `fto < 0` |
| **Pause** | within-turn silence between the same speaker's consecutive *floor* words, `≥ pause_min` | positive |

**Partition.** Every inter-word silence is exactly one of: *pause* (same speaker
resumes), *gap* (other speaker takes the floor, `+FTO`), or *overlap* (`−FTO`).
Gap and overlap together **are** the FTO distribution; pause is disjoint from
FTO (it is never a floor transfer).

### Worked example

```
time →   0    1    2    3    4    5    6    7    8
A:      [==A==]  [==A==]                    [==A==]
B:                          [=====B=====]
```
A `0.0–2.0`, `2.6–4.0`; B `4.8–7.0`; A `6.5–8.5`.
- Pause = `2.0→2.6` = **+0.6 s** (A resumes; floor held).
- Gap = `4.0→4.8` = **+0.8 s** (A→B transfer).
- FTO at B→A = `6.5 − 7.0` = **−0.5 s** (overlap).
- FTO distribution here = `{+0.8, −0.5}`; gap = `{+0.8}`; overlap = `{−0.5}`.

## Key resolution decision

**Gaps and FTOs are already at raw (word-alignment) resolution** — `ipu_gap`
merges silences only *within* a speaker, never flooring a between-speaker
offset, so `fto_i` is computed from raw word endpoints. The 0.2 s floor bites
**only on pauses** (a same-speaker silence `< 0.2 s` is currently absorbed into
one IPU). Therefore:

- **FTO / gap / overlap:** taken from the existing `ftos` list — turn model
  untouched, no minimum applied (small/zero/negative values are meaningful).
- **Pause:** extracted at **word resolution** with a configurable minimum
  `pause_min` (**default 0.05 s**), *decoupled* from `ipu_gap` so pauses finer
  than the IPU-merge are visible **without changing the turn model** (and hence
  without changing any existing published stat).

## Extraction

In `per_conversation_swbd.py`, behavior-preserving:

- Keep the turn model and `ftos` exactly as they are → **FTO** list;
  **gap** = `[f for f in ftos if f > 0]`, **overlap** = `[f for f in ftos if f < 0]`.
- **New pause extraction:** for each turn `[ts, te, sp]`, take speaker `sp`'s
  *floor* words (lexical, BC-excluded — the same set that builds `floor_ipus`)
  whose midpoints fall in `[ts, te]`, sort by onset, and collect
  `start(w_{k+1}) − end(w_k) ≥ pause_min` as pauses. (Within-turn by
  construction — a pause never spans a floor transfer.)
- `analyze()` returns its current scalar row **plus** the per-conversation event
  lists `{"pauses": [...], "ftos": [...]}` (gap/overlap derived by sign).

## Outputs (both raw and binned)

1. **Raw dump** — `results/swbd_silences.csv`, one row per event:
   `conversation_id, type, value_s`, with `type ∈ {pause, gap, overlap}` and
   `value_s` signed (gap `+`, overlap `−`, pause `+`). The **FTO distribution is
   `type ∈ {gap, overlap}`.** Complete, re-thresholdable downstream.
2. **Binned + summary** — `results/swbd_distributions.json`, per type
   `{pause, gap, overlap, fto}`:
   `n, mean, median, std, min, max`, quantiles `{p1,p5,p10,p25,p50,p75,p90,p95,p99}`,
   and `histogram: {bin_edges, counts}`. Bin width configurable (`--bin-width`,
   default 0.05 s); FTO on a signed range spanning its min/max.
3. **Per-conversation summaries** — extend `results/swbd_per_conversation.csv`
   with `pause_n, pause_median_s, gap_n, gap_median_s, overlap_n`
   (`fto_mean_s/fto_median_s/fto_n` already present). Preserves the
   "one Switchboard comparison row" ethos.
4. **Plots** — new `plot_distributions.py` → `results/plots/{pause,gap,fto}_hist.png`
   (FTO signed with a `0` line and the overlap region shaded; optional
   `--log-count` axis for the heavy tails). Renders from the raw dump. Adds
   `matplotlib` to `requirements.txt` (imported only by the plot script).

## Parameters

| Flag | Default | Meaning |
| --- | --- | --- |
| `--pause-min` | `0.05` | minimum same-speaker within-turn silence (s) counted as a pause |
| `--bin-width` | `0.05` | histogram bin width (s) for `swbd_distributions.json` / plots |
| `--ipu-gap` | `0.2` | **unchanged**; turn model (do not retune — keeps stats comparable) |

## Code structure

- Extend `analyze()` (small, behavior-preserving) to also return the per-conv
  event lists; add a corpus-aggregation block to the driver that writes the raw
  dump, the binned/summary JSON, and the new per-conversation columns; add a
  standalone `plot_distributions.py` that reads the raw dump. Reuse existing
  helpers (`parse_word_file`, `merge_intervals`, `build_turns`, the
  `sided`/floor-word logic). No refactor beyond exposing the pause list.
- Rationale: the distribution work is a distinct concern from the comparison
  row, but the turn/IPU derivation is already inside `analyze()`; returning the
  event lists from there (rather than re-deriving in a new module) keeps a single
  source of truth for the turn model and is the lowest-risk change.

## Verification

- **Regression:** every numeric column of the existing
  `results/swbd_per_conversation.csv` is byte-identical after the change (the
  turn model and all current stats are untouched).
- **Invariants (per conversation):** `len(gaps) + len(overlaps) == n_speaker_changes`;
  `mean(ftos) ≈ fto_mean_s`; `median(ftos) ≈ fto_median_s` (regression tie-out to
  the existing aggregate FTO).
- **Partition:** no pause interval spans a floor transfer (same-speaker,
  within-turn only); the worked example above reproduces `{pause 0.6, gap 0.8,
  overlap −0.5}`.
- Run on a 3–5 conversation subset first, then the full corpus.

## Scope & non-goals

- **In scope:** SWB-1 only (2,438 conversations); the three distributions + raw
  dump + binned summary + plots + per-conversation summary columns.
- **Out of scope (follow-up):** mirroring the same three distributions on the
  FLOOR/TURN benchmark side (`data_analysis/per_conversation.py`) for a direct
  SWBD-vs-benchmark distribution comparison. The turn/FTO model is identical
  there, so this is a straightforward later extension.
- **Not doing:** retuning `ipu_gap` or otherwise changing the turn model; BC
  subtypes; anything requiring annotation SWB-1 lacks.
