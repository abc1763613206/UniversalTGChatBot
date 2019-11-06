import os
import sys
import string
import random
import time
import subprocess
import traceback
from time import sleep
import json

def getReportID():
    seed = "1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    sa = []
    for i in range(8):
        sa.append(random.choice(seed))
    salt = ''.join(sa)
    return salt


if not os.path.exists("config.py"):
    print("Error: 配置文件不存在，请检查是否正确配置！")
    exit(0)
import config

if not os.path.exists("data.json"):
    print("Error: 数据文件不存在，请检查是否正确配置！")
    exit(0)

try: # 向下兼容
    if config.USE_SENTRY : # Bug Tracker
        import sentry_sdk
        sentry_sdk.init(config.SENTRY_LINK)
except Exception as e:
    ret = str(e)


from data import *

import logging
import telebot
bot = telebot.TeleBot(config.TOKEN)
from telebot import apihelper
from telebot import types
from telebot import util
from jieba import analyse

import requests

if config.USE_PROXY:
    apihelper.proxy = config.HTTP_PROXY
#telebot.logger.setLevel(logging.DEBUG)

logging.basicConfig(level=logging.INFO)


f = open('data.json','r',encoding='utf-8',errors='ignore')
jsdata = json.load(f)
#print(jsdata)
f.close()

welcome_msg = jsdata['welcome_msg']
text_not_supported = jsdata['text_not_supported']
data_saved = jsdata['data_saved']
demo_mode_on = jsdata['demo_mode_on']
demo_mode_off = jsdata['demo_mode_off']
not_admin = jsdata['not_admin']
quotes = jsdata['quotes']
texts = jsdata['texts']
jsadmins = jsdata['admins'] # see data.comment



def SetData():
    logging.info('重载设置中')
    global welcome_msg
    global text_not_supported
    global data_saved
    global demo_mode_on
    global demo_mode_off
    global not_admin
    global quotes
    global texts
    global jsadmins
    welcome_msg = jsdata['welcome_msg']
    text_not_supported = jsdata['text_not_supported']
    data_saved = jsdata['data_saved']
    demo_mode_on = jsdata['demo_mode_on']
    demo_mode_off = jsdata['demo_mode_off']
    not_admin = jsdata['not_admin']
    quotes = jsdata['quotes']
    texts = jsdata['texts']
    jsadmins = jsdata['admins']

SetData()

def SaveJson():
    logging.info('保存设置中')
    newdata = {
        'welcome_msg' : welcome_msg,
        'text_not_supported' : text_not_supported,
        'data_saved' : data_saved,
        'demo_mode_on' : demo_mode_on,
        'demo_mode_off' : demo_mode_off,
        'not_admin' : not_admin,
        'quotes' : quotes,
        'texts' : texts,
        'admins' : jsadmins
    }
    f1 = open('data.json','w+',encoding='utf-8',errors='ignore')
    json.dump(newdata,f1)
    f1.close()
    f = open('data.json', 'r', encoding='utf-8', errors='ignore')
    global jsdata
    jsdata = json.load(f)
    #print(jsdata)
    f.close()
    SetData()

def SaveSetJson():
    logging.info('保存新设置中')
    global jsdata
    f1 = open('data.json','w+',encoding='utf-8',errors='ignore')
    json.dump(jsdata,f1)
    f1.close()
    f = open('data.json', 'r', encoding='utf-8', errors='ignore')

    jsdata = json.load(f)
    #print(jsdata)
    f.close()
    SetData()

StateAdmin = { # 当前状态
    '' : ''
}

StateAdminEnd = {
    '' : ''
}

HandledAdmins = []


# init end


#logger = telebot.logger
#telebot.logger.setLevel(logging.DEBUG)




@bot.message_handler(commands=['start','help'])
def send_welcome(message):
    logging.info(message.text)
    bot.reply_to(message,welcome_msg)

def checkAdminMode(message):
    userid = str(message.from_user.id)
    username = str(message.from_user.username)
    if ifDemo == 1:
        return False
    else :
        if (userid in config.AdminList) or (userid in jsadmins):
            return True
        return False

def checkFullAdminMode(message):
    userid = str(message.from_user.id)
    if ifDemo == 1:
        return False
    else :
        if (userid in config.AdminList):
            return True
        return False


