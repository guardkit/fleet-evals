#!/bin/bash
# Verifier for abl-fs01 — runs offline: the repo and its dev extras (pytest &
# co.) are preinstalled in the task image. Copied to /tests/test.sh by Harbor
# and executed inside the environment.

mkdir -p /logs/verifier

python3 -m pytest /tests/test_outputs.py -rA -v 2>&1 | tee /logs/verifier/pytest.log
status=${PIPESTATUS[0]}

if [ "$status" -eq 0 ]; then
  echo 1 > /logs/verifier/reward.txt
else
  echo 0 > /logs/verifier/reward.txt
fi
