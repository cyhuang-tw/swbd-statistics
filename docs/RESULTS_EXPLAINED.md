# Switchboard turn-taking statistics — results & metric reference

Per-conversation turn-taking metrics for **Switchboard-1 (LDC97S62)**, aggregated to a
single **Switchboard** row in the schema of the FLOOR / TURN benchmark
(`data_analysis/per_conversation.py` → `stats_out/per_type_aggregate.csv`).

- **n = 2,438** conversations (whole SWB-1); single aggregate row (SWBD is one register).
- Parameters: `--ipu-gap 0.2 s`, `--trp-tol 1.0 s`.
- Multi-annotator **IAA columns are omitted** (SWBD is single-annotator).
- Reproduce: `python per_conversation_swbd.py` (≈4 min, CPU only). See the repo `README.md`.

## Why the "status" column exists

FLOOR's metrics are computed from **humans hand-labeling turn-taking events** (Normal
Turn, Backchannel, Interruption, Overlap, …). Switchboard has **no such labels** — only
word-level time-aligned transcripts (who said which word, when), an external backchannel
list, and dialog-act tags for a subset. For each metric I either compute it the same way
FLOOR does, or I **reconstruct the events** from word timings. The status tag says how
much reconstruction/assumption is baked in, i.e. how comparable the number is to FLOOR.

| Status | Meaning | Comparable to FLOOR? |
| --- | --- | --- |
| **exact** | Identical formula and same kind of input (words + times). | Yes — same number. |
| **exact‑ish** | Exact, with one harmless input swap (duration from transcript span, not the WAV). | Yes. |
| **analog** | Same phenomenon, but events are **derived from word timings / an external list** instead of hand-annotated. Principled, but a human on the same audio might give a somewhat different absolute value. | In spirit / for ranking — scale not guaranteed identical. |
| **approx** | A heuristic stands in for something SWBD **cannot recover** (TRP-based interruption; "?" questions). Definition diverges in a way that can bias it. | No — footnote it. |
| **composite** | Not a single FLOOR event type; a sum I defined to fill the column. | Depends on the definition. |
| **n/a** | SWBD has no information to compute it (the subtype breakdowns); left blank. | — |
| **omitted** | Inter-annotator-agreement columns; not computed (single annotator). | — |

Quick intuition: **needs only words+times → exact; needs turn-taking events I can
reconstruct → analog; needs a human judgment SWBD never recorded → approx.**

## Results

Channel mapping: **sp1 = telephone channel A, sp2 = channel B**. Rates are per minute of
the whole call (both speakers, silence included). Min–Max is the per-conversation range.

