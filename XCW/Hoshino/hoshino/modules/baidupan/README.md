# 度盘直链解析

---
首先. 你得是SVIP. 其次才有下载速度


安装依赖
> pip install pyyaml -i https://pypi.tuna.tsinghua.edu.cn/simple


文件夹丢到modules目录下
需要到bot的配置里的 MODULES_ON 添加 'baidupan'

例如hoshinov2如下配置和路径

文件丢到 hoshino/modules/baidupan

修改文件添加模块 `hoshino/config/__bot__.py`
```python
MODULES_ON = {
   'baidupan',
}
```

---
### 需要到度盘获取cookie值填入config.yml中

---

命令  | 说明 | 例
------------- | ------------- | -------------
p#或pan#  | 解析一个度盘链接 | p#分享地址 提取码<br>p#秒传链接
https://pan.baidu.com/s/xxx#提取码 | 同上 | 同上
ru# | 获取秒传链接 | #ru分享地址 提取码
panhelp  | 显示链接下载帮助 | panhelp

# 鸣谢
[baiduwp](https://github.com/TkzcM/baiduwp) <br>
[BaiduPCS-Go](https://github.com/Angey40/BaiduPCS-Go) <br>
