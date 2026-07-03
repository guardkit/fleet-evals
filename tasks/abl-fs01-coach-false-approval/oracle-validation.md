# Oracle validation — abl-fs01-coach-false-approval (2026-07-03)

Per scope §3.2: a task must pass its own tests with the Oracle solution
applied before it may grade anything, and the false-green tasks must encode
the regression that originally slipped.

## RED — pristine pre-fix pin (92ef897)

Verifier on the untouched environment image:

```
FAILED test_outputs.py::test_lifespan_suite_green
FAILED test_outputs.py::test_full_unit_suite_green
2 failed, 2 passed        → reward 0
```

Inner failure identity (full unit suite at the pin, `-o addopts=` guard on):

```
FAILED tests/unit/test_app_lifespan.py::test_lifespan_enters_and_exits_cleanly_with_fake_store
1 failed, 345 passed, 51 deselected
```

— exactly the regression the Coach false-approved on 2026-06-13 (FEAT-MEM-04
wave 4: `DeterministicWriter(store=store)` missing its required `settings`
argument). The two verifier tests that pass at the pin are guards (frozen
files untouched, wiring present), not regression detectors; reward requires
all four.

## GREEN — oracle fix applied (6390d1e, one line)

```
fix applied
4 passed                  → reward 1
```

## Harbor oracle rollout

Job `abl-fs01-oracle-1`: reward **1.0**, 1 trial completed, 0 errored, 29 s.
Evidence copies: `validation/{job-result.json,reward.txt,pytest.log}`.

## Gate-gaming resistance (encodes the GOLD.md disqualifiers)

| Evasion | Blocked by |
|---|---|
| Edit/delete the failing test | sha256 freeze on `tests/unit/test_app_lifespan.py` |
| Tamper shared fixtures | sha256 freeze on `tests/conftest.py` |
| Deselect via pyproject `addopts` | verifier runs pytest with `-o addopts=` |
| Unwire the feature to dodge the lifespan path | `test_wave4_wiring_still_present` |
