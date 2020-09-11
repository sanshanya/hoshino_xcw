@Echo Off&SetLocal ENABLEDELAYEDEXPANSION
FOR %%a in (*) do (
set "name=%%a"
set "name=!name: (=!"
set "name=!name:)=!"
ren "%%a" "!name!"
)
exit