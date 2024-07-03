::================================================================================================
::Script to install common dependencies package required for user or developer in windows platform
::================================================================================================
@echo off
:: index url and trusted host to be used for pip install
set index_url=https://artifactory.geo.conti.de/artifactory/api/pypi/c_adas_cip_pypi_v/simple
set trusted_host_url=artifactory.geo.conti.de
set "python_install_path=%~1"
set "python_exe_path=%python_install_path%\python.exe"


:: Steps
:: 1. Check if given input path exists
:: 2. Check if python python.exe exists
:: 3. Check and save python major & minor version
:: 4. Checking supported python version
:: 5. Install all common pip modules


:: Step 1. Check if given input path exists
if exist "%python_install_path%" (
    echo Python install path '%python_install_path%' exists on machine
) else (
    GOTO PYTHON_PATH_ERROR
)

:: Step 2. Check if python python.exe exists
if exist "%python_exe_path%" (
    echo Python executable found on machine at '%python_exe_path%'
) else (
    GOTO PY_EXE_ERROR
)

:: Step 3. Check and save python major & minor version
call "%python_exe_path%" -c "import sys; sys.exit(sys.version_info.major)"
set  PYTHON_MAJOR_VERSION=%errorlevel%
call "%python_exe_path%" -c "import sys; sys.exit(sys.version_info.minor)"
set  PYTHON_MINOR_VERSION=%errorlevel%
echo "PYTHON_MAJOR_VERSION: " %PYTHON_MAJOR_VERSION%
echo "PYTHON_MINOR_VERSION: " %PYTHON_MINOR_VERSION%
:: Here checking IF python major or minor versions are empty then exit
if %PYTHON_MAJOR_VERSION%=="" (
    echo "Python major version is empty"
    GOTO :EXIT
)
if %PYTHON_MINOR_VERSION%=="" (
    echo "Python minor version is empty"
    GOTO :EXIT
)

:: Step 4. checking supported python version
if %PYTHON_MAJOR_VERSION%==3 (
    if %PYTHON_MINOR_VERSION%==6 (
        GOTO RESUME
    ) else if %PYTHON_MINOR_VERSION% gtr 6 (
        GOTO RESUME
    ) else (
        GOTO PYTHON_VERSION_ERROR
    )
) else (
    GOTO PYTHON_VERSION_ERROR
)

:: Step 5. Install all common pip modules
:RESUME
echo Installing Python modules
"%python_exe_path%" -m pip install -i %index_url% --trusted-host %trusted_host_url% --upgrade pip setuptools wheel pipenv
GOTO :SUCCESS

:PY_EXE_ERROR
echo.
echo ----------------------------------- Python exe NOT FOUND -----------------------------------
echo '%python_exe_path%' not found
echo Please check if you installed Python correctly
echo ----------------------------------- Python exe NOT FOUND -----------------------------------
GOTO :EXIT
:PYTHON_PATH_ERROR
echo.
echo -------------------- PYTHON INSTALL PATH NOT FOUND --------------------
echo '%python_install_path%' not found
echo Please check if you gave correct path of your Python installation
echo -------------------- PYTHON INSTALL PATH NOT FOUND --------------------
GOTO :EXIT
:PYTHON_VERSION_ERROR
echo.
echo -------------------- PYTHON VERSION NOT FOUND --------------------
echo Supported Python versions are Python36, Python37, Python38 and Python39
echo Please check if you have installed Python36 or Python37 or Python38 or Python39
echo -------------------- PYTHON VERSION NOT FOUND --------------------
GOTO :EXIT
:EXIT
echo "Execution of pip common dependencies is failed"
exit /b 3
:SUCCESS
echo "Execution of pip common dependencies done successfully"
exit /b 0
