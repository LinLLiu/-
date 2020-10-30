# -*- coding: utf-8 -*-
from PIL import Image
import pytesseract
import cv2
import numpy as np
import re
# from multiprocessing import Pool, Queue, Lock, Process, freeze_support
import time
from cnocr import CnOcr
ocr = CnOcr()
import csv
import pandas as pd

#pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files (x86)\\Tesseract-OCR\\tesseract.exe'
x = 1280.00 / 3840.00
pixel_x = int(x * 3840)
# print(x, pixel_x)

#mode0:识别姓名，出生日期，身份证号； mode1：识别所有信息
def idcardocr(imgname, mode=1):
        print(u'进入身份证光学识别流程...')
        print(u'----------------------------------------------')
        if mode==1:
            # generate_mask(x)
            img_data_gray, img_org = img_resize_gray(imgname)
            result_dict = dict()
            name_pic = find_name(img_data_gray, img_org)
            # showimg(name_pic)
            # print 'name'
            result_dict['pname'] = get_name(name_pic)
            # print result_dict['name']

            sex_pic = find_sex(img_data_gray, img_org)
            # showimg(sex_pic)
            # print 'sex'
            result_dict['psex'] = get_sex(sex_pic)
            # print result_dict['sex']

            nation_pic = find_nation(img_data_gray, img_org)
            # showimg(nation_pic)
            # print 'nation'
            result_dict['pnation'] = get_nation(nation_pic)
            # print result_dict['nation']

            address_pic = find_address(img_data_gray, img_org)
            # showimg(address_pic)
            # print 'address'
            result_dict['paddress'] = get_address(address_pic)
            # print result_dict['address']

            idnum_pic = find_idnum(img_data_gray, img_org)
            result_dict['pidcardnumber'], result_dict['pbirth'] = get_idnum_and_birth(idnum_pic)
            # print result_dict['idnum']
        elif mode==0:
            # generate_mask(x)
            img_data_gray, img_org = img_resize_gray(imgname)
            result_dict = dict()
            name_pic = find_name(img_data_gray, img_org)
            result_dict['pname'] = get_name(name_pic)


            idnum_pic = find_idnum(img_data_gray, img_org)

            result_dict['pidcardnumber'], result_dict['pbirth'] = get_idnum_and_birth(idnum_pic)
            result_dict['psex']=''
            result_dict['pnation']=''
            result_dict['paddress']=''

        else:
            print(u"模式选择错误！")

        # 将结果写入test.csv文件
        # result_data = [result_dict]
        # name=['pname', 'psex','pnation','paddress','pidcardnumber','pbirth']
        # with open('test.csv', 'a',encoding='utf-8') as f: 
        #         writer = csv.DictWriter(f,fieldnames=name) # 提前预览列名，当下面代码写入数据时，会将其一一对应。
        #         writer.writerows(result_data) # 写入数据
        keys = []
        values = []
        for key,value in result_dict.items():
                keys.append(key)
                values.append(value)
        print(keys,values)
        if values[0]=='':
                result = {"result":result_dict,'code':"1001",'msg':"姓名无法识别!",} 
                if values[1]=='':
                        result = {"result":result_dict,'code':"1001",'msg':"姓名无法识别!性别无法识别!",}
                if values[2]=='':
                        result = {"result":result_dict,'code':"1001",'msg':"姓名无法识别!民族无法识别!",}
                if values[3]=='':
                        result = {"result":result_dict,'code':"1001",'msg':"姓名无法识别!户籍地址无法识别!",}
                if (values[4]=='' or len(values[4])!=18):
                        result = {"result":result_dict,'code':"1001",'msg':"姓名无法识别!身份证号码无法识别或者不正确!",}
                if values[1]=='' and values[2]=='':
                        result = {"result":result_dict,'code':"1001",'msg':"姓名无法识别!性别无法识别!民族无法识别!",}
                if values[1]=='' and values[3]=='':
                        result = {"result":result_dict,'code':"1001",'msg':"姓名无法识别!性别无法识别!户籍地址无法识别!",}
                if values[1] and (values[4]=='' or len(values[4])!=18):
                        result = {"result":result_dict,'code':"1001",'msg':"姓名无法识别!性别无法识别!身份证号码无法识别或者不正确!",}
                if values[2]=='' and values[3]=='':
                        result = {"result":result_dict,'code':"1001",'msg':"姓名无法识别!民族无法识别!户籍地址无法识别!",}
                if values[2]=='' and (values[4]=='' or len(values[4])!=18):
                        result = {"result":result_dict,'code':"1001",'msg':"姓名无法识别!民族无法识别!身份证号码无法识别或者不正确!",}
                if values[3]=='' and (values[4]=='' or len(values[4])!=18):
                        result = {"result":result_dict,'code':"1001",'msg':"姓名无法识别!户籍地址无法识别!身份证号码无法识别或者不正确!",}
                if values[1]=='' and values[2]=='' and values[3]=='':
                        result = {"result":result_dict,'code':"1001",'msg':"姓名无法识别!性别无法识别!民族无法识别!户籍地址无法识别!",}
                if values[1]=='' and values[2]=='' and (values[4]=='' or len(values[4])!=18):
                        result = {"result":result_dict,'code':"1001",'msg':"姓名无法识别!性别无法识别!民族无法识别!身份证号码无法识别或者不正确!",} 
                if values[2]=='' and values[3] and (values[4]=='' or len(values[4])!=18):
                        result = {"result":result_dict,'code':"1001",'msg':"姓名无法识别!民族无法识别!户籍地址无法识别!身份证号码无法识别或者不正确!",}       
                if values[1]=='' and values[2]=='' and values[3]=='' and (values[4]=='' or len(values[4])!=18) :
                        result = {"result":result_dict,'code':"1001",'msg':"姓名无法识别!性别无法识别!民族无法识别!户籍地址无法识别!身份证号码无法识别或者不正确!",}
                
        elif values[1]=='':
                result = {"result":result_dict,'code':"1001",'msg':"性别无法识别!",}
                if values[2]=='' :
                        result = {"result":result_dict,'code':"1001",'msg':"性别无法识别!民族无法识别!",}
                if values[3]:
                        result = {"result":result_dict,'code':"1001",'msg':"性别无法识别!户籍地址无法识别!",}
                if values[4]=='' or len(values[4])!=18:
                        result = {"result":result_dict,'code':"1001",'msg':"性别无法识别!身份证号码无法识别或者不正确!",}
                if values[2]=='' and values[3]=='':
                        result = {"result":result_dict,'code':"1001",'msg':"性别无法识别!民族无法识别!户籍地址无法识别!",}
                if values[2]=='' and (values[4]=='' or len(values[4])!=18):
                        result = {"result":result_dict,'code':"1001",'msg':"性别无法识别!民族无法识别!身份证号码无法识别或者不正确!",} 
                if values[3]=='' and (values[4]=='' or len(values[4])!=18) :
                        result = {"result":result_dict,'code':"1001",'msg':"性别无法识别!户籍地址无法识别!身份证号码无法识别或者不正确!",}
                if values[2]=='' and values[3]=='' and (values[4]=='' or len(values[4])!=18) :
                        result = {"result":result_dict,'code':"1001",'msg':"性别无法识别!民族无法识别!户籍地址无法识别!身份证号码无法识别或者不正确!",}

        elif values[2]=='':
                result = {"result":result_dict,'code':"1001",'msg':"民族无法识别!",}
                if values[3]=='':
                        result = {"result":result_dict,'code':"1001",'msg':"民族无法识别!户籍地址无法识别!",}
                if values[4]=='' or len(values[4])!=18 :
                        result = {"result":result_dict,'code':"1001",'msg':"民族无法识别!身份证号码无法识别或者不正确!",}
                if values[3]=='' and (values[4]=='' or len(values[4])!=18) :
                        result = {"result":result_dict,'code':"1001",'msg':"民族无法识别!户籍地址无法识别!身份证号码无法识别或者不正确!",}

        elif values[3]=='':
                result = {"result":result_dict,'code':"1001",'msg':"户籍地址无法识别!",}
                if values[4]=='' or len(values[4])!=18 :
                        result = {"result":result_dict,'code':"1001",'msg':"户籍地址无法识别!身份证号码无法识别或者不正确!",}

        elif values[4]=='' or len(values[4])!=18:
                result = {"result":result_dict,'code':"1001",'msg':"身份证号码无法识别或者不正确!",}

        else: 
                result = {"result":result_dict,'code':"200",'msg':"success",} 
        return result

