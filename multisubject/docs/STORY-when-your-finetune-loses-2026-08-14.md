# When Your Fine-Tune Loses to the Base Model — and Why That's the Best Thing That Happened to It

**Content-source document for YouTube (Rich's ask, 2026-08-14: "this failure actually
makes a good story, especially if we can turn it around to a success"). Every number
below has a receipt in `../runs/2026-08-13-multisubject-v2/` — this is a story we can
tell with the evidence on screen. Part 2 (the turnaround) gets written by the Lane 7
re-train; its recipe is at the bottom.**

---

## The story in one paragraph

We fine-tuned Gemma 4 26B for GCSE tutoring in April, shipped it to a Kaggle hackathon,
and served it to a real student for four months — and she loved it. Then we built a
proper evaluation estate: pre-registered protocol, blind judging, two independent judge
models, three measuring instruments. The verdict was brutal: **the stock base model beat
our fine-tune in all eight subjects, on every instrument — including the one we built
specifically to capture what we thought the fine-tune was best at.** This is the story of
why that happened, why the real-world experience wasn't wrong, and exactly what a
fine-tune has to do differently to beat a 2026 base model — which we're now doing.

## Act 1 — The fine-tune everyone liked

- April 2026: LoRA rank 16, 1 epoch, max-seq 2048, Unsloth + TRL on a DGX Spark.
  Training data: synthetic multi-turn tutoring dialogues from our own Player-Coach
  pipeline (the agentic-dataset-factory).
- It had personality. It held conversations. A real Year 10 student used it for real
  revision and enjoyed it. The Kaggle entry shipped.
- One early warning, politely ignored under deadline: a 16-item eval on 2026-05-18
  scored the base ahead 15–1 single-turn. n was tiny; multi-turn looked nearly level
  (2–0–1); we shipped anyway (the deadline was literally an ADR).

## Act 2 — Building an eval you can't argue with

Fast-forward to August. We built the judging estate properly:

- **136 golden items across 8 subjects** (adversarially reviewed), 24 scripted
  multi-turn scenarios, per-subject rubrics carrying the real AQA assessment-objective
  structures (a fact-check against AQA's own pages caught an AO error in our draft
  rubrics MID-JUDGING — two subjects were re-judged from scratch before any verdict
  existed; pre-registration discipline doing its job on camera).
- **Pre-registered protocol** — hypothesis, decision rule, seeds, judges, all committed
  BEFORE generation; the harness literally refuses to run without it.
- **Blind, position-randomised judging by two independent judges from different model
  families** (a fresh-context Claude with no access to the identity key, and a local
  Qwen 3.6 — zero API dollars), with per-item agreement reported.
- **Three instruments**, because one is a lie: pairwise single-turn, a length-neutral
  criterion track (each response scored ALONE against pre-registered behaviours — so
  verbosity can't win by contrast), and whole-session multi-turn judging with a
  dimension built for conversational tutoring: `engagement_elicitation`.

## Act 3 — The verdict (and the twist inside it)

| Instrument | Verdict |
|---|---|
| Pairwise single-turn | **base 106 / fine-tune 7 / tie 1** (84% judge agreement) |
| Criterion, length-neutral | base 73.9% vs ft 67.0% behaviours; red flags 4 vs 12 |
| Multi-turn sessions | **agreement set: base 20 / fine-tune 0** |

The twist: the owner challenged the first number — "in the real world it's brilliant at
holding a conversation; are you measuring the right thing?" — and he was HALF right.
The pairwise blowout WAS partly a format artifact: the length-neutral track shows the
real behaviour gap is ~7 points, not 15:1. But the conversational hypothesis died on
its own instrument: across 24 whole sessions, both judges preferred the base — and
scored it higher on engagement itself (4.17 vs 3.71 and 4.92 vs 3.50).

And the reconciliation with four months of happy real-world use: **the student never
met the bare fine-tune.** She met the SYSTEM — retrieval, quote verification, an async
coach, a planner. The system is good. The question the eval answers is which model
serves the system best — and the base has never been given the chance. (The next
receipt to collect: an attended base-in-the-loop trial. One config flip.)

## Act 4 — The autopsy: four mechanisms, all measured

1. **The bar was "base + a good prompt."** A 2026 instruction-tuned 26B already tutors
   Socratically when asked. The fine-tune's training target was behaviour that
   prompting already achieves — leaving no upside, only downside.
2. **Self-distillation subtracts.** The training data came from a same-class model
   teaching itself. That narrows toward the corpus's average — including its errors.
   The model card admitted "can hallucinate quotes"; the fabrication eval caught the
   tutor reproducing a known April misquote, live, in August. The accuracy tax is
   measured: subject_accuracy 4.46 vs 4.78, red flags 3× the base's.
3. **It learned to hide its virtues.** Trained to reason in `<think>` blocks — which
   the product strips — and to answer in short conversational turns. Its AO framing
   scored 2.91 vs 4.12 not because it lacks AO knowledge but because it puts it where
   no student ever looks. A training-convention own-goal.
4. **No eval in the loop.** One epoch, shipped on a deadline, first judged twelve days
   after submission. Nothing during training measured the only thing that matters:
   "is this better than the base?"

## Act 5 — The comeback recipe (Lane 7, now in motion)

Rich's directives (2026-08-14) plus the eval-derived recipe:

1. **A genuinely stronger teacher: DeepSeek v4 Flash 0731** generates the new dataset —
   distillation only adds what the teacher has over the student. No more
   self-distillation, ever.
2. **Batch mode in the agentic-dataset-factory** (previously discussed there) so
   generation runs as an unattended, resumable, high-volume job.
3. **Every training sample passes the fabrication gate**: quotes in generated dialogues
   are verified against the real corpora by the quote-verification harness BEFORE the
   sample enters the dataset. A model should never again train on a hallucinated quote.
4. **Fixed style targets**: pedagogy and AO framing in the VISIBLE answer; a mix of
   full-scaffold answers and conversational turns; direct questions get direct answers;
   set-text facts reinforced; longer max-seq so complete exchanges survive.
5. **Train against the eval**: golden sets held out; every checkpoint judged vs base by
   the same three-instrument harness; the pre-registered bar is "beats base on all
   three or it doesn't ship." The judge pipeline doubles as a preference-data factory
   (pairwise verdicts are DPO-ready) if SFT alone can't clear the bar.
6. **Generality protection**: mixed general instruction data against the accuracy tax;
   and the Qwen 3.6 bake-off tests whether Gemma is even the right chassis.

## The moral (the thumbnail line)

**A fine-tune isn't an asset until an eval says it is.** The happy ending isn't "our
model won" — it's that the product got better the day we let the evidence outrank our
attachment to our own weights. If the re-train clears the bar, that's Part 2. If it
doesn't, serving the base IS the success — and we'll say that on camera too.

---

*Receipts: `runs/2026-08-13-multisubject-v2/` (MANIFEST.json, RESULTS, judgements,
blinding artefacts, voided-run files kept); study-tutor plan-of-record Lane 7;
the 2026-05-18 history import in `docs/history/`.*
