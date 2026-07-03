# Oracle validation — abl-faud-feature-audit (2026-07-03)

Per scope §3.2: the task must pass its own tests with the Oracle solution
applied before it may grade anything.

## RED — pristine pre-FEAT pin (71db6d268)

Verifier on the untouched environment image (the `feature` CLI group exists
at the pin with only `validate`; `audit` and the core module are absent):

```
FAILED test_auditor_module_exists
FAILED test_stale_detected_exit_1
FAILED test_partial_feature_not_stale
FAILED test_fix_reconciles_and_clean_exit_0
FAILED test_clean_repo_exit_0
5 failed                  → reward 0
```

## GREEN — landed diff applied (71db6d268..8e6c5e9cf, behaviour paths)

```
solution applied OK
5 passed                  → reward 1
```

## Harbor oracle rollout

Job `abl-faud-oracle-1`: reward **1.0**, 1 trial completed, 0 errored, 14 s.
Evidence copies: `validation/{job-result.json,reward.txt,pytest.log}`.

## Verifier notes

- Black-box: drives the installed `guardkit-py feature audit` console script
  as a subprocess against synthetic project trees — no imports of the
  implementation, no reliance on the repo's own tests.
- Covers the landed dict-vs-string task-schema regression (the stale fixture
  uses dict tasks, the clean one bare strings) and the partial-completion
  inference (1/2 done ⇒ in_progress, not stale).
- Exit codes are the CI-gate contract (AC-004): 1 stale w/o --fix, 0 after
  --fix and when clean; --fix must rewrite only stale YAMLs.
