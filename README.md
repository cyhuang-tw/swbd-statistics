# swbd-statistics

Per-conversation **turn-taking statistics for Switchboard-1** (LDC97S62), computed in the
metric schema of the FLOOR / TURN benchmark (CMU Sesame, `cmu-sesame/tt-benchmark`,
`data_analysis/per_conversation.py`). The goal is a single **Switchboard** comparison row
that drops in next to the benchmark's per-conversation-type rows.

Switchboard is a **single conversational register** (telephone, strangers, assigned topic)
and is **single-annotator**, so it contributes **one aggregate row** (not a per-type
breakdown) and all multi-annotator IAA columns are omitted.

FLOOR's metrics come from human-labeled turn-taking events; Switchboard has none, so every
event here is a **derived analog** built from data SWBD *does* have — MS-State word
alignments, a backchannel list, and dialog-act tags. The `Status` column below says how
comparable each number is. Full definitions and caveats: [`docs/RESULTS_EXPLAINED.md`](docs/RESULTS_EXPLAINED.md).

## Results (means over all 2,438 conversations — except `question_rate_per_min`, over 1,155; see Coverage)

| Metric | Mean | Status | How it's derived on SWBD |
| --- | ---: | --- | --- |
| `duration_min` | 6.378 | exact‑ish | last word-end time ÷ 60 |
| `n_events_mean` | 116.6 | composite | turns + BC + overlaps + laughter + non-content |
| `event_rate_per_min` | 18.464 | composite | `n_events` ÷ min |
| `word_rate_wpm` | 197.562 | **exact** | MS-State lexical words ÷ min (both speakers) |
| `words_sp1` / `words_sp2` | 641.2 / 624.6 | **exact** | per-channel word counts |
| `wpm_sp1` / `wpm_sp2` | 99.9 / 97.7 | **exact** | per-channel words ÷ min |
| `ttr_sp1` / `ttr_sp2` | 0.386 / 0.389 | **exact** | unique ÷ total words (type-token ratio) |
| `silence_ratio` | 0.177 | analog | 1 − union(non-silence tokens) ÷ dur |
| `turn_count` | 50.288 | analog | floor-holding turns (same-spk IPUs merged, BC excluded) |
| `turn_dur_mean` / `_median` / `_std` | 9.42 / 4.43 / 11.92 | analog | turn-length distribution (s) |
| `n_speaker_changes` | 49.288 | analog | floor hand-offs (= `turn_count` − 1) |
| `fto_mean_s` / `fto_median_s` | 0.069 / 0.127 | analog | floor-transfer offset: start(next) − end(prev) |
| `fto_n` | 49.288 | analog | number of speaker changes |
| `speaker_balance` | 0.504 | analog | voiced(A) ÷ (voiced A + voiced B) |
| `bc_rate_per_min` | 3.897 | analog | VAP/Ekstedt backchannels ÷ min |
| `bc_{ack,cont,react}_per_min` | — | n/a | BC subtypes unavailable on SWBD |
| `int_rate_per_min` | 0.862 | **approx** | overlap-based interruption heuristic |
| `int_{competitive,cooperative}_per_min` | — | n/a | INT subtypes unavailable on SWBD |
| `int_floor_taking_per_min` | 0.814 | **approx** | speaker change overlapping prev turn > `trp-tol` |
| `int_non_floor_per_min` | 0.048 | **approx** | overlap (not at a change) onset > `trp-tol` before incumbent end |
| `overlap_count_per_min` | 3.609 | analog | both-channel floor-speech intersection ÷ min |
| `overlap_dur_s` | 9.366 | analog | total overlap duration per call |
| `laughter_rate_per_min` | 1.442 | analog | `[laughter]` tokens ÷ min |
| `non_content_ratio` | 0.013 | analog | (`[noise]` + `[vocalized-noise]`) dur ÷ dur |
| `question_rate_per_min` | 1.306 | **approx** | SWDA question dialog acts ÷ min (1,155-conv subset) |

`Status`: **exact** = same formula & input as FLOOR · **analog** = same phenomenon,
reconstructed from word timings/lists · **approx** = heuristic for something SWBD can't
recover (footnote it) · **composite** = a sum defined here · **n/a** = no SWBD information.
Medians, ranges, and the full per-metric explanation are in
[`docs/RESULTS_EXPLAINED.md`](docs/RESULTS_EXPLAINED.md); the drop-in row is
[`results/swbd_per_type_aggregate.csv`](results/swbd_per_type_aggregate.csv).

> **Coverage.** Every column is a mean over all **2,438** conversations **except
> `question_rate_per_min`**, which is over the **1,155** conversations annotated by the
> Switchboard Dialog Act corpus (SWDA) — the other 1,283 carry no dialog-act tags and
> cannot be scored for questions. The aggregate CSV's single `n_conversations = 2438`
> therefore does **not** apply to that one column. The SWDA subset tracks the full corpus
> within a few percent on every metric measurable on both halves, skewing only marginally
> more interactive (+2–4% turns / interruptions / events), so `1.306` is if anything a
> slight **over-estimate** of the full-corpus question rate. (`backchannels.csv` covers
> 2,436/2,438; the 2 absent sessions contribute 0 to `bc_rate`.)

