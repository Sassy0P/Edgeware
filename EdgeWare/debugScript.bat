@echo off
:top
echo Which feature would you like to run?
echo 1: Start.py (Edgeware)
echo 2: Popup.py (Popup only)
echo 2a: Popup.py (Video only)
echo 3: Config.py (Config)
set /p usrSelect=Select number:
if %usrSelect%==1 goto startLbl
if %usrSelect%==2 goto popupLbl
if %usrSelect%==2a goto popup2Lbl
if %usrSelect%==3 goto configLbl
echo Must enter selection number (1, 2, 3)
pause
goto top
:startLbl
echo Running start.py...
py start.py
echo Done.
pause
goto quitLbl
:popupLbl
echo Running popup.py...
py popup.py
echo Done.
pause
goto quitLbl
:popup2Lbl
echo Running popup.py...
py popup.py -video
echo Done.
pause
goto quitLbl
:configLbl
echo Running config.py
py config.py
echo Done.
pause
:quitLbl
echo Goodbye!