@bot.message_handler(commands=['setadmin']) # jsadmins
def set_jsadmin(message):
    if checkFullAdminMode(message) == True:  # 这里的设定是动态添加的管理不能再添加新管理
        ts = str(message.text)
        ts = ts.replace('/setadmin','')
        ts = ts.replace('@','')
        ts = ts.replace(' ','')
        if ts == '':
            pass
        set_username = ts
        bot.reply_to(message,'您已设置@{0}为二级管理员(无添加新管理员权限)。\n输入 /rmadmin {0} 可撤销管理员！'.format(set_username))
        jsadmins.append(set_username)
        SaveJson()
    else:
        bot.reply_to(message, not_admin)


@bot.message_handler(commands=['rmadmin'])  # jsadmins
def rm_jsadmin(message):
    if checkFullAdminMode(message) == True:  # 这里的设定是动态添加的管理不能再添加新管理
        ts = str(message.text)
        ts = ts.replace('/rmadmin', '')
        ts = ts.replace('@', '')
        ts = ts.replace(' ', '')
        set_username = ts
        bot.reply_to(message, '您已删除@{0}的二级管理员权限\n输入 /setadmin {0} 可重新添加！'.format(set_username))
        jsadmins.remove(set_username)
        SaveJson()
    else:
        bot.reply_to(message, not_admin)


def randText():
    ifhitokoto = random.randint(0,5) # 随机使用一言接口
    if ifhitokoto == 0:
        r = requests.get('https://v1.hitokoto.cn/?encode=text')
        return r.text
    else:
        return random.choice(texts)

def Process(text):
    if text in quotes:
        return random.choice(quotes[text])
    else:
        tfidf = analyse.extract_tags
        keywords = tfidf(text)
        logging.info("未找到，使用jieba切分：")
        for keyword in keywords:
            logging.info(keyword)
            if keyword in quotes:
                return random.choice(quotes[keyword])
        print()
        return randText()



ifDemo = 0 # Demo模式，管理员当普通用户看待，重启后状态即失效




@bot.message_handler(commands=['demo']) # demo模式
def demo_mode(message):
    try:
        if checkAdminMode(message) == True :
            ifDemo = 1
            if userid in HandledAdmins:
                HandledAdmins.remove(userid)
            bot.reply_to(message,demo_mode_on)
        else :
            userid = str(message.from_user.id)
            if userid in config.AdminList:
                ifDemo = 0
                bot.reply_to(message,demo_mode_off)
            else:
                bot.reply_to(message,not_admin)
    except Exception as e:
        rid = getReportID()
        traceback.print_exc()
        logging.error(str(rid + '::' + str(repr(e)) + '\n' + traceback.format_exc()))
        bot.send_message(message.from_user.id,'抱歉，我出现错误，识别ID为 '+rid+'\n\n信息如下：\n'+str(repr(e))+'\n\n请将这条信息 Forward 给 @abc1763613206 中所列的用户 进行处理！')


@bot.message_handler(commands=['save','sv'])
def save_data(message):
    try:
        if checkAdminMode(message) == True :
            SaveJson()
            bot.reply_to(message,data_saved)
        else:
            bot.reply_to(message,not_admin)
    except Exception as e:
        rid = getReportID()
        traceback.print_exc()
        logging.error(str(rid + '::' + str(repr(e)) + '\n' + traceback.format_exc()))
        bot.send_message(message.from_user.id,'抱歉，我出现错误，识别ID为 '+rid+'\n\n信息如下：\n'+str(repr(e))+'\n\n请将这条信息 Forward 给 @abc1763613206 中所列的用户 进行处理！')

@bot.message_handler(commands=['setquotes','sq'])
def set_quotes(message):
    userid = str(message.from_user.id)
    chatid = str(message.chat.id)
    try:
        if checkAdminMode(message) == True :
            StateAdminEnd[userid] = ''
            markup = types.ForceReply(selective=False)
            bot.send_message(chatid, '请输入您要定义的语段(输入-1终止)：', reply_markup=markup)
            StateAdmin[userid] = '#SettingQuotes1#'
        else :
            bot.reply_to(message,not_admin)
    except Exception as e:
        rid = getReportID()
        traceback.print_exc()
        logging.error(str(rid + '::' + str(repr(e)) + '\n' + traceback.format_exc()))
        bot.send_message(message.from_user.id,'抱歉，我出现错误，识别ID为 '+rid+'\n\n信息如下：\n'+str(repr(e))+'\n\n请将这条信息 Forward 给 @abc1763613206 中所列的用户 进行处理！')