| Metric | Mean | Median | Min–Max | Status | Meaning |
| --- | ---: | ---: | :--- | --- | --- |
| `duration_min` | 6.378 | 4.992 | 0.85 – 10.03 | exact‑ish | call length (minutes) |
| `n_events_mean` | 116.6 | 105.0 | 12 – 380 | composite | # turn-taking events (turns+BC+overlap+laughter+non-content) |
| `event_rate_per_min` | 18.464 | 17.5 | 3.4 – 54.1 | composite | events per minute |
| `word_rate_wpm` | 197.562 | 196.66 | 111.9 – 292.8 | **exact** | total words / min (both speakers) |
| `words_sp1` | 641.2 | 564.0 | 53 – 2132 | **exact** | word count, channel A |
| `words_sp2` | 624.6 | 560.0 | 18 – 1849 | **exact** | word count, channel B |
| `wpm_sp1` | 99.903 | 98.38 | 18.6 – 213.2 | **exact** | words / min, channel A |
| `wpm_sp2` | 97.659 | 96.66 | 15.8 – 195.5 | **exact** | words / min, channel B |
| `ttr_sp1` | 0.386 | 0.384 | 0.23 – 0.79 | **exact** | type-token ratio (lexical diversity), A |
| `ttr_sp2` | 0.389 | 0.386 | 0.22 – 0.89 | **exact** | type-token ratio, B |
| `silence_ratio` | 0.177 | 0.174 | 0.03 – 0.50 | analog | fraction of call with neither speaker active |
| `turn_count` | 50.288 | 45.0 | 3 – 171 | analog | # floor-holding turns |
| `turn_dur_mean` | 9.416 | 7.92 | 2.3 – 98.1 | analog | mean turn length (s) |
| `turn_dur_median` | 4.426 | 3.154 | 0.76 – 104.3 | analog | median turn length (s) |
| `turn_dur_std` | 11.921 | 10.366 | 2.3 – 65.8 | analog | within-call SD of turn length (s) |
| `n_speaker_changes` | 49.288 | 44.0 | 2 – 170 | analog | # floor hand-offs (= `turn_count` − 1) |
| `fto_mean_s` | 0.069 | 0.043 | −0.91 – 2.65 | analog | mean floor-transfer offset (s); +gap / −overlap |
| `fto_median_s` | 0.127 | 0.116 | −0.95 – 2.65 | analog | median floor-transfer offset (s) |
| `fto_n` | 49.288 | 44.0 | 2 – 170 | analog | # FTO measurements (= speaker changes) |
| `speaker_balance` | 0.504 | 0.502 | 0.12 – 0.93 | analog | talk-time share of A (0.5 = equal) |
| `bc_rate_per_min` | 3.897 | 3.806 | 0 – 10.35 | analog | backchannels / min (VAP/Ekstedt list) |
| `bc_ack_per_min` | — | | | n/a | BC subtype: Acknowledgement (unavailable) |
| `bc_cont_per_min` | — | | | n/a | BC subtype: Continuer (unavailable) |
| `bc_react_per_min` | — | | | n/a | BC subtype: Reaction (unavailable) |
| `int_rate_per_min` | 0.862 | 0.629 | 0 – 5.24 | **approx** | interruptions / min (heuristic) |
| `int_competitive_per_min` | — | | | n/a | INT subtype: competitive (unavailable) |
| `int_cooperative_per_min` | — | | | n/a | INT subtype: cooperative (unavailable) |
| `int_floor_taking_per_min` | 0.814 | 0.603 | 0 – 4.03 | **approx** | floor-taking interruptions / min |
| `int_non_floor_per_min` | 0.048 | 0.0 | 0 – 1.41 | **approx** | non-floor-taking interruptions / min |
| `overlap_count_per_min` | 3.609 | 3.198 | 0 – 16.5 | analog | simultaneous-speech events / min |
| `overlap_dur_s` | 9.366 | 6.89 | 0 – 68.7 | analog | total overlap duration / call (s) |
| `laughter_rate_per_min` | 1.442 | 1.202 | 0 – 8.48 | analog | laughter events / min |
| `non_content_ratio` | 0.013 | 0.009 | 0 – 0.15 | analog | fraction of call that is noise |
| `question_rate_per_min` | 1.306 | 1.103 | 0 – 7.20 | **approx**† | questions / min (SWDA subset) |

† `question_rate_per_min` is computed only on the **1,155 / 2,438** conversations the
Switchboard Dialog Act corpus (SWDA) covers; the rest are blank and excluded from its mean.

Sanity signals that build confidence: **FTO ≈ 0.07 s** (human transitions cluster near
zero), **speaker_balance ≈ 0.50** (balanced dyads), durations 5–10 min, ≈198 combined WPM,
backchannels ≈ 3.9/min, laughter ≈ 1.4/min.

## What each attribute means (detailed)

### Size / pacing
- **`duration_min`** *(exact‑ish, 6.38)* — call length in minutes = last word-end time
  across both channels ÷ 60. FLOOR uses the WAV duration; the transcript span ≈ that.
