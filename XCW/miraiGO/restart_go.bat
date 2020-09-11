@echo off
echo "GO Restart"
taskkill /im go-cqhttp.exe
echo "GO Stop"
start go-cqhttp.exe
echo "GO Start"
exit