#!/usr/bin/env bash
# Tailor the master resume to a job description using the LiteLLM proxy.
#
#   ./tailor.sh                          interactive: pick the type, then paste the job
#   ./tailor.sh job.txt industry         from a file
#   pbpaste | ./tailor.sh - teaching     from a pipe
#
# Output: resumes/Jose Alberto Tupayachi Silva - Resume-<TAG>_<ind|Teaching>_tay.pdf
#         resumes/tailored/  (.tex, report, model response, job description)
# The master resume, build.sh outputs and main.pdf are never modified.
# The headline under your name is never changed and the job's title is not used.
#
# Settings (environment variables):
#   LITELLM_BASE_URL  proxy URL            (default http://localhost:4000)
#   LITELLM_MODEL     model_name in config (default qwen3)
#   LITELLM_API_KEY   proxy key            (default: master_key in ~/litellm/config.yaml)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"

usage() { sed -n '2,6p' "$0" | sed 's/^# \{0,1\}//'; exit 1; }

if [ $# -eq 0 ]; then
  echo "Which resume do you want to tailor?"
  echo "  1) Industry"
  echo "  2) Teaching"
  while :; do
    read -r -p "Select 1 or 2: " choice
    case "$choice" in
      1|i|I|industry) KIND=industry; break ;;
      2|t|T|teaching) KIND=teaching; break ;;
    esac
  done
  JD="-"
elif [ $# -eq 2 ]; then
  JD="$1"
  case "$2" in
    industry|ind) KIND=industry ;;
    teaching|teach) KIND=teaching ;;
    *) echo "Type must be 'industry' or 'teaching'"; usage ;;
  esac
  if [ "$JD" != "-" ] && [ ! -f "$JD" ]; then echo "Job description file not found: $JD"; exit 1; fi
else
  usage
fi

# Same master source and tag as build.sh
TAG="$(sed -n 's/^TAG=//p' "$ROOT/build.sh")"
SRC="$ROOT/resumes/Jose_Tupayachi_Resume_$TAG.tex"
[ -f "$SRC" ] || { echo "Master resume not found: $SRC"; exit 1; }

exec python3 "$ROOT/tailor.py" "$JD" "$KIND" --src "$SRC" --tag "$TAG"
