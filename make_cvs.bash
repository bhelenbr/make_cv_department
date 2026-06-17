#!/bin/zsh

if (( $# < 2 )); then
  echo "Usage: $0 <string> <dir> [dir ...]" >&2
  echo "  <string>  passed as the first argument to test_cv.py" >&2
  echo "  <dir>     directory or directories to process" >&2
  exit 1
fi

arg="$1"
shift
args=(${(z)arg})

for file in "$@"; do
  echo "$file"
  if [[ -d "$file/make_cv/CV" ]]; then
    cd "$file/make_cv/CV" || exit 1
    test_cv.py "${args[@]}"
    cd - >/dev/null || exit 1
  else
    echo "Skipping missing directory: $file/make_cv/CV" >&2
  fi
done
