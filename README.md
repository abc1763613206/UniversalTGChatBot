# UniversalTGChatBot

这是为 @AlexChunHK 打造的聊天机器人，适当修改后便可作通用使用。

## 使用配置
1. `pip install -r requirements.txt`
2. 复制一份 `config.sample.py` 为 `config.py` ，之后进行配置。

一般情况下您需要如下配置：

- `Token` ： 机器人的 Token (私聊 @BotFather)
- `USE_PROXY` : 跑在网络封锁地区，您可能需要启用一个代理
- `HTTP_PROXY` : 遵从 `request` 库的配置
- `AdminList` : 以列表形式填入 **字符串** 形式的 `userid`，通常为9位数字，可私聊发送 `/whoami` 获取！
- `USE_SENTRY` 与 `SENTRY_LINK` : [Sentry.io](https://sentry.io) 的错误追踪服务。
- `LOG_LEVEL` : 日志记录等级，INFO模式记录消息，ERROR模式只记录报错。 

## 使用说明

### 管理员设置

- 添加： `/setadmin @用户名` 
- 删除： `/rmadmin @用户名` 

#### 特别注意
此处添加的管理为二级管理，其权限不同于 [`config.py`](./config.py) 中 `AdminList` 写死的管理。        
但是基础权限全部具备，所以请谨慎操作！


### 语料库设置

- 匹配语库
  - 添加 : `/setquotes` 或 `/sq`
  - 删除 : `/rmquotes` 或 `/rq`
  
- 无匹配时回复
  - 添加 : `/settexts` 或 `/st`
  - 删除 : `/rmtexts` 或 `/rt`
 
#### 特别注意
- 此处为交互式添加，所以指令之后无需再附带内容
- 无匹配时的回复有一定几率匹配到一言，可通过 `config.py` 中的 `ifHITOKOTO` 项关闭。
- 语库使用了 `jieba` 分词，所以语库中可以只设置词语。

### 其他语段设置
`/setother` 或 `/so`
#### 特别注意
- 此处为交互式添加，所以指令之后无需再附带内容


### 管理员控制模式
管理员使用 `/handle` 开启或关闭。 
#### 特别注意
- 该功能类似 `Livegram` ，开启此模式后消息将转发给管理员处理。
- 理论上该模式能处理非文字消息，但是其他模式 **只能处理文字消息** 。


## 问题反馈
对于反馈的错误，您可以 TG 私聊 [@abc1763613206](https://t.me/abc1763613206) 中所列的账户，或在 Issues 区处理。
