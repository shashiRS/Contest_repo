setlocal
cd %~dp0\..
pylint --enable=useless-suppression --exit-zero --rcfile=%~dp0\pylint.config --ignore mfile %~dp0\..
endlocal
