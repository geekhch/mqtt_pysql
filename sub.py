# coding=utf-8
'''
1. 使用前pip install pymysql、　pip install paho-mqtt
2. MQTT API: https://pypi.python.org/pypi/paho-mqtt
3. topic报文格式使用python一级字典（单层json）格式，报文中需要加入单片机唯一id编号，例如｛"id":"123","tempreture":"48","humility":"89"｝
4. 数据表名称为（b_001）,001代表单片机id前缀
mosquitto_pub -h tx.3cat.top -t "SCU/TEST" -m "{'fk_id':'0020001','fire':'0','battery':'100'}"
'''
import paho.mqtt.client as mqtt
from sqlSet import Mysql
import time


def Time():
    str = time.strftime("[%m-%d %H:%M]", time.localtime())
    return str

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe("SCU/#")

def analzeJson(dict_var):
    if(not 'fk_id' in dict_var.keys()):
        return -1
    dict_var['fk_id'] = "\'%s\'" % dict_var['fk_id']
    sql_cllient = Mysql()
    sql = "select tableName from boxes where id={0}".format(dict_var['fk_id'])
    sql = sql.replace('fk_id','type')
    results = sql_cllient.querry(sql)
    table = results[0]['tableName']
    columns=''
    values=''
    for key in dict_var:
        columns += key + ','
        values += dict_var[key] + ','
    sql = "INSERT INTO {0}({1}) VALUES({2})".format(table,columns[:-1],values[:-1])
    sql = sql.replace('fk_id','type')
    sql_cllient.update(sql)
    
def on_message(client, userdata, msg):
    '''收到消息就执行下面的操作'''
    jsonStr = msg.payload.decode()
    print("msg:",jsonStr,type(jsonStr))
    try:
        dictType = eval(jsonStr)
        print("dict:",dictType,type(dictType))
        if(not isinstance(dictType, dict)):
            raise Exception("不是json")
    except:
        return
    print(Time()+str(dictType)) #日志消息
    # try:
    analzeJson(dictType)
    # except:
        # print('解析json报文失败')

mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.connect("tx.3cat.top", 1883, 60)
mqtt_client.loop_forever()
