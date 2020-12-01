# 表情包生成器

这是一个用于生成表情包的插件，适用HoshinoBot v2。

## 安装

安装fonts文件夹中1.ttf字体。

根据自己的文件安放位置更改nokia.py 52行图片位置

将整个snitchgenerator文件夹放入hoshino/modules中，并在config/__bot__.py里的模块列表中加入snitchgenerator。

## 使用

### 命令

本插件的命令有：

- ```/nokia <文案> | 生成一张内鬼表情包```：生成一张内鬼表情包

### 示例

欲生成一张表情包，可发：```/nokia 有内鬼 终止交易```。

文案不建议过长，否则文字会很小。文字的大小取决于文案的长度。

Demo picture: ![](./demo.png)

## 已知问题

- 若文案中英混杂，可能有排版错误
- 若表情图过大，可能会发送失败

本插件未经充分测试，若发现bug，希望能提交issue。万分感谢。

## 开源

本插件以GPL-v3协议开源。[项目地址](https://gitee.com/MarvelousXiang/snitchgenerator)