@bot.message_handler(commands=['settexts','st'])
def set_texts(message):
    userid = str(message.from_user.id)
    chatid = str(message.chat.id)
    try:
        if checkAdminMode(message) == True :
            StateAdminEnd[userid] = ''
            markup = types.ForceReply(selective=False)
            bot.send_message(chatid, '请输入您要定义的无命中时回复语段(输入-1终止)：', reply_markup=markup)
            StateAdmin[userid] = '#SettingTexts#'
        else :
            bot.reply_to(message,not_admin)
    except Exception as e:
        rid = getReportID()
        traceback.print_exc()
        logging.error(str(rid + '::' + str(repr(e)) + '\n' + traceback.format_exc()))
        bot.send_message(message.from_user.id,'抱歉，我出现错误，识别ID为 '+rid+'\n\n信息如下：\n'+str(repr(e))+'\n\n请将这条信息 Forward 给 @abc1763613206 中所列的用户 进行处理！')

@bot.message_handler(commands=['rmquotes','rq'])
def rm_quotes(message):
    userid = str(message.from_user.id)
    chatid = str(message.chat.id)
    try:
        if checkAdminMode(message) == True :
            StateAdminEnd[userid] = ''
            markup = types.ForceReply(selective=False)
            if quotes == {[]}:
                bot.send_message(chatid, '您似乎并没有定义回复！')
                return
            bot.send_message(chatid,'正在以数组形式输出回复列表')
            for i in quotes:
                if quotes[i] != []:
                    bot.send_message(chatid,str(i)+' -> '+str(quotes[i]))
            bot.send_message(chatid, '请输入您要管理的回复(输入-1终止)：', reply_markup=markup)
            StateAdmin[userid] = '#RemoveQuotes1#'
        else :
            bot.reply_to(message,not_admin)
    except Exception as e:
        rid = getReportID()
        traceback.print_exc()
        logging.error(str(rid + '::' + str(repr(e)) + '\n' + traceback.format_exc()))
        bot.send_message(message.from_user.id,'抱歉，我出现错误，识别ID为 '+rid+'\n\n信息如下：\n'+str(repr(e))+'\n\n请将这条信息 Forward 给 @abc1763613206 中所列的用户 进行处理！')


@bot.message_handler(commands=['rmtexts','rt'])
def rm_texts(message):
    userid = str(message.from_user.id)
    chatid = str(message.chat.id)
    try:
        if checkAdminMode(message) == True:
            StateAdminEnd[userid] = ''
            markup = types.ForceReply(selective=False)
            if texts == []:
                bot.send_message(chatid, '您似乎并没有定义无回复命中语段！')
                return
            bot.send_message(chatid, '正在打印回复清单')
            for i in texts:
                bot.send_message(chatid, str(texts[i]))
            bot.send_message(chatid, '请输入您要删除的回复(输入-1终止)：', reply_markup=markup)
            StateAdmin[userid] = '#RemoveTexts#'
        else:
            bot.reply_to(message, not_admin)
    except Exception as e:
        rid = getReportID()
        traceback.print_exc()
        logging.error(str(rid + '::' + str(repr(e)) + '\n' + traceback.format_exc()))
        bot.send_message(message.from_user.id, '抱歉，我出现错误，识别ID为 ' + rid + '\n\n信息如下：\n' + str(
            repr(e)) + '\n\n请将这条信息 Forward 给 @abc1763613206 中所列的用户 进行处理！')

