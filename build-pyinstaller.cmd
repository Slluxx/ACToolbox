@echo off

pyinstaller --name ACToolbox --onefile --noconsole src/tool.py
REM C:\Program Files (x86)\Windows Kits\10\bin\10.0.22621.0\x64\signtool.exe sign /a /fd SHA256 /tr http://timestamp.digicert.com /td SHA256 dist/ACToolbox.exe