def generate_mask(x):
        name_mask_pic = cv2.UMat(cv2.imread('name_mask.jpg'))
        sex_mask_pic = cv2.UMat(cv2.imread('sex_mask.jpg'))
        nation_mask_pic = cv2.UMat(cv2.imread('nation_mask.jpg'))
        birth_mask_pic = cv2.UMat(cv2.imread('birth_mask.jpg'))
        year_mask_pic = cv2.UMat(cv2.imread('year_mask.jpg'))
        month_mask_pic = cv2.UMat(cv2.imread('month_mask.jpg'))
        day_mask_pic = cv2.UMat(cv2.imread('day_mask.jpg'))
        address_mask_pic = cv2.UMat(cv2.imread('address_mask.jpg'))
        idnum_mask_pic = cv2.UMat(cv2.imread('idnum_mask.jpg'))
        name_mask_pic = img_resize_x(name_mask_pic)
        sex_mask_pic = img_resize_x(sex_mask_pic)
        nation_mask_pic = img_resize_x(nation_mask_pic)
        birth_mask_pic = img_resize_x(birth_mask_pic)
        year_mask_pic = img_resize_x(year_mask_pic)
        month_mask_pic = img_resize_x(month_mask_pic)
        day_mask_pic = img_resize_x(day_mask_pic)
        address_mask_pic = img_resize_x(address_mask_pic)
        idnum_mask_pic = img_resize_x(idnum_mask_pic)
        cv2.imwrite('name_mask_%s.jpg'%pixel_x, name_mask_pic)
        cv2.imwrite('sex_mask_%s.jpg' %pixel_x, sex_mask_pic)
        cv2.imwrite('nation_mask_%s.jpg' %pixel_x, nation_mask_pic)
        cv2.imwrite('birth_mask_%s.jpg' %pixel_x, birth_mask_pic)
        cv2.imwrite('year_mask_%s.jpg' % pixel_x, year_mask_pic)
        cv2.imwrite('month_mask_%s.jpg' % pixel_x, month_mask_pic)
        cv2.imwrite('day_mask_%s.jpg' % pixel_x, day_mask_pic)
        cv2.imwrite('address_mask_%s.jpg' %pixel_x, address_mask_pic)
        cv2.imwrite('idnum_mask_%s.jpg' %pixel_x, idnum_mask_pic)