@bot.message_handler(commands=['setother','so'])
def set_others(message):
    userid = str(message.from_user.id)
    chatid = str(message.chat.id)
    try:
        if checkAdminMode(message) == True:
            StateAdminEnd[userid] = ''
            markup = types.ForceReply(selective=False)
            if texts == []:
                bot.send_message(chatid, '您似乎并没有定义无回复命中语段！')
                return
            bot.send_message(chatid, '正在打印设置清单')
            for i in jsdata:
                bot.send_message(chatid, str(i)+'('+comment[str(i)]+') -> '+str(jsdata[i]))
            bot.send_message(chatid, '请输入您要修改的内容(输入-1终止)：', reply_markup=markup)
            StateAdmin[userid] = '#Settings1#'
        else:
            bot.reply_to(message, not_admin)
    except Exception as e:
        rid = getReportID()
        traceback.print_exc()
        logging.error(str(rid + '::' + str(repr(e)) + '\n' + traceback.format_exc()))
        bot.send_message(message.from_user.id, '抱歉，我出现错误，识别ID为 ' + rid + '\n\n信息如下：\n' + str(
            repr(e)) + '\n\n请将这条信息 Forward 给 @abc1763613206 中所列的用户 进行处理！')


@bot.message_handler(commands=['handle'])
def handle_mode(message):
    userid = str(message.from_user.id)
    chatid = str(message.chat.id)
    try:
        if checkAdminMode(message) == True:
            if chatid in HandledAdmins:
                HandledAdmins.remove(chatid)
                logging.info(str('UnHandled::@{} ({} {}): {}'.format(message.from_user.username,
                                                              message.from_user.first_name,
                                                              message.from_user.last_name, message.text)))
                bot.reply_to(message,'已退出控制模式！')
            else:
                logging.info(str('Handled::@{} ({} {}): {}'.format(message.from_user.username,
                                                              message.from_user.first_name,
                                                              message.from_user.last_name, message.text)))
                HandledAdmins.append(chatid)
                bot.reply_to(message,'已成功开启控制模式(机器人重启后状态消失)，机器人将不会根据词库处理消息，回复对应的消息即可处理，关闭请发送相同命令！')

        else:
            bot.reply_to(message, not_admin)
    except Exception as e:
        rid = getReportID()
        traceback.print_exc()
        logging.error(str(rid + '::' + str(repr(e)) + '\n' + traceback.format_exc()))
        bot.send_message(message.from_user.id, '抱歉，我出现错误，识别ID为 ' + rid + '\n\n信息如下：\n' + str(
            repr(e)) + '\n\n请将这条信息 Forward 给 @abc1763613206 中所列的用户 进行处理！')

@bot.message_handler(commands=['whoami'])
def retID(message):
    userid = str(message.from_user.id)
    chatid = str(message.chat.id)
    username = str(message.from_user.username)
    try:
        ret = '您的用户ID为 {0} ， 用户名为 @{1} ，当前聊天ID为 {2} \n您当前所在用户组为：'.format(userid,username,chatid)
        if userid in config.AdminList:
            ret+= 'FullAdmin '
        elif username in jsadmins:
            ret+= 'Admin'
        else :
            ret+= 'User'
        bot.reply_to(message, ret)
    except Exception as e:
        rid = getReportID()
        traceback.print_exc()
        logging.error(str(rid + '::' + str(repr(e)) + '\n' + traceback.format_exc()))
        bot.send_message(message.from_user.id, '抱歉，我出现错误，识别ID为 ' + rid + '\n\n信息如下：\n' + str(
            repr(e)) + '\n\n请将这条信息 Forward 给 @abc1763613206 中所列的用户 进行处理！')