- **`n_events_mean`** *(composite, 116.6)* — FLOOR = number of labeled events per
  conversation, averaged over its 3 annotators (hence the `_mean`). SWBD has no single
  event stream, so I *define* it = #turns + #backchannels + #overlaps + #laughter +
  #non-content segments — a "how many turn-taking events happened" proxy.
- **`event_rate_per_min`** *(composite, 18.5)* — `n_events_mean ÷ duration_min`.

### Lexical (the "exact" metrics)
- **`word_rate_wpm`** *(exact, 197.6)* — total words (both speakers) per minute, using the
  same word-extraction regex FLOOR uses, applied to the MS-State transcript (excluding
  `[silence]`/`[noise]`/`[laughter]`; partial and laughed words counted). It is words/min
  over the *whole call*, so ~198 combined / ~99 per speaker — lower than the ~150 wpm you'd
  measure only while a person is actually speaking.
- **`words_sp1` / `words_sp2`** *(exact, 641 / 625)* — raw per-channel word counts.
- **`wpm_sp1` / `wpm_sp2`** *(exact, 99.9 / 97.7)* — per-channel words per minute.
- **`ttr_sp1` / `ttr_sp2`** *(exact, 0.386 / 0.389)* — **type-token ratio** = unique word
  types ÷ total word tokens for that speaker (lower-cased). Lexical diversity: 1.0 = never
  repeats a word, lower = more repetition. (TTR shrinks with length, and SWBD per-speaker
  word counts differ from FLOOR's, so compare with that in mind even though the formula is
  identical.)

### Floor timing
- **`silence_ratio`** *(analog, 0.177)* — fraction of the call where **neither** speaker
  produces any token. FLOOR: 1 − union(all labeled events)/dur. SWBD: 1 − union(all
  non-`[silence]` tokens, both channels)/dur. 17.7% mutual silence.
- **`turn_count`** *(analog, 50.3)* — number of floor-holding **turns**. A turn is built by:
  (1) group each speaker's lexical words into IPUs (words <0.2 s apart merge), dropping
  words inside a backchannel span; (2) walk all IPUs in time order and merge consecutive
  same-speaker ones — the floor "changes" only when the *other* speaker produces a
  non-backchannel IPU. So a turn = one speaker holding the floor, possibly across several
  sentences and the listener's "uh-huhs."
- **`turn_dur_mean` / `_median` / `_std`** *(analog, 9.42 s / 4.43 s / 11.9 s)* —
  distribution of turn lengths. Mean ≫ median ⇒ right-skewed (a few long floor-holds, e.g.
  storytelling, pull the mean up). ⚠️ Most sensitive to the turn definition: SWBD turns
  merge across the listener's backchannels, so they're **coarser/longer** than IPU-level
  turns; a finer FLOOR "Regular Turn" would yield more, shorter turns. Tunable via
  `--ipu-gap`.
- **`n_speaker_changes`** *(analog, 49.3)* — how many times the floor passes between
  speakers. By construction = `turn_count − 1`.
- **`fto_mean_s` / `fto_median_s`** *(analog, 0.069 / 0.127)* — **Floor Transfer Offset**:
  at each speaker change, start(incoming turn) − end(outgoing turn). **Positive = a silent
  gap; negative = the next speaker started before the previous finished (overlap).** The
  core turn-taking timing metric; ≈0.07 s reproduces the well-known finding that human
  transitions are precisely timed (~0–250 ms). Mean < median because negative (overlapping)
  FTOs pull the mean down.
- **`fto_n`** *(analog, 49.3)* — number of FTOs measured = number of speaker changes.
- **`speaker_balance`** *(analog, 0.504)* — talk-time split: voiced(A) ÷ (voiced A + voiced
  B), voiced = that speaker's lexical+laughter time. **0.5 = equal; →1 A dominates; →0 B
  dominates.** Corpus mean ~0.50 ⇒ neither channel is systematically dominant; individual
  calls range 0.12–0.93.

