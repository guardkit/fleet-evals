"""Did the seat actually do what the note asked? — the gates for the revise path.

WHY THIS EXISTS, in plain words (2026-09-05).

Rich has three touches per feature: approve the spec, tap the build gate, say merge. On
the first of those he can send a note back instead of approving. On 2026-09-05 he sent
"drop example 3, seven exactly is the rule". The forge marked the draft superseded and
re-dispatched the spec writer with the note at the top of its prompt. The writer returned
the same six worked examples — example 3 reworded, still there. Its coach scored the
result 1.0, because the coach's criteria never ask whether the feedback was resolved. The
second card he was shown was identical to the first, line for line, and nothing said that
nothing had changed.

So one of his three touches silently did nothing. Nothing in the estate could have caught
it, because nothing measured it. This module is the measurement, and it is ORDINARY CODE
on the produced digest — no model judges whether a model obeyed.

WHAT IT ASKS, and nothing more:

  1. Was the asked-for change made?   (the note's own target)
  2. Was anything ELSE changed?       (an "improved" spec is a rejected spec too)
  3. Do the plain-language list and the specification file still agree on how many
     worked examples there are?

The note itself is DATA, carried in the task's `task.toml` under `[revise]`, never
hard-coded here — a second note is a second table, not a second grader.

Every finding is a sentence a person can read without a key: it names the example by its
position in the list Rich saw, quotes what is there, and says what was expected instead.

stdlib + PyYAML (the digest is YAML, and the rest of the spec gates already parse it with
the same reader production uses).
"""

from __future__ import annotations

import re
import tomllib
from difflib import SequenceMatcher
from pathlib import Path

# A reworded survivor is the exact failure that got through on 2026-09-05, so "is it gone"
# cannot be a string equality test alone. Measured on this task's own sentences: the worst
# innocent pair scores 0.55, the real paraphrase scores 0.86. 0.75 sits in the gap with
# room on both sides.
PARAPHRASE_RATIO = 0.75

NOTE_KINDS = ("remove", "reword")

CHECK_NOTE = "note_honoured"
CHECK_COLLATERAL = "nothing_else_changed"
CHECK_COUNT = "list_and_spec_agree"


# --- reading the note and the two digests --------------------------------------

def load_note(task_dir: Path) -> dict:
    """The `[revise]` table of a task's task.toml, checked for the fields the gates read."""
    with open(Path(task_dir) / "task.toml", "rb") as f:
        note = (tomllib.load(f).get("revise") or {})
    if not note:
        raise ValueError(f"{task_dir}: task.toml has no [revise] table — this is not a revise task")
    kind = note.get("kind")
    if kind not in NOTE_KINDS:
        raise ValueError(f"{task_dir}: [revise] kind must be one of {NOTE_KINDS}, not {kind!r}")
    index = note.get("example_number")
    if not isinstance(index, int) or index < 1:
        raise ValueError(f"{task_dir}: [revise] example_number must be the 1-based position "
                         f"of the example the note is about, not {index!r}")
    if not str(note.get("note") or "").strip():
        raise ValueError(f"{task_dir}: [revise] note must carry the words Rich actually sent")
    return note


def digest_sentences(digest) -> list[str]:
    """The plain-language list a person reads on the card, in the order they read it."""
    if not isinstance(digest, dict):
        return []
    out = []
    for entry in digest.get("scenarios") or []:
        if isinstance(entry, dict):
            out.append(str(entry.get("sentence") or "").strip())
    return out


def _flat(text: str) -> str:
    """Whitespace-insensitive, case-insensitive — a line wrapped differently is the same
    sentence. Nothing else is normalised: 'word for word' has to mean word for word."""
    return re.sub(r"\s+", " ", str(text)).strip().lower()


def _same(a: str, b: str) -> bool:
    return _flat(a) == _flat(b)


def _quote(sentence: str, limit: int = 110) -> str:
    s = re.sub(r"\s+", " ", str(sentence)).strip()
    return '"' + (s if len(s) <= limit else s[: limit - 1] + "…") + '"'


# --- the gates ------------------------------------------------------------------

