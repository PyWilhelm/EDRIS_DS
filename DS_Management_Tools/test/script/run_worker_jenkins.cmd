taskkill /F /IM dymosim.exe
set DIR=%~dp0\..\..\..\EDRIS_Worker_devel
set PYTHON_PATH=C:\softwares\WinPython-64bit-2.7.6.4\python-2.7.6.amd64
set PATH=%PYTHON_PATH%;%PATH%
cd "%DIR%"
python run.py jenkins