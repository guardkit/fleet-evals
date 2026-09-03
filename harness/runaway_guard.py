#!/usr/bin/env python3
"""Stop a reply that has started repeating itself, instead of paying for it to the ceiling.

WHY THIS EXISTS (2026-09-03)
----------------------------
A product-owner exam rep generated to the 16,384-token ceiling for 17 minutes and only then
could be graded. The answer was the same 19 scenarios written out eleven times
(`runs/po-heldout-spec/20260902-followup-po-v6-v3-batchinvariant/po-held-007-feature-spec/rep1/
response.txt`: 203 `Scenario:` lines, 19 distinct). Nothing in the harness noticed. The reply
was always going to fail its grade; the only question was whether we paid seventeen minutes to
find out.

THE RULE — one sentence
-----------------------
    Abort when the last 300 characters generated have ALREADY appeared, verbatim, four or more
    times in this same reply.

That is it. No content judgement, no model, no heuristic about what a good answer looks like:
pure string counting over the text the server has streamed so far.

WHY NOT PRODUCTION'S THRESHOLDS
-------------------------------
Production's degeneration guard is `describe_degenerate_run()` in
`specialist-agent/src/specialist_agent/orchestrator/demarcation_conformance.py:159`, with
`_DEGENERATE_RUN_MIN = 1024` (same file, line ~150): it fires on "a run of N consecutive
identical CHARACTERS" once N reaches 1024, sized against a live 259,072-character '-' run
(run 63a5baf5, 2026-08-15) and a 291-character legitimate box rule. That rule is right for what
it guards and useless here: measured over all 107 `runs/**/response.txt` answer sheets in this
repo on 2026-09-03, it fires on NONE of them — including all nine responses that are plainly
runaways. A model repeating whole scenarios never repeats one character.

WHY NOT A "REPEATED LINE" WINDOW
--------------------------------
The other obvious rule — over the last 2,000 generated characters, the most frequent non-blank
line occurs 12+ times — was measured on the same 107 answer sheets before being rejected:

  * it fired on FIVE legitimate replies, on lines like `    {`, `    },` and `  tags:`. Any JSON
    extract answer has a dozen `    {` lines inside 2,000 characters. One of the five is the
    2026-09-02 control run, a good answer the guard would have destroyed;
  * it caught NONE of the nine runaways, because their repeat cycle is about 6,600 characters
    long — three times the window. The repetition is real but far too wide to see through a
    2,000-character slit.

Ignoring short structural lines (30+ characters) removes the five false fires and still catches
none of the nine. So the window rule is not carried: it costs answers and buys nothing.

THE MEASUREMENT BEHIND THE RULE THAT IS CARRIED
-----------------------------------------------
Same 107 answer sheets, 2026-09-03, replayed 500 characters at a time:

  * fires on 9 of 9 known runaways, at 8,000-66,000 characters in — the 2026-09-03 incident
    aborts at ~15,000 of 72,821 characters, so about four fifths of the seventeen minutes is
    never spent;
  * fires on 0 of the other 98 answer sheets.

The thresholds (300 characters, 4 occurrences) are the ones the 2026-09-03 instruction named;
only the search window is the whole reply rather than the last 2,000 characters, because the
measurement above says a 2,000-character window cannot see a 6,600-character cycle.

WHAT AN ABORT COSTS
-------------------
Nothing that was going to be earned. The partial text is kept and graded exactly as today, and
it fails — quickly and honestly. The receipt records that the guard fired, which rule fired, and
how much text arrived first, so no later reader can mistake an aborted rep for a model that
merely wrote a short answer.

stdlib only, like every other harness module. Python 3.11+.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Callable, Iterable

# The rule's two numbers, and how often it is asked.
BLOCK_CHARS = 300          # length of the trailing block compared against the reply so far
BLOCK_REPEATS = 4          # how many verbatim occurrences of that block end the reply
CHECK_EVERY_CHARS = 500    # cadence: the rule is asked once per 500 new characters

# Fields a streamed delta may carry. `content` is the answer; the other two are the separated
# thinking (llama.cpp calls it reasoning_content, vLLM v0.25.0 calls it reasoning) — a runaway
# inside the thinking costs exactly as much as one inside the answer, so all three are watched.
DELTA_FIELDS = ("content", "reasoning_content", "reasoning")


class RunawayDetector:
    """Accumulates generated text and says when it has started repeating itself.

    `feed(piece)` returns None while the reply looks healthy, and a plain-English description of
    the rule that fired the first time the reply repeats itself. After it fires it keeps
    returning that same description.
    """

    def __init__(
        self,
        block_chars: int = BLOCK_CHARS,
        block_repeats: int = BLOCK_REPEATS,
        check_every_chars: int = CHECK_EVERY_CHARS,
    ) -> None:
        self.block_chars = block_chars
        self.block_repeats = block_repeats
        self.check_every_chars = check_every_chars
        self._parts: list[str] = []
        self._chars = 0
        self._next_check = block_chars * block_repeats
        self.fired: str | None = None

    @property
    def chars(self) -> int:
        return self._chars

    def text(self) -> str:
        return "".join(self._parts)

    def feed(self, piece: str) -> str | None:
        if self.fired is not None:
            return self.fired
        if not piece:
            return None
        self._parts.append(piece)
        self._chars += len(piece)
        if self._chars < self._next_check:
            return None
        self._next_check = self._chars + self.check_every_chars
        self.fired = self.check(self.text())
        return self.fired

    def check(self, text: str) -> str | None:
        """The rule itself, on the whole text generated so far."""
        if len(text) < self.block_chars * self.block_repeats:
            return None
        probe = text[-self.block_chars :]
        occurrences = text.count(probe)  # non-overlapping, which is the conservative count
        if occurrences >= self.block_repeats:
            return (
                f"the last {self.block_chars} characters generated had already been written "
                f"{occurrences} times in this reply (abort at {self.block_repeats})"
            )
        return None


def iter_sse_events(lines: Iterable[bytes | str]) -> Iterable[dict]:
    """Yield the JSON objects out of an OpenAI-style `data: {...}` stream."""
    for raw in lines:
        line = raw.decode("utf-8", "replace") if isinstance(raw, bytes) else raw
        line = line.strip()
        if not line or line.startswith(":") or not line.startswith("data:"):
            continue
        payload = line[len("data:") :].strip()
        if payload == "[DONE]":
            return
        try:
            yield json.loads(payload)
        except json.JSONDecodeError:
            continue  # a half-line or a keep-alive: the next event carries the text


def consume_stream(
    lines: Iterable[bytes | str],
    detector: RunawayDetector | None = None,
    on_abort: Callable[[], None] | None = None,
) -> dict:
    """Fold a streamed completion back into the shape a non-streaming reply has.

    The returned `reply` is `{"choices": [{"message": {...}, "finish_reason": ...}], ...}` so the
    runners' own `response_text()` reads it unchanged — same text, same provenance strings,
    including the reasoning re-wrap. Nothing about a healthy reply changes.
    """
    parts: dict[str, list[str]] = {field: [] for field in DELTA_FIELDS}
    finish_reason = None
    server_model = None
    usage = None
    tokens_received = 0
    aborted_rule = None

    for chunk in iter_sse_events(lines):
        if chunk.get("model"):
            server_model = chunk["model"]
        if chunk.get("usage"):
            usage = chunk["usage"]
        for choice in chunk.get("choices") or []:
            if choice.get("finish_reason"):
                finish_reason = choice["finish_reason"]
            delta = choice.get("delta") or choice.get("message") or {}
            carried_text = False
            for field in DELTA_FIELDS:
                piece = delta.get(field)
                if not piece:
                    continue
                carried_text = True
                parts[field].append(piece)
                if detector is not None:
                    aborted_rule = detector.feed(piece)
            if carried_text:
                tokens_received += 1  # one streamed delta ≈ one token on these servers
            if aborted_rule:
                break
        if aborted_rule:
            break

    if aborted_rule and on_abort is not None:
        on_abort()  # close the connection: the point of the guard is to stop paying

    message: dict = {"content": "".join(parts["content"])}
    for field in ("reasoning_content", "reasoning"):
        if parts[field]:
            message[field] = "".join(parts[field])
    reply = {
        "choices": [{"message": message, "finish_reason": finish_reason}],
        "model": server_model,
        "usage": usage,
    }
    return {
        "reply": reply,
        "aborted": bool(aborted_rule),
        "rule": aborted_rule,
        "tokens_received": tokens_received,
        "chars_received": detector.chars if detector is not None else None,
    }


def _post(endpoint: str, payload: dict, timeout_s: int, opener: Callable[..., object] | None):
    request = urllib.request.Request(
        endpoint.rstrip("/") + "/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", "Accept": "text/event-stream"},
        method="POST",
    )
    return (opener or urllib.request.urlopen)(request, timeout=timeout_s)


def stream_chat_completion(
    endpoint: str,
    body: dict,
    timeout_s: int,
    detector: RunawayDetector | None = None,
    opener: Callable[..., object] | None = None,
) -> dict:
    """POST a streaming /chat/completions and fold it back, aborting on a runaway.

    `body` is the same body the non-streaming call sends, with `stream` set here. `opener` is a
    seam for the tests: it defaults to urllib.

    A streamed reply carries no token counts unless they are asked for, and a rep record that
    stopped saying how many tokens it cost would be a receipt made worse by a safety feature —
    so `stream_options.include_usage` is requested. A server too old to know that option answers
    with an HTTP error; the request is then sent again without it rather than failing the rep.
    """
    payload = dict(body)
    payload["stream"] = True
    payload["stream_options"] = {"include_usage": True}
    try:
        resp = _post(endpoint, payload, timeout_s, opener)
    except urllib.error.HTTPError:
        payload.pop("stream_options")
        resp = _post(endpoint, payload, timeout_s, opener)
    try:
        return consume_stream(resp, detector=detector, on_abort=resp.close)
    finally:
        try:
            resp.close()
        except Exception:  # noqa: BLE001 — already closed by the abort path
            pass


def guard_record(enabled: bool, outcome: dict | None) -> dict:
    """The plain-English block written into each rep's config.json.

    Every run before 2026-09-03 read its reply in one non-streaming response with no guard at
    all, so the frozen exam's comparability has to be readable off the receipt: this block says
    whether the guard was on, and if it fired, which rule fired and how much text had arrived.
    """
    if not enabled:
        return {
            "enabled": False,
            "note": "off (--no-runaway-guard): the reply was read in one non-streaming "
                    "response, as in every run before 2026-09-03",
        }
    record: dict = {
        "enabled": True,
        "rule": f"abort when the last {BLOCK_CHARS} characters generated have already been "
                f"written {BLOCK_REPEATS} times in this reply",
        "fired": bool(outcome and outcome.get("aborted")),
        "transport": "streamed",
    }
    if outcome:
        record["tokens_received"] = outcome.get("tokens_received")
        record["chars_received"] = outcome.get("chars_received")
        if outcome.get("aborted"):
            record["fired_rule"] = outcome.get("rule")
    return record
