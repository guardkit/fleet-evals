# _multiturn — session-level judging addendum (PROTOCOL v3, 2026-08-13)

Compose this addendum WITH the subject's rubric when judging multi-turn
transcripts. You are judging the WHOLE SESSION as a tutoring conversation,
not any single reply: read the full dialogue before scoring anything.

**The seventh dimension — `engagement_elicitation`:** does the tutor DRAW THE
STUDENT IN across the session? Strong signals: elicits the student's own
attempts before explaining; builds each turn on the student's actual words;
sustains momentum (the student says more, tries more, risks more as the
session goes on); hands thinking back to the student at every opportunity.
Weak signals: lectures; answers its own questions; comprehensive
mini-essays that leave the student nothing to do; ignores what the student
just said. A short, well-aimed question that gets the student working beats
a complete explanation the student passively receives — score accordingly.
This dimension exists because single-turn judging structurally cannot see
it (v3 rationale, on the record).

**Session-level reading of the other six:** scaffolding = does the ARC build
(diagnose → support → stretch), not "is each reply thorough"; aqa_alignment
= woven naturally across the session, not name-dropped per reply;
subject_accuracy = across everything said; tone = including how it handles
the student's frustration turns.

Verdict shape (SEVEN dimensions per side — names are load-bearing):

```
Return ONLY a fenced ```json block of exactly this shape:
{"winner": "A" | "B" | "tie",
 "A": {"socratic_stance": int, "aqa_alignment": int, "scaffolding": int,
       "subject_accuracy": int, "tone": int, "reasoning_visibility": int,
       "engagement_elicitation": int},
 "B": {... same seven keys ...},
 "rationale": "<= 2 sentences"}
```