def CheckState(message):
    try:
        userid = str(message.from_user.id)
        chatid = str(message.chat.id)
        global quotes
        global texts
        if (userid in StateAdmin) and (StateAdmin[userid] != ''):
            if StateAdmin[userid] == '#SettingQuotes1#':
                StateAdminEnd[userid] = message.text
                if message.text == '-1':
                    bot.reply_to(message, '已退出！')
                    StateAdmin[userid] = ''
                    return
                markup = types.ForceReply(selective=False)
                bot.send_message(chatid, '请输入您要定义的回复(输入-1终止)：', reply_markup=markup)
                StateAdmin[userid] = '#SettingQuotes2#'
                return
            elif StateAdmin[userid] == '#SettingQuotes2#':
                if message.text == '-1':
                    bot.reply_to(message, '已退出！')
                    StateAdmin[userid] = ''
                    return
                logging.info(str('Setting(Quotes):add::@{} ({} {}): {} -> {}'.format(message.from_user.username, message.from_user.first_name,
                                                                message.from_user.last_name, StateAdminEnd[userid],message.text)))
                if StateAdminEnd[userid] in quotes:
                    quotes[StateAdminEnd[userid]].append(message.text)
                else:
                    quotes[StateAdminEnd[userid]] = [message.text]
                bot.reply_to(message,'定义：\n{} -> {}'.format(str(StateAdminEnd[userid]),str(message.text)))
                StateAdmin[userid] = ''

                SaveJson()
                bot.reply_to(message, '成功定义！')
                return
            else:
                if StateAdmin[userid] == '#SettingTexts#':
                    if message.text == '-1':
                        bot.reply_to(message, '已退出！')
                        StateAdmin[userid] = ''
                        return
                    texts.append(message.text)
                    logging.info(str('Setting(Texts):add::@{} ({} {}): {}'.format(message.from_user.username,
                                                                                     message.from_user.first_name,
                                                                                     message.from_user.last_name,
                                                                                     message.text)))

                    SaveJson()
                    bot.reply_to(message, '成功定义！')
                    return
                if StateAdmin[userid] == '#RemoveQuotes1#':
                    if message.text == '-1':
                        bot.reply_to(message, '已退出！')
                        StateAdmin[userid] = ''
                        return
                    if message.text in quotes:
                        StateAdminEnd[userid] = message.text
                        markup = types.ForceReply(selective=False)
                        bot.send_message(chatid, '请输入您要删除的回复(输入-1终止)：', reply_markup=markup)
                        StateAdmin[userid] = '#RemoveQuotes2#'
                        return
                    else :
                        bot.send_message(chatid,'未找到对应的语段！\n请检查是否输入了多余的空格或引号！')
                        StateAdmin[userid] = ''
                        return
                elif StateAdmin[userid] == '#RemoveQuotes2#':
                    if message.text == '-1':
                        bot.reply_to(message, '已退出！')
                        StateAdmin[userid] = ''
                        return
                    logging.info(str('Setting(Quotes):remove::@{} ({} {}): {} -> {}'.format(message.from_user.username,message.from_user.first_name,message.from_user.last_name,StateAdminEnd[userid],message.text)))
                    quotes[StateAdminEnd[userid]].remove(message.text)
                    bot.reply_to(message, '删除：\n{} -> {}'.format(str(StateAdminEnd[userid]), str(message.text)))
                    StateAdmin[userid] = ''
                    SaveJson()
                    bot.reply_to(message, '成功删除！')
                    return
                elif StateAdmin[userid] == '#RemoveTexts#':
                    if message.text == '-1':
                        bot.reply_to(message, '已退出！')
                        StateAdmin[userid] = ''
                        return
                    bot.reply_to(message, '删除：\n{}'.format(str(message.text)))
                    texts.remove(message)
                    logging.info(str('Setting(Texts):remove::@{} ({} {}): {}'.format(message.from_user.username,message.from_user.first_name,message.from_user.last_name,message.text)))
                    StateAdmin[userid] = ''
                    SaveJson()
                    bot.reply_to(message, '成功删除！')
                    return
                elif StateAdmin[userid] == '#Settings1#':
                    if message.text == '-1':
                        bot.reply_to(message, '已退出！')
                        StateAdmin[userid] = ''
                        return
                    if message.text == 'quotes':
                        bot.reply_to(message, '请使用 /setquotes(/rmquotes) 编辑此项！')
                        StateAdmin[userid] = ''
                        return
                    if message.text == 'quotes':
                        bot.reply_to(message, '请使用 /settexts(/rmtexts) 编辑此项！')
                        StateAdmin[userid] = ''
                        return
                    StateAdminEnd[userid] = message.text
                    markup = types.ForceReply(selective=False)
                    bot.send_message(chatid, '请输入该项您要编辑的内容(输入-1终止)：', reply_markup=markup)
                    StateAdmin[userid] = '#Settings2#'
                    return
                elif StateAdmin[userid] == '#Settings2#':
                    if message.text == '-1':
                        bot.reply_to(message, '已退出！')
                        StateAdmin[userid] = ''
                        return

                    markup = types.ForceReply(selective=False)
                    logging.info(str('Setting:set::@{} ({} {}): {} -> {}'.format(message.from_user.username,
                                                                                            message.from_user.first_name,
                                                                                            message.from_user.last_name,
                                                                                            StateAdminEnd[userid],
                                                                                            message.text)))
                    jsdata[StateAdminEnd[userid]] = message.text
                    bot.reply_to(message, '设置：\n{} -> {}'.format(str(StateAdminEnd[userid]), str(message.text)))
                    StateAdmin[userid] = ''
                    SaveSetJson()
                    bot.reply_to(message, '设置完成！')
                    return
    except Exception as e:
        rid = getReportID()
        traceback.print_exc()
        logging.error(str(rid + '::' + str(repr(e)) + '\n' + traceback.format_exc()))
        bot.send_message(message.from_user.id, '抱歉，我出现错误，识别ID为 ' + rid + '\n\n信息如下：\n' + str(
            repr(e)) + '\n\n请将这条信息 Forward 给 @abc1763613206 中所列的用户 进行处理！')




