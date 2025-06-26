#!/usr/bin/env sh

# Check if the user provided a YAML file as an argument
if [ -z "$1" ]; then
  echo "Usage: $0 <path-to-workflow-file.yaml> [additional act options]"
  echo ""
  echo "Examples:"
  echo "  $0 .github/workflows/ci.yaml                    # Run all jobs"
  echo "  $0 .github/workflows/ci.yaml -j tests           # Run only test jobs"
  echo "  $0 .github/workflows/ci.yaml --matrix python-version:3.12.8 --matrix vyper-version:0.4.3"
  echo "                                                   # Run specific matrix combination"
  echo "  $0 .github/workflows/ci.yaml --pull=false       # Skip pulling images"
  exit 1
fi

WORKFLOW_FILE="$1"
shift  # Remove first argument to pass the rest to act

# Run the act command with the provided workflow file
act -W "$WORKFLOW_FILE" \
  --container-architecture linux/amd64 \
  -P ubuntu-latest=catthehacker/ubuntu:act-latest \
  "$@"
