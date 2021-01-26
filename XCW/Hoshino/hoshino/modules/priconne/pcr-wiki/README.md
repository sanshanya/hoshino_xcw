# pcr-wiki插件

本插件需配合[Hoshino(v2)](https://github.com/Ice-Cirno/HoshinoBot)使用

数据搬运于[蘭德索爾圖書館](https://pcredivewiki.tw/)，图片资源来源[干炸里脊资源站](https://redive.estertion.win/)

## 功能

- **[@bot简介ue] 角色简介**：查询角色简介
- **[@bot技能ue] 角色技能**：查询角色技能
- **[@bot专武ue] 角色专武**：查询角色专武
- **[@bot羁绊ue] 角色羁绊**：查询角色羁绊
- **启用wiki**：启用wiki
- **禁用wiki**：禁用wiki

## 部署

1. 将本项目的`wiki`文件夹复制到`hoshino/modules/priconne`下

2. 安装`requirements.txt`

3. 将本项目的`skill`与`equipment`文件夹复制到`res/img/priconne`文件夹下面

   > 实际上，只需要新建`skill`与`equipment`文件夹并把`skill`下的`icon_skill_ap01.png`、`icon_skill_ap02.png`、`icon_skill_attack.png`、`icon_skill_tack.png`四个图片复制过去就好，其他没有的图片使用时会自动下载

4. 重启Hoshino

   > 注意：**不要**在hoshino的配置文件添加模块。
   >
   > 注意：**不要**把`spider`文件夹及该文件夹下的文件任何文件放到`hoshino`下

至此，你可以开始使用插件了。

插件的数据源自文件夹下的`data.db`，wiki有更新时需要对应更新（我尝试过实时拉取数据，速度太慢，所以改用数据库存储），`data.db`会不定时更新(Releases里下载，一般在图书馆更新了新角色，新专武后我会更新)，如果你想要自己手动更新，请看下一小节

## 更新数据

> 强烈建议在windows机器上更新数据，更为快速方便。`spider`文件夹仅作更新数据使用，**不要**把这个文件夹混入`hoshino`的任何目录，它是独立的

#### windows

1. 打开`spider`文件夹，安装`requirements.txt`

2. 将你需要更新的`data.db`准备好

3. 安装chrome浏览器，并查看chrome版本

4. http://npm.taobao.org/mirrors/chromedriver/ 下载最为接近你的chrome版本的驱动

   > **不要**双击运行解压得到的exe文件，看下一步！

5. 打开`run.py`按照注释修改对应处（第24、27、35行），打开`data.py`按照注释修改第3行

6. 将你最新的`_pcr_data.py`复制到`spider`文件夹下替换（保证`spider/_pcr_data.py`里有你需要更新的id信息）

7. 运行`run.py`

8. 若无报错，则更新成功，得到最新的`data.db`，替换掉你`hoshino/modules/priconne/wiki`下的同名件

#### Linux

1. 将`spider`文件夹复制到服务器，打开该文件夹，安装`requirments.txt`

2. 将你需要更新的`data.db`准备好

3. 安装chrome浏览器，并查看chrome版本

   依次运行以下命令（第二行大概率会报错，不用管，但必须运行）

   ```
   wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
   sudo dpkg -i google-chrome-stable_current_amd64.deb
   sudo apt-get install -f
   sudo dpkg -i google-chrome-stable_current_amd64.deb
   sudo apt-get install xvfb
   google-chrome --version
   ```

4. http://npm.taobao.org/mirrors/chromedriver/ 下载最为接近你的chrome版本的驱动

5. 打开`run.py`按照注释修改对应处（第24、27、35行），打开`data.py`按照注释修改第3行

6. 将你最新的`_pcr_data.py`复制到`spider`文件夹下替换（保证`spider/_pcr_data.py`里有你需要更新的id信息）

7. 运行`run.py`

8. 若无报错，则更新成功，得到最新的`data.db`，替换掉你`hoshino/modules/priconne/wiki`下的同名件

