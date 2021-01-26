@echo off
echo "hoshino Restart"
taskkill /im python.exe
echo "hoshino Stop"
start python run.py
echo "hoshino Start"
exit