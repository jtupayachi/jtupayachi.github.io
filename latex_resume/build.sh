#!/usr/bin/env bash
# Builds the industry and teaching resumes (tagged MMDDYYYY) in resumes/,
# then publishes the industry PDF as main.pdf for the website.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT/resumes"
TAG=11022026
SRC=Jose_Tupayachi_Resume_$TAG
NAME="Jose Alberto Tupayachi Silva - Resume-$TAG"
build() { # $1 = suffix, $2 = preamble
  for _ in 1 2; do
    pdflatex -interaction=nonstopmode -halt-on-error -jobname="build_$1" "$2\\input{$SRC.tex}" >/dev/null \
      || { echo "LaTeX error while building '$1' resume:"; grep -A3 '^!' "build_$1.log" | head -n 8; rm -f build_$1.*; exit 1; }
  done
  mv "build_$1.pdf" "$NAME""_$1.pdf"
  rm -f build_$1.aux build_$1.log build_$1.out
}
build ind ""
build Teaching "\\def\\TEACHING{1}"
cp "$NAME""_ind.pdf" "$ROOT/main.pdf"
echo "Built: resumes/$NAME""_ind.pdf, resumes/$NAME""_Teaching.pdf -> main.pdf"