### Discrete events
- **`bc_rate_per_min`** *(analog, 3.90)* — **backchannels** per minute: short listener
  responses ("uh-huh," "right") that signal listening without taking the floor. Count of
  entries in the VAP/Ekstedt `backchannels.csv` for that session (both speakers) ÷ minutes.
  Analog because it depends on Ekstedt's *detector*, not gold labels (and that list also
  shapes turns/overlap, since those spans are excluded).
- **`bc_ack` / `bc_cont` / `bc_react_per_min`** *(n/a, blank)* — FLOOR's three backchannel
  subtypes (Acknowledgement / Continuer / Reaction). SWBD's list has no subtyping → blank.
- **`int_rate_per_min`, `int_floor_taking_per_min`, `int_non_floor_per_min`** *(approx,
  0.86 / 0.81 / 0.05)* — **interruptions** per minute. FLOOR defines an interruption as
  starting *before a TRP* (a legitimate completion point), split floor-taking vs
  non-floor-taking. SWBD records no TRPs, so this is a heuristic: *floor-taking* = a speaker
  change overlapping the prior turn by >1 s (`--trp-tol`); *non-floor-taking* = an overlap
  (not at a floor change) starting >1 s before the incumbent's turn ends. ⚠️ This conflates
  "smooth overlap at a natural ending" with "genuine barge-in" — exactly the distinction
  FLOOR makes and SWBD can't — so it likely **over-counts**. Consider footnoting/blanking.
- **`int_competitive` / `int_cooperative_per_min`** *(n/a, blank)* — FLOOR's
  cooperative-vs-competitive axis; unrecoverable on SWBD.
- **`overlap_count_per_min` / `overlap_dur_s`** *(analog, 3.61 / 9.37 s)* — **simultaneous
  speech**: intersection of the two channels' floor-speech intervals (lexical words,
  backchannels excluded); each maximal both-active stretch is one overlap. ⚠️ SWBD counts
  *every* co-active stretch, while FLOOR annotators mark only salient overlaps, so SWBD's
  counts run higher.
- **`laughter_rate_per_min`** *(analog, 1.44)* — standalone `[laughter]` tokens (both
  channels) per minute. Laughed words like `[laughter-all]` count as the word "all," not as
  laughter, to avoid inflation.
- **`non_content_ratio`** *(analog, 0.013)* — fraction of time that is non-speech vocal
  noise. FLOOR's NonContent (noise / channel bleed / non-linguistic) → SWBD's `[noise]` +
  `[vocalized-noise]` token duration ÷ call duration. 1.3%.

### Questions
- **`question_rate_per_min`** *(approx + subset, 1.31)* — questions per minute. FLOOR counts
  events whose text literally contains "?". MS-State SWBD transcripts have **no
  punctuation**, so I use the Switchboard Dialog Act corpus (SWDA): utterances whose dialog
  act is a question (`qy` yes-no, `qw` wh-, `qo` open, `qh` rhetorical, `qrr` or-clause,
  their `^d`/`^t` variants, plus `^g` tag-questions; `^q` *quotation* excluded). Approx
  because it's a different signal (dialog acts vs "?") **and** only the 1,155 SWDA-covered
  conversations contribute (the other 1,283 are blank, excluded from the mean).

### Omitted (as requested)
- **`iaa_kappa_ab/ac/bc`, `iaa_fleiss_kappa`, `event_count_cv_abc`, `boundary_f1_*`** —
  these measure *agreement among FLOOR's 3 annotators* (Cohen's/Fleiss' kappa,
  event-count coefficient of variation, boundary F1). SWBD has one annotation, so agreement
  is undefined → omitted entirely.

---
*Full per-conversation distributions: `results/swbd_per_conversation.csv`. The drop-in
aggregate row: `results/swbd_per_type_aggregate.csv`. Setup, data sources & citations: the
repo `README.md`.*