#用于生成模板
def img_resize_x(imggray):
        # print 'dheight:%s' % dheight
        crop = imggray
        size = crop.get().shape
        dheight = int(size[0]*x)
        dwidth = int(size[1]*x)
        crop = cv2.resize(src=crop, dsize=(dwidth, dheight), interpolation=cv2.INTER_CUBIC)
        return crop

#idcardocr里面resize以高度为依据, 用于get部分
def img_resize(imggray, dheight):
        # print 'dheight:%s' % dheight
        crop = imggray
        size = crop.get().shape
        height = size[0]
        width = size[1]
        width = width * dheight / height
        crop = cv2.resize(src=crop, dsize=(int(width), dheight), interpolation=cv2.INTER_CUBIC)
        return crop

def img_resize_gray(imgorg):
        
        #imgorg = cv2.imread(imgname)
        crop = imgorg
        size = cv2.UMat.get(crop).shape
        # print size
        height = size[0]
        width = size[1]
        # 参数是根据3840调的
        height = int(height * 3840 * x / width)
        # print height
        crop = cv2.resize(src=crop, dsize=(int(3840 * x), height), interpolation=cv2.INTER_CUBIC)
        return hist_equal(cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)), crop

def find_name(crop_gray, crop_org):
        template = cv2.UMat(cv2.imread('name_mask_%s.jpg'%pixel_x, 0))
        # showimg(crop_org)
        w, h = cv2.UMat.get(template).shape[::-1]
        res = cv2.matchTemplate(crop_gray, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        # print(max_loc)
        top_left = (max_loc[0] + w, max_loc[1] - int(20*x))
        bottom_right = (top_left[0] + int(700*x), top_left[1] + int(300*x))
        result = cv2.UMat.get(crop_org)[top_left[1]-10:bottom_right[1], top_left[0]-10:bottom_right[0]]
        cv2.rectangle(crop_gray, top_left, bottom_right, 255, 2)
        # showimg(result)
        return cv2.UMat(result)

def find_sex(crop_gray, crop_org):
        template = cv2.UMat(cv2.imread('sex_mask_%s.jpg'%pixel_x, 0))
        # showimg(template)
        w, h = cv2.UMat.get(template).shape[::-1]
        res = cv2.matchTemplate(crop_gray, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        top_left = (max_loc[0] + w, max_loc[1] - int(20*x))
        bottom_right = (top_left[0] + int(300*x), top_left[1] + int(300*x))
        result = cv2.UMat.get(crop_org)[top_left[1]-10:bottom_right[1], top_left[0]-10:bottom_right[0]]
        cv2.rectangle(crop_gray, top_left, bottom_right, 255, 2)
        #showimg(crop_gray)
        return cv2.UMat(result)

def find_nation(crop_gray, crop_org):
        template = cv2.UMat(cv2.imread('nation_mask_%s.jpg'%pixel_x, 0))
        #showimg(template)
        w, h = cv2.UMat.get(template).shape[::-1]
        res = cv2.matchTemplate(crop_gray, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        top_left = (max_loc[0] + w - int(20*x), max_loc[1] - int(20*x))
        bottom_right = (top_left[0] + int(500*x), top_left[1] + int(300*x))
        result = cv2.UMat.get(crop_org)[top_left[1]-10:bottom_right[1], top_left[0]-10:bottom_right[0]]
        cv2.rectangle(crop_gray, top_left, bottom_right, 255, 2)
        #showimg(crop_gray)
        return cv2.UMat(result)


def find_address(crop_gray, crop_org):
        template = cv2.UMat(cv2.imread('address_mask_%s.jpg'%pixel_x, 0))
        # showimg(template)
        #showimg(crop_gray)
        w, h = cv2.UMat.get(template).shape[::-1]
        #t1 = round(time.time()*1000)
        res = cv2.matchTemplate(crop_gray, template, cv2.TM_CCOEFF_NORMED)
        #t2 = round(time.time()*1000)
        #print 'time:%s'%(t2-t1)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        top_left = (max_loc[0] + w, max_loc[1] - int(20*x))
        bottom_right = (top_left[0] + int(1700*x), top_left[1] + int(550*x))
        result = cv2.UMat.get(crop_org)[top_left[1]-10:bottom_right[1], top_left[0]-10:bottom_right[0]]
        cv2.rectangle(crop_gray, top_left, bottom_right, 255, 2)
        #showimg(crop_gray)
        return cv2.UMat(result)

def find_idnum(crop_gray, crop_org):
        template = cv2.UMat(cv2.imread('idnum_mask_%s.jpg'%pixel_x, 0))
        # showimg(template)
        #showimg(crop_gray)
        w, h = cv2.UMat.get(template).shape[::-1]
        res = cv2.matchTemplate(crop_gray, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        top_left = (max_loc[0] + w, max_loc[1] - int(20*x))
        bottom_right = (top_left[0] + int(2300*x), top_left[1] + int(300*x))
        result = cv2.UMat.get(crop_org)[top_left[1]-10:bottom_right[1], top_left[0]-10:bottom_right[0]]
        cv2.rectangle(crop_gray, top_left, bottom_right, 255, 2)
        #showimg(crop_gray)
        return cv2.UMat(result)


def showimg(img):
        cv2.namedWindow("contours", 0);
        cv2.resizeWindow("contours", 1280, 720);
        cv2.imshow("contours", img)
        cv2.waitKey()


def get_name(img):
        #    cv2.imshow("method3", img)
        #    cv2.waitKey()
        # print('姓名')
        _, _, red = cv2.split(img) #split 会自动将UMat转换回Mat
        cv2.imwrite('name.png', red)
        img = Image.open('name.png')
        img_gray = img.convert('L')
        im_arr = np.array(img_gray)
        im2 = ((100.0/255)*im_arr +100).astype(np.int)
        im2 = Image.fromarray(np.uint8(im2))      
        im2.convert('RGB').save('name_lim.jpg')
        add_val = ocr.ocr(r"name_lim.jpg")
        # img = cv2.imread(r"name.png", cv2.IMREAD_COLOR)  
        # # 调整亮度
        # rows, cols, channels = img.shape
        # # 新建全零(黑色)图片数组:np.zeros(img1.shape, dtype=uint8)
        # blank = np.zeros([rows, cols, channels], img.dtype)
        # dst = cv2.addWeighted(img, 1.3, blank, -0.3, 3)
        # add_val = ocr.ocr(dst)
        res_name = ''
        for i in add_val:
                for j in i:
                        res_name+=j
        return res_name


def get_sex(img):
        _, _, red = cv2.split(img)
        # print('性别')
        cv2.imwrite('sex.png', img)
        res_sex = ocr.ocr_for_single_line('sex.png')
        res_sex_ = ''
        for i in res_sex:
                res_sex_+=i
        red = cv2.UMat(red)
        red = hist_equal(red)
        red = cv2.adaptiveThreshold(red, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 151, 50)
        #    red = cv2.medianBlur(red, 3)
        red = img_resize(red, 150)

        if res_sex_ in ["文", "安", "仗", "如", "汝", "奴", "义", "丈", "好", "乂", "㚢", "囡",'女']:
                res_sex_ = "女"
        else:
                res_sex_ = "男"
        return res_sex_

def get_nation(img):
        # _, _, red = cv2.split(img)
        # print('nation')
        # red = cv2.UMat(red)
        # red = hist_equal(red)
        # red = cv2.adaptiveThreshold(red, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 151, 50)
        # red = img_resize(red, 150)
        # # cv2.imwrite('nation.png', red)
        # # img = Image.fromarray(cv2.UMat.get(red).astype('uint8'))
        # #return get_result_fix_length(red, 1, 'nation', '-psm 10')
        # return get_result_fix_length(red, 1, 'chi_sim', '--psm 10')
      
        _, _, red = cv2.split(img)
        # print('民族')
        cv2.imwrite('nation.png', red)
        # img = cv2.imread(r"nation.png", cv2.IMREAD_COLOR)  
        img = Image.open('nation.png')
        img_gray = img.convert('L')
        im_arr = np.array(img_gray)
        im2 = ((100.0/255)*im_arr +100).astype(np.int)
        im2 = Image.fromarray(np.uint8(im2))      
        im2.convert('RGB').save('nation_lim.jpg')
        add_val = ocr.ocr(r"nation_lim.jpg")
        # # 调整亮度
        # rows, cols, channels = img.shape
        # # 新建全零(黑色)图片数组:np.zeros(img1.shape, dtype=uint8)
        # blank = np.zeros([rows, cols, channels], img.dtype)
        # dst = cv2.addWeighted(img, 1.3, blank, -0.3, 3)
        # add_val = ocr.ocr(dst)
        res_nation = ''
        for i in add_val:
                for j in i:
                        res_nation+=j
        if res_nation in ["汶", "汊", "汝", "汐", "汲", "汀", "波", "叹", "仅", "汊","义",'','汉','汉箴^','X','x','又']:
                res_nation = '汉'
        elif res_nation in ["固", "同", "倜", "调", "垌", "桐", "恫", "洞", "峒", "硐", "胴",'侗']:
                res_nation = "侗"
        elif res_nation in ["瞒", "蹒", "螨", "潢", "滿",'满']:
                res_nation = '满'
        elif res_nation in ["惊", "凉", "谅", "掠", "谅", "晾", "掠", "景", "亰","京"]:
                res_nation = "京"
        elif res_nation in ["泰", "秦", "倴", "僚", "溙", "奉","傣"]:     
                res_nation = "傣"
        elif res_nation in ["亩", "启", "茔", "芸", "盅", "电", "宙", "田", "喵", "描", "猫","苗"]:
                res_nation = "苗"
        elif res_nation in ["臧", "臧", "葬"]:
                res_nation = "藏"
        elif res_nation in ["壯", "莊", "荘", "妆","壮"]:  
                res_nation = "壮"   
        elif res_nation in ["摇", "遥", "谣","瑶"]:
                res_nation = "瑶"
        elif res_nation in ["日", "自", "百", "囱", "曰", "囪", "甶", "凹", "汩", "彐","旧", "囗", "田", "帕", "伯", "拍", "泊", "柏", "陌","白"]:
                res_nation = "白"
        elif res_nation in ["藜", "棃", "黧", "梨", "犁", "藜","黎"]:
                res_nation = "黎"
        elif res_nation in ["仉", "巩", "讥", "伉", "瓦", "咓", "砙","佤"]:
                res_nation = "佤"
        elif res_nation in ["番", "禽", "肏","畲"]:
                res_nation = "畲"
        elif res_nation in ["氷", "囦", "永", "冰", "木", "未","水"]:
                res_nation = "水"
        elif res_nation in ["工", "二", "三", "王", "亍", "士", "七","土"]:
                res_nation = "土"
        elif res_nation in ["恙", "羊", "羔", "羔","羌"]:
                res_nation ="羌" 
        elif res_nation in ["囚", "四", "迴", "佪", "廻", "洄", "叵", "固", "间", "囧", "区","回"]:
                res_nation = "回"
        elif res_nation in ["努", "恕", "奴", "弩", "驽", "孥", "㐐","怒"]:
                res_nation = "怒"
        else:
                res_nation = res_nation
        return res_nation
        # # return pytesseract.image_to_string(img, lang='nation', config='-psm 13').replace(" ","")



def get_address(img):
        _, _, red = cv2.split(img)
        # cv2.imwrite('addre.png',img)
        cv2.imwrite('address.png', red)
        img = Image.open('address.png')
        img_gray = img.convert('L')
        im_arr = np.array(img_gray)
        im2 = ((100.0/255)*im_arr +100).astype(np.int)
        im2 = Image.fromarray(np.uint8(im2))      
        im2.convert('RGB').save('address_lim.jpg')
        add_val = ocr.ocr(r"address_lim.jpg")
        # 调整图片亮度
        # img = cv2.imread(r"address.png", cv2.IMREAD_COLOR)  
        # rows, cols, channels = img.shape
        # # 新建全零(黑色)图片数组:np.zeros(img1.shape, dtype=uint8)
        # blank = np.zeros([rows, cols, channels], img.dtype)
        # dst = cv2.addWeighted(img, 1.3, blank, -0.3, 3)
        # add_val = ocr.ocr(dst)
        # add_val = ocr.ocr('addre.png')
        res_address = ''
        for i in add_val:
                for j in i:
                        res_address+=j
                        # res_address.append(j)
        
        # res_address = ocr.ocr(dst)
        # res_address = ocr.ocr('address.png')
        # red = cv2.UMat(red)
        # red = hist_equal(red)
        # red = cv2.adaptiveThreshold(red, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 151, 50)
        # red = img_resize(red, 300)
        #img = img_resize(img, 300)
        # cv2.imwrite('img.png', red)
        # res_address = ocr.ocr('img.png')
        # img = Image.fromarray(cv2.UMat.get(red).astype('uint8'))
        return res_address


def get_idnum_and_birth(img):
        _, _, red = cv2.split(img)
        # print('公民身份号码')
        red = cv2.UMat(red)
        red = hist_equal(red)
        red = cv2.adaptiveThreshold(red, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 151, 50)
        red = img_resize(red, 150)
        cv2.imwrite('idnum_red.png', red)
        img = Image.fromarray(cv2.UMat.get(red).astype('uint8'))
        idnum_str = get_result_vary_length(red, 'eng', img, '--psm 8 ')
        return idnum_str, idnum_str[6:12]

def get_result_fix_length(red, fix_length, langset, custom_config=''):
    red_org = red
    cv2.fastNlMeansDenoising(red, red, 4, 7, 35)
    rec, red = cv2.threshold(red, 127, 255, cv2.THRESH_BINARY_INV)
    image, contours, hierarchy = cv2.findContours(red, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    # print(len(contours))
    # 描边一次可以减少噪点
    cv2.drawContours(red, contours, -1, (0, 255, 0), 1)
    color_img = cv2.cvtColor(red, cv2.COLOR_GRAY2BGR)

    h_threshold = 54
    numset_contours = []
    calcu_cnt = 1
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        if h > h_threshold:
            numset_contours.append((x, y, w, h))
    while len(numset_contours) != fix_length:
        if calcu_cnt > 50:
            print(u'计算次数过多！目前阈值为：', h_threshold)
            break
        numset_contours = []
        calcu_cnt += 1
        if len(numset_contours) > fix_length:
            h_threshold += 1
            contours_cnt = 0
            for cnt in contours:
                x, y, w, h = cv2.boundingRect(cnt)
                if h > h_threshold:
                    contours_cnt += 1
                    numset_contours.append((x, y, w, h))
        if len(numset_contours) < fix_length:
            h_threshold -= 1
            contours_cnt = 0
            for cnt in contours:
                x, y, w, h = cv2.boundingRect(cnt)
                if h > h_threshold:
                    contours_cnt += 1
                    numset_contours.append((x, y, w, h))
    result_string = ''
    numset_contours.sort(key=lambda num: num[0])
    for x, y, w, h in numset_contours:
        result_string += pytesseract.image_to_string(cv2.UMat.get(red_org)[y-10:y + h + 10, x-10:x + w + 10], lang=langset, config=custom_config)
    # print(new_r)
    # cv2.imwrite('fixlengthred.png', cv2.UMat.get(red_org)[y-10:y + h +10 , x-10:x + w + 10])
#     print(result_string)
    return result_string

def get_result_vary_length(red, langset, org_img, custom_config=''):
    red_org = red
    # cv2.fastNlMeansDenoising(red, red, 4, 7, 35)
    rec, red = cv2.threshold(red, 127, 255, cv2.THRESH_BINARY_INV)
    image, contours, hierarchy = cv2.findContours(red, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    # print(len(contours))
    # 描边一次可以减少噪点
    cv2.drawContours(red, contours, -1, (255, 255, 255), 1)
    color_img = cv2.cvtColor(red, cv2.COLOR_GRAY2BGR)
    numset_contours = []
    height_list=[]
    width_list=[]
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        height_list.append(h)
        # print(h,w)
        width_list.append(w)
    height_list.remove(max(height_list))
    width_list.remove(max(width_list))
    height_threshold = 0.70*max(height_list)
    width_threshold = 1.4 * max(width_list)
    # print('height_threshold:'+str(height_threshold)+'width_threshold:'+str(width_threshold))
    big_rect=[]
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        if h > height_threshold and w < width_threshold:
            # print(h,w)
            numset_contours.append((x, y, w, h))
            big_rect.append((x, y))
            big_rect.append((x + w, y + h))
    big_rect_nparray = np.array(big_rect, ndmin=3)
    x, y, w, h = cv2.boundingRect(big_rect_nparray)
    # imgrect = cv2.rectangle(color_img, (x, y), (x + w, y + h), (0, 255, 0), 2)
    # showimg(imgrect)
    # showimg(cv2.UMat.get(org_img)[y:y + h, x:x + w])

    result_string = ''
    result_string += pytesseract.image_to_string(cv2.UMat.get(red_org)[y-10:y + h + 10, x-10:x + w + 10], lang=langset,
                                                 config=custom_config)
#     print(result_string)

    return punc_filter(result_string)


def punc_filter(str):
        temp = str
        xx      =   u"([\u4e00-\u9fff0-9A-Z]+)"
        pattern =   re.compile(xx)
        results =   pattern.findall(temp)
        string = ""
        for result in results:
            string += result
        return string

#这里使用直方图拉伸，不是直方图均衡
def hist_equal(img):

        image = img.get() #UMat to Mat
        # result = cv2.equalizeHist(image)
        lut = np.zeros(256, dtype = image.dtype )#创建空的查找表
        #lut = np.zeros(256)
        hist= cv2.calcHist([image], #计算图像的直方图
                            [0], #使用的通道
                            None, #没有使用mask
                           [256], #it is a 1D histogram
                           [0,256])
        minBinNo, maxBinNo = 0, 255
        #计算从左起第一个不为0的直方图柱的位置
        for binNo, binValue in enumerate(hist):
            if binValue != 0:
                minBinNo = binNo
                break
        #计算从右起第一个不为0的直方图柱的位置
        for binNo, binValue in enumerate(reversed(hist)):
            if binValue != 0:
                maxBinNo = 255-binNo
                break
        #print minBinNo, maxBinNo
        #生成查找表
        for i,v in enumerate(lut):
            if i < minBinNo:
                lut[i] = 0
            elif i > maxBinNo:
                lut[i] = 255
            else:
                lut[i] = int(255.0*(i-minBinNo)/(maxBinNo-minBinNo)+0.5)
        result = cv2.LUT(image, lut)

        return cv2.UMat(result)

if __name__=="__main__":
    idocr = idcardocr(cv2.UMat(cv2.imread('testimages/zrh.jpg')))
    print(idocr)


