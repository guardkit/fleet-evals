#!/bin/bash
# Verifier for abl-spike-001 — runs offline: pytest + pyyaml are preinstalled
# in the task image (environment/Dockerfile), no network fetch at verify time.
# Copied to /tests/test.sh by Harbor and executed inside the environment.

mkdir -p /logs/verifier

python3 -m pytest /tests/test_outputs.py -rA -v 2>&1 | tee /logs/verifier/pytest.log
status=${PIPESTATUS[0]}

if [ "$status" -eq 0 ]; then
  echo 1 > /logs/verifier/reward.txt
else
  echo 0 > /logs/verifier/reward.txt
fi
