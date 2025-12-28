# twip-napcat-ws

本地已验证能正常运行的python版本：3.13.2、3.13.11

## 用正向连接的twip

napcat配置服务端
twip驱动器选择websockets

/*
 * @Author: tanyongqiang 1157529280@qq.com
 * @Date: 2025-06-01 09:48:05
 * @LastEditors: tanyongqiang 1157529280@qq.com
 * @LastEditTime: 2025-06-03 16:11:57
 * @FilePath: \twip-napcat-ws\常用命令.txt
 * @Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
 */
=== 本地执行的
进入虚拟环境
.venv\Scripts\activate.ps1

安装复读机插件echo
pip install nonebot-plugin-echo

导出依赖列表
pip freeze > requirements.txt


=== 部署服务器linux
创建虚拟环境
python3 -m venv twipenv

服务器虚拟环境
source twipenv/bin/activate

安装依赖
pip install -r requirements.txt

检查依赖
pip freeze

直接停掉某个端口下的程序
lsof -t -i:8095 | xargs kill -9 2>/dev/null || echo "端口没有被占用"

启动机器人
nohup python bot.py > bot.log 2>&1 &

=== 其它
安装mysql
docker pull mysql:8
docker run --name=twip-mysql -e MYSQL_ROOT_PASSWORD=密码 -p 3306:3306 -d mysql:8

服务器安装mysql依赖的时候需要执行的
sudo apt-get update
sudo apt-get install python3-dev default-libmysqlclient-dev build-essential

加权限
chmod +x start_bot.sh



# 启动
./start_bot.sh start

# 停止
./start_bot.sh stop

# 重启
./start_bot.sh restart

# 查看状态
./start_bot.sh status



### 配置项（.env .env.dev .env.prod）

ENVIRONMENT=dev
DRIVER=~websockets
HOST=127.0.0.1
PORT=8000
ONEBOT_WS_URLS=["ws://你的napcatIP地址:放开的端口号"]

db_url="数据库IP"
db_card="账号"
db_pass="密码"
db_lib="数据库名"

SUPERUSERS=["超管QQ号"]
NICKNAME=["机器人昵称"]
COMMAND_START=["/", ""]
COMMAND_SEP=["."]
LOG_LEVEL=SUCCESS


### 2.权限
/tool/find_power/data 的 _power.json文件去掉_，并且填入相关的QQ号或者群号即可


### 3.功能
> 1.求签
怎么看？
左上好、右下坏、右上感觉好、左下感觉坏
线条越长越倾向，线条左右走平平淡淡、线条上下走整体好或坏
踩的点越多事件越多


### napcat配置（本机器人）
添加网络配置：Websocket Server
host:0.0.0.0
port:你在`ONEBOT_WS_URLS=`填写的url的端口号
上报自身消息：开
强制推送消息：开
其它默认，名字随便取


### 接入maiBot机器人（麦麦）
架构为：1个napcat + 2个机器人端（本机器人+麦麦机器人）
napcat配置
添加一个新的网络配置：Websocket Client
url：ws://adapters:8095（maiBot部署教程的默认地址）
上报自身消息：关
其它默认，名字随便取，此时这两个网络配置都需要开启（端口号需要不一样）




