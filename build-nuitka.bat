@echo off

REM --windows-icon-from-ico=your-icon.png
REM --windows-disable-console
REM --onefile 
REM --noinclude-setuptools-mode=nofollow --noinclude-pytest-mode=nofollow 
python -m nuitka --standalone --onefile --windows-disable-console --noinclude-setuptools-mode=nofollow --noinclude-pytest-mode=nofollow src/tool.py