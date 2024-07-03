::==========================================================================
::Script to install all the needed dependencies package for windows platform
::==========================================================================

@echo off
:: index url and trusted host to be used for pip install
set index_url=https://artifactory.geo.conti.de/artifactory/api/pypi/c_adas_cip_pypi_v/simple
set trusted_host_url=artifactory.geo.conti.de
:: following input is to run this script within either jenkins env where we have known paths or with user given path
:: jenkins_mode --> is for supporting the use of this script in contest jenkins pipeline
:: user/auto_mode --> is for backward compatibility of this script where user give python installation path as input
set input_arg=%~1

:: checking if script is running in jenkins env
IF %1.==. (
    GOTO USER_MODE
) ELSE (
    GOTO DETECT_MODE
)

:: Steps
:: Step 1. Taking python installation path from user in-case of user mode else setting paths for jenkins mode/automode
:: Step 2. Check if python installation path exists
:: Step 3. Check if python.exe exists in installation path
:: Step 4. Check if user gave base python location or a virtual env location
:: Step 5. Ask user about venv creation if base python location was given else ignore
:: Step 6. Create venv if user requested
:: Step 7. Install pip modules in newly created venv or base python if venv creation ignored by user

:: Step 1. Setting python installation paths incase use provided input
:DETECT_MODE
if "%input_arg%" == "jenkins" (
    echo Jenkins mode detected
    GOTO SET_JENKINS_PATHS
) else (
    echo User gave python install path as argument
    GOTO SET_USER_PATHS
)

:SET_JENKINS_PATHS
set python_install_path=.\venv\Scripts
set python_exe_path=%python_install_path%\python.exe
GOTO INSTALL_MODS

:SET_USER_PATHS
set python_install_path=%input_arg%
set python_exe_path=%python_install_path%\python.exe
GOTO INSTALL_MODS

:: Step 1. Asking for python installation paths as user mode detected
:USER_MODE
echo.
echo =====================================================================================================
echo                                       Python Exe Path
echo =====================================================================================================
echo Please provide Python installation path i.e. the path where python.exe is located
echo You can also provide Python virtual environment exe location (if exists)
echo.
echo Example:
echo.
echo    C:\LegacyApp\Python\Python39 (Path in-case of base Python)
echo    D:\my_awesome_venv\Scripts   (Path in-case of virtual environment created at D:\my_awesome_venv)
echo.
echo =====================================================================================================
echo.
set /p "python_install_path=Please provide location of python.exe [check info above]: "
set "python_exe_path=%python_install_path%\python.exe"

:: Step 2. Check if python installation path exists
if exist "%python_install_path%" (
    echo Python install path '%python_install_path%' exists on machine
) else (
    GOTO PYTHON_PATH_ERROR
)

:: Step 3. Check if python.exe exists in installation path
if exist "%python_exe_path%" (
    echo Python executable found on machine at '%python_exe_path%'
) else (
    GOTO PY_EXE_ERROR
)

:: Step 4. Check if user gave base python location or a virtual env location
call "%python_exe_path%" -c "import sys; is_base = 1 if sys.prefix == sys.base_prefix else 0; sys.exit(is_base)"
set  is_base=%errorlevel%

:: Step 5. Ask user about venv creation if base python location was given else ignore
if %is_base%==1 (
    echo.
    echo ===================================================================================================================
    echo                                 Python Virtual Environment Creation
    echo ===================================================================================================================
    echo Python installation path is given for a base python, you have an option to create python virtual environment
    echo.
    echo What is Python Virtual Environment and how will it help?
    echo.
    echo Python Virtual Environment will be a separate Python environment on your machine.
    echo.
    echo Virtual Environment will be created using base python %python_exe_path%
    echo.
    echo Python pip modules required for an application e.g. ConTest can be installed separately in virtual environment.
    echo In this way, the main Python installation will be clean and virtual environment can be used to run the application.
    echo.
    echo ===================================================================================================================
    echo.
    GOTO :ASK_VENV_QUEST
) else (
    echo Python virtual environment path given
    GOTO :INSTALL_MODS
)

:ASK_VENV_QUEST
set /p "venv_yes=Would you like to create a Python Virtual Environment [Read Info Above]? (y/n) "
if %venv_yes% NEQ y (
    if %venv_yes% NEQ n (
        echo Please provide correct input for virtual environment creation i.e. 'y' for yes and 'n' for no
        pause
        GOTO :eof
    ) else (
        echo Creation of Virtual Environment ignored, the python modules shall be installed in Python interpreter at %python_install_path%
        GOTO :INSTALL_MODS
    )
) else (
    GOTO :VENV
)

:: Step 6. Create venv if user requested
:VENV
echo.
set /p "venv_dir=Good choice ! Now, Please provide the location where you want to create virtual environment: "
set /p "venv_name=Please provide the name of virtual environment e.g. 'my_awesome_venv': "
set "venv_loc=%venv_dir%\%venv_name%"
if exist "%venv_dir%" (
    if exist "%venv_loc%" (
        echo An environment with name '%venv_name%' already exists at '%venv_dir%', please select a different name
        pause
        GOTO :eof
    )
    echo.
    echo Location for virtual environment creation '%venv_dir%' exists on machine
    echo Preparing to create virtual environment, please wait ...
    echo.
    "%python_exe_path%" -m pip install -i %index_url% --trusted-host %trusted_host_url% pipenv
    echo.
    echo Python virtual environment shall be created at '%venv_loc%' location, please wait ...
    echo.
    "%python_exe_path%" -m venv "%venv_loc%"
    set python_install_path=%venv_loc%\Scripts
    set python_exe_path=%venv_loc%\Scripts\python.exe
    echo.
    echo Python virtual environment created successfully at %venv_loc%
    echo.
    GOTO :INSTALL_MODS
) else (
    echo.
    echo Location for virtual environment creation '%venv_dir%' does not exist on machine, please provide correct location
    pause
    GOTO :eof
)

:: Step 7. Install pip modules in newly created venv or base python if venv creation ignored by user
:INSTALL_MODS
echo ===================================================================================================================
echo                        Python modules shall be installed in %python_exe_path%
echo ===================================================================================================================
call %~dp0\install_scripts\install_pip_common_dependencies.bat "%python_install_path%"
echo Error Code %errorlevel%
IF %errorlevel% NEQ 0  (
    echo Installing of pip user dependencies is Failed
    pause
    exit /b
    )
"%python_exe_path%" -m pip install -i %index_url% --trusted-host %trusted_host_url% -r "%~dp0\install_scripts\dependencies_user.txt"
echo.
echo =================================================================================
echo                        All Modules installed successfully
echo                Please use %python_exe_path% for starting ConTest
echo =================================================================================
:: following if-else statement is added in order to unblock script execution in automation (jenkins)
:: when user provided a default path for installation
if "%input_arg%" == "" (
    pause
    GOTO :eof
) else (
    GOTO :eof
)

:PY_EXE_ERROR
echo.
echo ============================================ Python exe NOT FOUND ===================================
echo '%python_exe_path%' not found
echo Please check if you installed Python correctly
echo ============================================ Python exe NOT FOUND ===================================
pause
GOTO :eof

:PYTHON_PATH_ERROR
echo.
echo =================================== PYTHON INSTALL PATH NOT FOUND ===================================
echo '%python_install_path%' not found
echo Please check if you gave correct path of your Python installation
echo =================================== PYTHON INSTALL PATH NOT FOUND ===================================
pause
GOTO :eof
