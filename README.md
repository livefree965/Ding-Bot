# Ding Bot
一个基于python-telegram-bot开发的项目，项目的初衷是为了让用户能够及时获取需要的推送，在未来，该项目会加入更多诸如股市监控，商品价格监控等日常实用信息，用户可根据自己的需求选择开启某几个模块。利用该项目，用户能够便捷地在服务器上部署相关的Bot后台，在众多场景中高效地获取消息，并将相关服务分享给好友。

项目目前仅提供淘宝及天猫的商品监控功能，使用上，用户可以便捷地发送App的分享链接给Bot直接进行添加，当商品上架时，用户会连续三次收到来自Bot的消息。在监控频率上，项目提供了有限的监控，避免因此造成服务器负担过大，仅作为实验性质的使用。

如果项目造成侵权，请在项目内发ISSUE告知。

## Table of Contents

- [Install](#install)
- [Usage](#usage)
- [Example Config](#example-config)
- [Running Display](#running-display)

## Install

项目基于Python3开发，请确保有相关环境

1. `pip install -r requirements.txt`安装相关依赖包
2. *main.py*为主入口，首次运行会生成*config.ini*，需要填充**token**，**proxy**可留空
3. 再次运行*main.py*即可使用，log默认保存为*telegram.log*，数据默认保存为*telegram.db*

## Usage

首先需要创建一个Bot，在客户端搜索@BotFather发送`/newbot`指令即可，按提示提交信息后即可获取到token，运行项目后直接向自己的Bot发送消息即可使用

目前bot支持以下几种命令：

1. 使用指令`/area`可以设置地区，往后的查询都将查询属于自己地区的商品库存，该命令可以重复使用，会覆盖之前的设置

2. 在淘宝/天猫的商品页面点击分享按钮，方式选择复制链接，然后将剪贴板的内容发送给Bot即可自动将商品加入监控
3. 使用指令`/del`可以删除监控商品，Bot会返回标签为商品名的按钮，点击即可删除
4. 使用指令`/list`可以展示自己当前设定的地区和监控的商品列表
5. 使用指令`/status`可以查看服务器的监控情况，该线程每分钟请求一次接口，可根据历史数据确定接口是否正常
6. 指令`/start`提供了简单的文本说明

## Example Config

```Python
token = 96123456:AABBCCCd0
proxy_url = socks5://127.0.0.1:10808 #HTTP ALSO
```

## Running Display

![Pic1.jpg](https://i.loli.net/2020/02/09/ZLQlhAStNjYCo5c.jpg)