def note_findings(prior: list[str], produced: list[str], note: dict) -> list[dict]:
    """Check 1: was the change the note asked for actually made?"""
    kind, n = note["kind"], int(note["example_number"])
    findings: list[dict] = []
    if n > len(prior):
        return [{"check": CHECK_NOTE,
                 "reason": f"The note is about example {n}, but the spec sent back for revision "
                           f"only had {len(prior)} of them. The task is mis-registered."}]
    target = prior[n - 1]
    wanted = len(prior) - 1 if kind == "remove" else len(prior)

    if len(produced) != wanted:
        asked = ("drop one worked example, so the list should now have"
                 if kind == "remove" else
                 "change one worked example and no more, so the list should still have")
        findings.append({"check": CHECK_NOTE,
                         "reason": f"The note asked to {asked} {wanted} sentences. "
                                   f"It has {len(produced)}."})

    if kind == "remove":
        for i, sentence in enumerate(produced, start=1):
            if _same(sentence, target):
                findings.append({"check": CHECK_NOTE,
                                 "reason": f"Example {n} was supposed to be dropped, but sentence "
                                           f"{i} is still it, word for word: {_quote(sentence)}"})
            elif SequenceMatcher(None, _flat(target), _flat(sentence)).ratio() >= PARAPHRASE_RATIO:
                findings.append({"check": CHECK_NOTE,
                                 "reason": f"Example {n} was supposed to be dropped, but sentence "
                                           f"{i} is a reworded version of it, not a different "
                                           f"example: {_quote(sentence)}"})
        for phrase in note.get("must_not_say") or []:
            for i, sentence in enumerate(produced, start=1):
                if _flat(phrase) in _flat(sentence):
                    findings.append({"check": CHECK_NOTE,
                                     "reason": f"Sentence {i} still says \"{phrase}\", which is the "
                                               f"thing the note ruled out: {_quote(sentence)}"})
    else:  # reword
        if len(produced) >= n:
            now = produced[n - 1]
            if _same(now, target):
                findings.append({"check": CHECK_NOTE,
                                 "reason": f"Example {n} is unchanged — it still reads "
                                           f"{_quote(now)}. The note asked for it to change."})
            for phrase in note.get("must_say") or []:
                if _flat(phrase) not in _flat(now):
                    findings.append({"check": CHECK_NOTE,
                                     "reason": f"Example {n} does not say \"{phrase}\", which is "
                                               f"what the note asked for. It reads {_quote(now)}"})
            alternatives = note.get("must_say_any") or []
            if alternatives and not any(_flat(p) in _flat(now) for p in alternatives):
                spoken = ", ".join(f'"{p}"' for p in alternatives)
                findings.append({"check": CHECK_NOTE,
                                 "reason": f"Example {n} says none of {spoken} — the note asked for "
                                           f"one of those. It reads {_quote(now)}"})
            for phrase in note.get("must_not_say") or []:
                if _flat(phrase) in _flat(now):
                    findings.append({"check": CHECK_NOTE,
                                     "reason": f"Example {n} still says \"{phrase}\", which is the "
                                               f"wording the note replaced. It reads {_quote(now)}"})
        else:
            findings.append({"check": CHECK_NOTE,
                             "reason": f"Example {n} is not in the list at all. The note asked for "
                                       f"it to be reworded, not removed."})
    return findings


def collateral_findings(prior: list[str], produced: list[str], note: dict) -> list[dict]:
    """Check 2: every example the note did NOT mention survives word for word, in order.

    Matched by CONTENT, not by position: when a note drops an example, everything after it
    shifts up by one, and comparing position to position would then report five changes
    where a person reading the two cards sees none. So each surviving sentence is looked
    for in the new list from where the last one was found — present and in order, or a
    finding that names it.

    A revise that quietly improves a sentence nobody asked about is a revise Rich cannot
    approve by reading the difference, which is the only way he reads it."""
    kind, n = note["kind"], int(note["example_number"])
    expected = [(i + 1, s) for i, s in enumerate(prior)
                if not (i == n - 1 and kind in ("remove", "reword"))]
    findings: list[dict] = []
    remaining = list(enumerate(produced, start=1))  # (position in the new list, sentence)
    for was_number, sentence in expected:
        hit = next((k for k, (_pos, cand) in enumerate(remaining) if _same(cand, sentence)), None)
        if hit is not None:
            del remaining[: hit + 1]
            continue
        if not remaining:
            findings.append({"check": CHECK_COLLATERAL,
                             "reason": f"Example {was_number} was not mentioned in the note but is "
                                       f"missing from the end of the new list: {_quote(sentence)}"})
            continue
        near = max(remaining, key=lambda c: SequenceMatcher(None, _flat(sentence),
                                                            _flat(c[1])).ratio())
        ratio = SequenceMatcher(None, _flat(sentence), _flat(near[1])).ratio()
        if ratio >= 0.5:
            findings.append({"check": CHECK_COLLATERAL,
                             "reason": f"Example {was_number} was not mentioned in the note but has "
                                       f"been rewritten. It read {_quote(sentence)} and now reads "
                                       f"{_quote(near[1])}"})
            remaining = remaining[remaining.index(near) + 1:]
        else:
            stands = remaining[0]
            findings.append({"check": CHECK_COLLATERAL,
                             "reason": f"Example {was_number} was not mentioned in the note but is "
                                       f"not in the new list word for word. It read "
                                       f"{_quote(sentence)}; sentence {stands[0]} now reads "
                                       f"{_quote(stands[1])}"})
            remaining = remaining[1:]
    return findings


def count_findings(produced: list[str], feature_scenario_count: int) -> list[dict]:
    """Check 3: the list a person approves and the specification it stands for agree."""
    if len(produced) != feature_scenario_count:
        return [{"check": CHECK_COUNT,
                 "reason": f"The plain-language list has {len(produced)} sentences but the "
                           f"specification file has {feature_scenario_count} worked examples. "
                           f"They have to be the same list."}]
    return []


def revise_findings(prior: list[str], produced: list[str], feature_scenario_count: int,
                    note: dict) -> list[dict]:
    """All three checks, in the order a reader would ask them."""
    return (note_findings(prior, produced, note)
            + collateral_findings(prior, produced, note)
            + count_findings(produced, feature_scenario_count))


def grade(prior: list[str], produced: list[str], feature_scenario_count: int,
          note: dict) -> dict:
    """PASS/FAIL plus the plain-English reasons — the shape a card can print."""
    findings = revise_findings(prior, produced, feature_scenario_count, note)
    return {
        "passed": not findings,
        "note": str(note.get("note")),
        "reasons": [f["reason"] for f in findings],
        "findings": findings,
    }