Sanity signals: FTO ≈ 0.07 s (human transitions cluster near zero), speaker balance ≈ 0.50
(balanced dyads), durations 5–10 min, ≈198 combined WPM.

## Layout

```
per_conversation_swbd.py        the analysis script (stdlib + numpy)
backchannels.csv                VAP/Ekstedt SWBD backchannel list (input; see Data)
results/
  swbd_per_type_aggregate.csv   the single Switchboard comparison row
  swbd_per_conversation.csv     one row per conversation (2,438 rows)
  swbd_per_type_aggregate.json  mean/median/std/min/max/n per metric
docs/
  RESULTS_EXPLAINED.md          results table + per-metric reference + status legend
scripts/
  fetch_backchannels.sh         (re)download backchannels.csv from its source
```

## Setup

```bash
pip install -r requirements.txt        # numpy only; Python >= 3.8, no GPU
```

## Data prerequisites

| Data | Needed for | Where to get it |
| --- | --- | --- |
| **MS-State word alignments** `swb_ms98_transcriptions/` | everything | LDC97S62 `transcriptions/`, or the ISIP/MS-State `switchboard_word_alignments.tar.gz`. Layout: `<root>/<2-digit>/<session>/sw<session>{A,B}-ms98-a-word.text` |
| **`backchannels.csv`** | backchannel rate | included in this repo (from [ErikEkstedt/VoiceActivityProjection](https://github.com/ErikEkstedt/VoiceActivityProjection) `dataset_swb/`); or run `scripts/fetch_backchannels.sh` |
| **SWDA** `*.utt.csv` | question rate only | [cgpotts/swda](https://github.com/cgpotts/swda) (python-swda). Optional — pass `--swda-root ''` to skip |

## Run

```bash
python per_conversation_swbd.py \
    --trans-root /path/to/swb_ms98_transcriptions \
    --backchannels backchannels.csv \
    --swda-root   /path/to/swda \
    --out-dir     results
# ~4 min, CPU only (I/O-bound on the transcript reads)
```

Knobs (defaults shown): `--ipu-gap 0.2` (merge a speaker's own words into an IPU across
≤ this gap, seconds) and `--trp-tol 1.0` (interruption onset window, seconds). Omit
`--swda-root` data and `question_rate_per_min` is simply left blank.

The committed `results/` were produced on the Delta cluster with
`--trans-root …/LDC97S62/transcriptions/swb_ms98_transcriptions`,
`--swda-root …/swda_data/swda`, default knobs.

## How a FLOOR metric maps onto Switchboard (summary)

* **exact** (`word_rate_wpm`, `words_sp*`, `wpm_sp*`, `ttr_sp*`) — identical formula; FLOOR
  averages over 3 annotator transcripts, SWBD has one.
* **analog** (silence, turns, FTO, speaker balance, overlap, laughter, non-content,
  backchannels) — the same phenomenon, but events are reconstructed from MS-State word
  timings or read from the VAP backchannel list rather than hand-labeled. A turn = a
  floor-holding stretch (a speaker's IPUs merged across the listener's backchannels);
  overlap = both channels' floor speech intersecting (backchannels excluded).
* **approx** (`int_*`, `question_rate_per_min`) — heuristics for things SWBD never recorded:
  interruption (FLOOR needs a non-TRP onset + cooperative/competitive judgment; here it's an
  overlap-with-floor-change proxy that likely **over-counts**) and questions (MS-State text
  has no punctuation, so question acts come from SWDA's dialog tags, on the 1,155-conv subset
  SWDA covers).
* **omitted** — `iaa_*`, `event_count_cv_abc`, `boundary_f1_*` measure inter-annotator
  agreement, undefined for a single-annotator corpus.

See [`docs/RESULTS_EXPLAINED.md`](docs/RESULTS_EXPLAINED.md) for the per-metric detail and
the exact heuristics.

## Data sources & citations

- **Switchboard-1** (LDC97S62): Godfrey, Holliman & McDaniel, *SWITCHBOARD: Telephone speech
  corpus for research and development*, ICASSP 1992.
- **MS-State / ISIP word alignments** (`swb_ms98_transcriptions`): Mississippi State
  University ISIP Switchboard transcription/resegmentation project, 1998.
- **Backchannel list** (`backchannels.csv`): Ekstedt & Skantze, *Voice Activity Projection:
  Self-supervised Learning of Turn-taking Events*, Interspeech 2022 — file from
  `ErikEkstedt/VoiceActivityProjection`.
- **Switchboard Dialog Act corpus (SWDA)**: Jurafsky, Shriberg & Biasca, *SWBD-DAMSL
  Coders Manual*, 1997; Stolcke et al., *Dialogue act modeling…*, Computational Linguistics
  2000; `.utt.csv` distribution via `cgpotts/swda`.
- **FLOOR / TURN benchmark** schema: CMU Sesame, `cmu-sesame/tt-benchmark`.
