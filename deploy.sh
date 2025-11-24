#! /bin/bash
set -euo pipefail

while getopts "t:" arg; do
  case $arg in
    t) Tag=$OPTARG ;;
  esac
done

if [[ -z "${Tag:-}" ]]; then
  echo "Usage: $0 -t <tag>" >&2
  exit 1
fi

Version=${Tag#v}
export Version

# Update setup.py version from tag
python - <<'PY'
import os
import re
import sys
from pathlib import Path

version = os.environ["Version"]
path = Path("setup.py")
text = path.read_text()
new_text, count = re.subn(r'version\s*=\s*"[^\"]+"', f'version="{version}"', text, count=1)
if count != 1:
    sys.exit("Не удалось обновить версию в setup.py")
path.write_text(new_text)
PY

git add setup.py
git commit -m "Release ${Tag}"
git tag -a "${Tag}" -m "Version ${Tag}"
git push origin HEAD --tags
