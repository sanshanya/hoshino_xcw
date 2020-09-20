@echo off
echo "hoshino Restart"
taskkill /im py.exe
echo "hoshino Stop"
start py run.py
echo "hoshino Start"
exit