#coding:utf-8
import requests
import json
import numpy as np
import cv2
import base64
import matplotlib.pyplot as plt
from PIL import Image

def getByte(path):
    with open(path, 'rb') as f:
        img_byte = base64.b64encode(f.read()) #二进制读取后变base64编码
    img_str = img_byte.decode('ascii') #转成python的unicode
    return img_str 
    
img_str = getByte('zyc_0.jpg')

requestsss={'name':'张山', 'image':img_str}
req = json.dumps(requestsss) #字典数据结构变json(所有程序语言都认识的字符串)

res=requests.post('http://127.0.0.1:6060/', data=req)
print(res.text)
