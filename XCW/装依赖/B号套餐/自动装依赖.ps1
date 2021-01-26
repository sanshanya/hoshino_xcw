Write-Host 'README:' -ForegroundColor Green
Write-Host '该脚本会自动搜索当前目录及其子目录下所有依赖配置文件并自动进行安装，故请将本脚本置于程序最外层目录。例如：D:\HoshinoBot' -ForegroundColor Green
Write-Host '请按任意键继续。' -ForegroundColor Green
[void][System.Console]::ReadKey($true)

$fileList = Get-ChildItem -Path $PSScriptRoot -Include requirements.txt -Recurse -ErrorAction SilentlyContinue -Force | % { $_.FullName }
$fileList2 = Get-ChildItem -Path $PSScriptRoot -Include requirement.txt -Recurse -ErrorAction SilentlyContinue -Force | % { $_.FullName }

Write-Host '已找到以下依赖配置文件: '-ForegroundColor Yellow
$fileList
$fileList2
sleep 2

Foreach ($file in $fileList) {
    py -3.8 -m pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r $file
}
Foreach ($file2 in $fileList2) {
    py -3.8 -m pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r $file2
}