@bot.message_handler(func=lambda m: True,content_types=['audio', 'photo', 'voice', 'video', 'document', 'text', 'location', 'contact', 'sticker'])
def echo_all(message):
    try:
        userid = str(message.from_user.id)
        chatid = str(message.chat.id)
        if (userid in StateAdmin) and (StateAdmin[userid] != ''):  # 是管理，且处于设置模式
            CheckState(message)
            return
        if HandledAdmins != []: # 托管模式
            #print(message.forward_from)
            #print(message.reply_to_message)
            #if message.reply_to_message != None:
            #    print('-----------------------')
            #    print(message.reply_to_message)
            if chatid in HandledAdmins: #是管理回复
                if (message.reply_to_message != None):
                    if (str(message.reply_to_message.from_user.id) == str(chatid)):
                        logging.info(str(
                            'Chat(FORWARDED)::@{} ({} {}): {}'.format(message.from_user.username,
                                                                      message.from_user.first_name,
                                                                      message.from_user.last_name, message.text)))
                        for i in HandledAdmins:
                            bot.forward_message(i, chatid, message.message_id)
                        return
                    logging.info(str('Reply:admin::@{} ({} {}): ->(@{}) {}'.format(message.from_user.username,
                                                                                   message.from_user.first_name,
                                                                                   message.from_user.last_name,
                                                                                   message.reply_to_message.forward_from.username,
                                                                                   message.text)))

                    bot.forward_message(message.reply_to_message.forward_from.id, message.chat.id, message.message_id)
                    return
                logging.info(str(
                    'Chat(FORWARDED)::@{} ({} {}): {}'.format(message.from_user.username,
                                                              message.from_user.first_name,
                                                              message.from_user.last_name, message.text)))
                for i in HandledAdmins:
                    bot.forward_message(i, chatid, message.message_id)
                return


            else:
                logging.info(str(
                    'Chat(FORWARDED)::@{} ({} {}): {}'.format(message.from_user.username, message.from_user.first_name,
                                                   message.from_user.last_name, message.text)))
                for i in HandledAdmins:
                    bot.forward_message(i,message.chat.id,message.message_id)
            return

        if message.content_type != 'text':
            bot.reply_to(message,text_not_supported)
            return
        logging.info(str('Chat::@{} ({} {}): {}'.format(message.from_user.username, message.from_user.first_name, message.from_user.last_name, message.text)))
        bot.reply_to(message,Process(message.text))


    except Exception as e:
        rid = getReportID()
        traceback.print_exc()
        logging.error(str(rid + '::' + str(repr(e)) + '\n' + traceback.format_exc()))
        bot.send_message(message.from_user.id,'抱歉，我出现错误，识别ID为 '+rid+'\n\n信息如下：\n'+str(repr(e))+'\n\n请将这条信息 Forward 给 @abc1763613206 中所列的用户 进行处理！')



def main_loop():
    try:
        bot.polling(True)
        while 1:
            time.sleep(2)
    except Exception as e:
        rid = getReportID()
        traceback.print_exc()
        logging.error(str(rid + '::' + str(repr(e)) + '\n' + traceback.format_exc()))


if __name__ == '__main__':
    try:
        logging.info("准备处理信息")
        main_loop()
    except KeyboardInterrupt:
        print('\nExiting by user request.\n')
        exit(0)
    except Exception as e:
        rid = getReportID()
        traceback.print_exc()
        logging.error(str(rid + '::' + str(repr(e)) + '\n' + traceback.format_exc()))

