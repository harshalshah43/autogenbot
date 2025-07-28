@echo off
REM Start Anaconda Prompt and run the Python script in the specified conda environment

REM Path to Anaconda's activate.bat (change this if your Anaconda is installed elsewhere)
CALL "D:\anaconda-install\condabin\activate.bat"

REM Activate your conda environment
CALL conda activate aiagent

REM Change to your script's directory
cd /d "D:\AIAgent\autogen\rfqbot"

REM Run your Python script
streamlit run appui.py

pause
