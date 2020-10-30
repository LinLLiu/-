#coding:utf-8
from flask import request, Flask
import time
import os
from PIL import Image
from io import StringIO
import matplotlib.pyplot as plt
import cv2
import numpy as np
from io import BytesIO
import json
import base64

app = Flask(__name__)

@app.route("/", methods=['POST'])
def get_frame():
    start_time = time.time()
    upload_file = request.get_data()
    req = json.loads(upload_file)
    #old_file_name = upload_file.filename
    
    if upload_file:
        name = req['name']
        print(name)
        img_str = req['image'] #得到unicode的字符串
        img_decode_ = img_str.encode('ascii') #从unicode变成ascii编码
        img_decode = base64.b64decode(img_decode_) #解base64编码，得图片的二进制
        img_np_ = np.frombuffer(img_decode, np.uint8)
        img = cv2.imdecode(img_np_, cv2.COLOR_RGB2BGR) #转为opencv格式
        cv2.imshow('frame', img)
        
        cv2.waitKey()
        return 'success'
    else:
        return 'failed'


if __name__ == "__main__":
    app.run("127.0.0.1", port=6060)
