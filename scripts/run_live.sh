#!/usr/bin/env bash

set -euo pipefail

exec /Users/rileylai/.config/learnloop/run-with-secrets.sh "${1:-api}"
