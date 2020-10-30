# -*- coding: utf-8 -*-
import idcardocr
import findidcard
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from multiprocessing import Lock
lock = Lock()
import socketserver
import cv2, time
import uuid
import cgi
import os

def process(img_name):
    try: 
        lock.acquire()
        idfind = findidcard.findidcard()
        idcard_img = idfind.find(img_name)
        result_dict = idcardocr.idcardocr(idcard_img)   
        lock.release()
    except Exception as e:
        result = []
        result_dict = {"result":{'result':result},'code':"500",'msg':"error",}
        # print(e)
    return result_dict

#SocketServer.ForkingMixIn, SocketServer.ThreadingMixIn
class ForkingServer(socketserver.ThreadingMixIn, HTTPServer):
    pass

class S(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        #self.end_headers()

    def do_GET(self):
        self._set_headers()
        # self.wfile.write("<html><body><h1>hi!</h1></body></html>")

    def do_HEAD(self):
        self._set_headers()

    def do_POST(self):
        #content_length = int(self.headers['Content-Length']) # <--- Gets the size of data
        # post_data = self.rfile.read(content_length) # <--- Gets the data itself
        ctype, pdict = cgi.parse_header(self.headers['content-type'])
        # print(pdict)
        pdict['boundary'] = bytes(pdict['boundary'], "utf-8")
        multipart_data = cgi.parse_multipart(self.rfile, pdict)
        filename = uuid.uuid1()
        fo = open("tmp/%s.jpg"%filename, "wb")
        fo.write( multipart_data.get('pic')[0] )
        fo.close()
        result = process("tmp/%s.jpg"%filename)
        os.remove("tmp/%s.jpg"%filename)
        #print result
        self._set_headers()
        self.send_header("Content-Length", str(len(json.dumps(result).encode('utf-8'))))
        self.end_headers()
        self.wfile.write(json.dumps(result).encode('utf-8'))

def http_server(server_class=ForkingServer, handler_class=S, port=8080):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    cv2.ocl.setUseOpenCL(True)
    print('Starting httpd...')
    print(u"是否启用OpenCL：%s"%cv2.ocl.useOpenCL())
    httpd.serve_forever()

if __name__=="__main__":
    # process(input("请输入要识别的文件名:").strip())
    http_server()


