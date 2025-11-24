@echo off
setlocal enabledelayedexpansion

if "%~1"=="" (
    echo Usage: %~nx0 ^<tag^>
    exit /b 1
)

set "Tag=%~1"
set "Version=%Tag%"
if /i "%Version:~0,1%"=="v" set "Version=%Version:~1%"

REM Update setup.py version from tag
python -c "import re, sys, pathlib; p = pathlib.Path('setup.py'); t = p.read_text(); new, c = re.subn(r'version\s*=\s*\"[^\"]+\"', 'version=\"%Version%\"', t, 1); (c==1) or sys.exit('Не удалось обновить версию в setup.py'); p.write_text(new)"
if errorlevel 1 exit /b 1

git add setup.py
git commit -m "Release %Tag%"
git tag -a %Tag% -m "Version %Tag%"
git push origin HEAD --tags

endlocal
