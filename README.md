# paddlehub-task\_mgr\_bot

本例子展示通过task\_mgr\_bot插件 增强的 Wechaty 的微信闲聊机器人如何远程控制操作系统。通过Wechaty获取微信接收的消息，并且根据RPA和SNS社交属性对信息包括，发送人、聊天室、推送进行分析并进行命令管理，实现比闲聊更有价值的自动化远程管理功能

## 风险提示

本项目采用的api为第三方——Wechaty提供，**非微信官方api**，用户需承担来自微信方的使用风险。  
在运行项目的过程中，建议尽量选用**新注册的小号**进行测试，不要用自己的常用微信号。

## Wechaty

关于Wechaty和python-wechaty，请查阅以下官方repo：
- [Wechaty](https://github.com/Wechaty/wechaty)
- [python-wechaty](https://github.com/wechaty/python-wechaty)
- [python-wechaty-getting-started](https://github.com/wechaty/python-wechaty-getting-started/blob/master/README.md)
- [paddlehub-wechat-demo](https://github.com/KPatr1ck/paddlehub-wechaty-demo)


## 环境准备

- 系统环境：Linux
- python3.7+
- docker


## 安装和使用

1. Clone本项目代码

   ```shell
   git clone git@github.com:yiakwy/paddlehub-task_mgr_bot.git
   cd paddlehub-task_mgr_bot.git
   ```

2. 安装依赖 ——闲聊功能由paddlehub提供，paddlepaddle, paddlehub, wechaty

   ```shell
   pip install -r requirements.txt
   ```

    此demo以`plato-mini`为示例，其他module根据项目所需安装，更多的模型请查阅[PaddleHub官网](https://www.paddlepaddle.org.cn/hublist)。
   ```shell
   hub install plato-mini==1.0.0
   ```

3. 支持Pad协议以及Padlocal和Paimon口令

    在当前系统的环境变量中，配置以下与`WECHATY_PUPPET`相关的两个变量。
    关于其作用详情和TOKEN的获取方式，请查看[Wechaty Puppet Services](https://wechaty.js.org/docs/puppet-services/)。
    ```shell
    export WECHATY_PUPPET_SERVICE_TOKEN=your_token_at_here
    mv env.sh.bak env.sh
    source env.sh
    ```
    
    PadLocal口令目前不支持wechaty-python，但我们可以通过搭建wechaty代理服务器，使得wechaty-python客户端可以正常使用:
    ```shell
    # 启动wechaty-es6 padlocal代理服务器:
    bash scripts/wechaty_token_gateway_padlocal.sh

    # 若非公网，修改 env.sh EndPoint 地址到局域网地址端口
    export WECHATY_PUPPET_SERVICE_ENDPOINT="YOUR_DOCKER_PROXY_SERVER_ENDPOINT"

    # 代理服务器会自动发现
    # Docker镜像代理服务器运行后，可以通过浏览器复制qr码地址，用微信移动端扫码登陆，登陆成功后则可收发消息。
    ```

    Paimon可以参考下面文档：
    [Paimon](https://wechaty.js.org/docs/puppet-services/paimon/)。

4. 运行机器人

   ```shell
   python examples/paddlehub-task_mgr_bot.py
   ```

   启动后则可以通过python客户端，响应消息

## 运行效果

通过TaskMgrPlugin插件，用户可进行远程服务器访问，包括手机查询GPU机器占用，负载，以及远程调用和文件读取。

![bot-test-1](https://user-images.githubusercontent.com/8510840/126877912-8998ae56-e837-40a8-9edd-bf45f62ea27b.jpeg)
![bot-test-2](https://user-images.githubusercontent.com/8510840/126877916-8c916e39-821b-48c1-b84f-0baaf36c5e2c.jpeg)
![bot-test-3](https://user-images.githubusercontent.com/8510840/126877920-3f7d0864-e375-4ad3-a10c-aaa452b654ed.jpeg)
![bot-test-4](https://user-images.githubusercontent.com/8510840/126877923-6b351e32-1d83-4d96-be5c-19d63c76e487.jpeg)

