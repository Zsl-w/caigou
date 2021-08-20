# -*- coding: UTF-8 -*-
# 作者：ZHiLuan1

import datetime
import json
import os
import threading
import time
import tkinter as tk
import tkinter.ttk as ttk  # 分页栏
import webbrowser
from tkinter import messagebox
from tkinter.constants import E, W  # 空间布局方位

import pymysql
import requests


class TestBenchMaker:
    def __init__(self):
        self.TITLE = "CaiGou"
        self.WIDTH = 1500
        self.HEIGHT = 950
        self.parseDic = {}


# Initial GUI
    def initialGUI(self):
        window = tk.Tk()
        window.title(self.TITLE)
                
        # 界面显示在屏幕中心
        self.ws = window.winfo_screenwidth()
        self.hs = window.winfo_screenheight()
        x = (self.ws / 2) - (self.WIDTH / 2)
        y = (self.hs / 2) - (self.HEIGHT / 2)
        window.geometry('%dx%d+%d+%d' % (self.WIDTH, self.HEIGHT, x, y))
        window.resizable(0, 0)
        # post请求参数设置    
        
        
        base_url = "http://www.ccgp-xinjiang.gov.cn"
        url = "http://www.ccgp-xinjiang.gov.cn/front/search/category"
        ZcyAnnouncement = ['ZcyAnnouncement2', 'ZcyAnnouncement4']
        
        
        def post_url(payloadData):
            timeout = (5, 10)
            # 设置代理
            # proxy_1 = '222.74.202.229:8080'
            # proxy_2 = '101.132.186.175:9090'
            # proxies = {
            #         'http': 'http://' + proxy_2,
            #         'https': 'https//' + proxy_2
            #     }
            # {
            #     'http': 'http://' + proxy_2,
            #     'https': 'https//' + proxy_2
            #     }
            def get_proxy():
                return requests.get("http://127.0.0.1:5010/get/").json()
            
            def delete_proxy(proxy):
                requests.get("http://127.0.0.1:5010/delete/?proxy={}".format(proxy))
            # 请求头设置
            headers = {
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36 Edg/92.0.902.62",
                        "Host": "www.ccgp-xinjiang.gov.cn",
                        "Content-Type": "application/json;charset=UTF-8"}
            # Json数据格式转换
            dumpJsonData = json.dumps(payloadData)
            # 打印解析信息
            # print(f"dumpJsonData = {dumpJsonData}")
            proxy = get_proxy().get("proxy")
            retry_count = 5
            while retry_count >0 :
                try:
                    res = requests.post(url, data=dumpJsonData, headers=headers, timeout=timeout,  allow_redirects=True,  proxies={"http": "http://{}".format(proxy)})
                    return res
                except Exception:
                    retry_count -= 1
            delete_proxy(proxy)
            return None
        
        
        # 清洗数据，获得字典类型数据
        def clear_data(res):
            html = res.content.decode('utf8')
            html_dic = json.loads(html)
            dic_data = html_dic["hits"]
            final_datas = dic_data["hits"]
            return final_datas


        
        # 时间选择
        def value(combox1, combox2,combox3,combox4,combox5,combox6):
            return combox1.get(), combox2.get(), combox3.get(), combox4.get(), combox5.get(), combox6.get()

        
        def content_select(ZcyAnnouncement,text):
            for i in range(1, 5):
                names["payloadData%s" % i] = {
                        'categoryCode': ZcyAnnouncement,
                        'pageNo': f'{i}',
                        'pageSize': 15}
                names["res%s" % i] = post_url(names["payloadData%s" % i])
                final_datas = clear_data(names["res%s" % i])
                for final_data in final_datas:
                    data = final_data['_source']
                    timeStamp = float(data['publishDate']/1000)
                    # timeStamp_2 = int(data['bidOpeningTime']/1000)
                    timeArrays = time.localtime(timeStamp)
                    # timeArrays_2 = time.localtime(timeStamp_2)
                    publishDate = time.strftime("%Y--%m--%d %H:%M:%S", timeArrays)
                    # publishDate_Ymd = time.strftime("%Y--%m--%d")
                    # bidOpeningTime = time.strftime("%Y--%m--%d %H:%M:%S", timeArrays_2)
                    districtName = data['districtName'].replace("新疆维吾尔自治区本级", '', 1)
                    title = (data['title'])
                    f_url = (base_url + data['url'])
                    
                    text.tag_config('link>' + f_url)
                    text.insert('insert', "【" + publishDate + "】" + title + '\n' + '\n', 'link>' + f_url)
                    text.tag_bind('link>' + f_url, "<Double-Button-1>",
                                lambda event, f_url=f_url: open_url(event, f_url))
                # 鼠标左键双击点击打开网页时间绑定
                    def open_url(event, f_url):
                        webbrowser.open(f_url, new=0)
        
        
        def func(text, ZcyAnnouncement):
            text.delete('0.0', 'end')
            val = entry.get()
            value_tuple_func = ()
            value_tuple_func = value(combox1, combox2,combox3,combox4,combox5,combox6)
            s1 = value_tuple_func[0]+'-'+value_tuple_func[1]+'-'+value_tuple_func[2]+' 00:00:00'
            s2 = value_tuple_func[3]+'-'+value_tuple_func[4]+'-'+value_tuple_func[5]+' 00:00:00'

            start_time = time.mktime(time.strptime(s1, '%Y-%m-%d %H:%M:%S'))
            end_time = time.mktime(time.strptime(s2, '%Y-%m-%d %H:%M:%S'))

            if(start_time>end_time):
                messagebox.showwarning(title="警告", message="日期选择错误！")
            # 关键字提交信息
            for i in range(1, 6):   # 最多显示75条关键字查询公告
                payloadDatakw = {
                    'categoryCode': ZcyAnnouncement,
                    'keyword': f'{val}',
                    'pageNo': f'{i}',
                    'pageSize': 15
                }
                names["res%s" % i] = post_url(payloadDatakw)
                final_datas = clear_data(names["res%s" % i])
                for final_data in final_datas:
                    data = final_data['_source']
                    timeStamp = float(data['publishDate']/1000)
                    # timeStamp_2 = int(data['bidOpeningTime']/1000)
                    timeArrays = datetime.datetime.fromtimestamp((timeStamp))
                    # timeArrays_2 = time.localtime(timeStamp_2)
                    publishDate = timeArrays.strftime("%Y--%m--%d %H:%M:%S")
                    # bidOpeningTime = time.strftime("%Y--%m--%d %H:%M:%S", timeArrays_2)
                    # districtName = data['districtName']
                    title = (data['title'])
                    f_url = (base_url + data['url'])
                    # print(title)
                    
                    if start_time <= timeStamp <= end_time:
                        text.tag_config('link>'+f_url)
                        text.insert('insert', "【"+publishDate+"】"+title+'\n'+'\n', 'link>'+f_url)
                        text.tag_bind('link>'+f_url, "<Double-Button-1>", lambda event, f_url = f_url: open_url(event, f_url))
                        def open_url(event, f_url):
                            webbrowser.open(f_url, new=0)
                        frame1.update()
                
                
        def save_to_db():
            # 数据库连接
            conn = pymysql.connect(
                    host="localhost",
                    user="root",
                    passwd="12100910zsl.",
                    db="notice",
            )
            value_tuple_save = ()
            status_now = combox0_p2.get()
            print(status_now)
            if status_now == "(进行中)":
                ZcyAnnouncement_1 = ZcyAnnouncement[0]
            if status_now == "(已结束)":
                ZcyAnnouncement_1 = ZcyAnnouncement[1]
                
            val = update()
            # 创建val表单
            create_sql = """
                            CREATE TABLE IF NOT EXISTS `notice`.%s ( 
                            `id` INT(4) UNSIGNED ZEROFILL NOT NULL AUTO_INCREMENT COMMENT '序号', 
                            `pathName` VARCHAR(25) NOT NULL COMMENT '公告结果', 
                            `publishDate` DATETIME NOT NULL COMMENT '发布时间', 
                            `title` VARCHAR(200) NOT NULL COMMENT '公告标题', 
                            `districtName` VARCHAR(20) NOT NULL COMMENT '地域',
                            `gpCatalogName` VARCHAR(30) NOT NULL COMMENT '具体类别',
                            `url` VARCHAR(500) NOT NULL COMMENT '链接', 
                            
                            PRIMARY KEY (`id`) ) ENGINE=INNODB CHARSET=utf8 COLLATE=utf8_general_ci; 
                        """%(val)
                        
            text_p2.delete('0.0', 'end')
            value_tuple_save = value(combox11_p2, combox12_p2,combox13_p2,combox14_p2,combox15_p2,combox16_p2)
            s1 = value_tuple_save[0]+'-'+value_tuple_save[1]+'-'+value_tuple_save[2]+' 00:00:00'
            s2 = value_tuple_save[3]+'-'+value_tuple_save[4]+'-'+value_tuple_save[5]+' 00:00:00'
            start_time = time.mktime(time.strptime(s1, '%Y-%m-%d %H:%M:%S'))
            end_time = time.mktime(time.strptime(s2, '%Y-%m-%d %H:%M:%S'))

            if start_time>end_time:
                messagebox.showwarning(title="警告", message="日期选择错误！")
            # 关键字提交信息
            
            for i in range(1, 101):   # 最多显示1500条关键字查询公告
                payloadDatakw = {
                            'categoryCode': ZcyAnnouncement_1,
                            'keyword': f'{val}',
                            'pageNo': f'{i}',
                            'pageSize': 15
                }
                names["res%s" % i] = post_url(payloadDatakw)
                final_datas = clear_data(names["res%s" % i])
                for final_data in final_datas:
                    data = final_data['_source']
                    timeStamp = float(data['publishDate']/1000)
                # timeStamp_2 = int(data['bidOpeningTime']/1000)
                    timeArrays = datetime.datetime.fromtimestamp((timeStamp))
                # timeArrays_2 = time.localtime(timeStamp_2)
                    publishDate = timeArrays.strftime("%Y--%m--%d %H:%M:%S")
                # bidOpeningTime = time.strftime("%Y--%m--%d %H:%M:%S", timeArrays_2)
                # districtName = data['districtName']
                    title = data['title']
                    f_url = (base_url + data['url'])
                    districtName = data['districtName']
                    gpCatalogName = data['gpCatalogName']
                    pathName = data['pathName']
                    # print(title)
                    if (start_time <= timeStamp <= end_time)&bool(data):                            
                        cursor1 = conn.cursor()
                        cursor2 = conn.cursor()
                        sql = """insert into %s"""%(val) + """(publishDate, pathName, title, districtName, gpCatalogName, url) values(%s, %s, %s, %s, %s, %s)"""
                        
                        cursor2.execute(create_sql)
                        cursor2.close()
                        rows = cursor1.execute(sql, (publishDate, pathName, title, districtName, gpCatalogName, f_url))
                        conn.commit()
                        cursor1.close()
                        # time.sleep(1) 
                progress_bar['value'] += 1
                frame2.update()

            if rows!=0:
                messagebox.showinfo(title='恭喜！', message="保存成功")
            else:
                messagebox.showerror()(title='Error!', message="保存失败")                    
            conn.close()
            
            
            
        def function_p2():
            if combox0_p2.get() == "(进行中)":
                ZcyAnnouncement_1 = ZcyAnnouncement[0]
            if combox0_p2.get() == "(已结束)":
                ZcyAnnouncement_1 = ZcyAnnouncement[1]
            value_tuple_function_p2 = ()    
            val = update()
            text_p2.delete('0.0', 'end')
            value_tuple_function_p2 = value(combox11_p2, combox12_p2,combox13_p2,combox14_p2,combox15_p2,combox16_p2)
            s1 = value_tuple_function_p2[0]+'-'+value_tuple_function_p2[1]+'-'+value_tuple_function_p2[2]+' 00:00:00'
            s2 = value_tuple_function_p2[3]+'-'+value_tuple_function_p2[4]+'-'+value_tuple_function_p2[5]+' 00:00:00'
            start_time = time.mktime(time.strptime(s1, '%Y-%m-%d %H:%M:%S'))
            end_time = time.mktime(time.strptime(s2, '%Y-%m-%d %H:%M:%S'))

            if(start_time>end_time):
                messagebox.showwarning(title="警告", message="日期选择错误！")
            # 关键字提交信息
            for i in range(1, 6):   # 最多显示75条关键字查询公告
                payloadDatakw = {
                            'categoryCode': ZcyAnnouncement_1,
                            'keyword': f'{val}',
                            'pageNo': f'{i}',
                            'pageSize': 15
                }
                names["res%s" % i] = post_url(payloadDatakw)
                final_datas = clear_data(names["res%s" % i])
                for final_data in final_datas:
                    data = final_data['_source']
                    timeStamp = float(data['publishDate']/1000)
                    # timeStamp_2 = int(data['bidOpeningTime']/1000)
                    timeArrays = datetime.datetime.fromtimestamp((timeStamp))
                    # timeArrays_2 = time.localtime(timeStamp_2)
                    publishDate = timeArrays.strftime("%Y--%m--%d %H:%M:%S")
                    # bidOpeningTime = time.strftime("%Y--%m--%d %H:%M:%S", timeArrays_2)
                    # districtName = data['districtName']
                    title = (data['title'])
                    f_url = (base_url + data['url'])
                    # print(title)
                    if start_time<=timeStamp<=end_time:
                        text_p2.tag_config('link>'+f_url)                                                      
                        text_p2.insert('insert', "【"+publishDate+"】"+title+'\n'+'\n', 'link>'+f_url)
                        text_p2.tag_bind('link>'+f_url, "<Double-Button-1>", lambda event, f_url = f_url: open_url(event, f_url))

                    def open_url(event, f_url):
                        webbrowser.open(f_url, new=0)
                    frame2.update()
        
        def get_subword_list():
            cmd = 'notepad subscribe_keyword.txt'
            os.system(cmd)
        
        def subscribe():
            # 文件操作
            var = entry.get()
            counts1 = []
            with open("subscribe_keyword.txt", "r") as f:
                for count1 in f.readlines():
                    counts1.append(count1.strip('\n'))
                if var not in counts1:
                    with open("subscribe_keyword.txt", "a+") as f:                
                        f.write(var+"\n")
                        messagebox.showinfo(title="提示", message="订阅成功！")
                else:
                    messagebox.showwarning(title="重复订阅", message="您已订阅过%s,请勿重复订阅！"%var) # 弹窗提示
            update()
        
        
        def update():
            counts = []
            with open("subscribe_keyword.txt", "r") as f:
                for count in f.readlines():
                    counts.append(count.strip('\n'))
                lens = len(counts)
            lable1 = tk.Label(frame2, text="已订阅数："+str(lens), font=("宋体", 12, 'bold'))
            lable1.grid(row=0, sticky=W, padx=20, pady=20)           
            combox9_p2['values'] = counts
            x =  combox9_p2.get()
            return x
        
        
        names = locals() # 创建动态变量功能
        year_select = ['2010', '2011', '2012', '2013', '2014', '2015', '2016', '2017', '2018', '2019', '2020', '2021', '2022', '2023', '2024', '2025', '2026', '2027', '2028', '2029', '2030']
        
        month_select = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']
        
        day_select = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24', '25', '26', '27', '28', '29', '30', '31']
        
        
        tab = ttk.Notebook(window)  # 创建分页栏
        style = ttk.Style()
        style.configure('TNotebook.Tab', font=('宋体', '15', 'bold'), padding=[10, 10])
        style.theme_use('classic')


        """
        
        **************第一页*************
        ***********采购项目公告***********
        
        
        """
        frame1 = tk.Frame(tab)
        tab.add(frame1, text="采购项目公告")
        
        key_word_label = tk.Label(frame1, text='请输入关键词：', font=("宋体", 12, 'bold'))
        key_word_label.grid(row=0, sticky=W, padx=20, pady=20)
        kw = tk.StringVar()
        start_time_p1 = tk.Label(frame1, text='开始时间：', font=("宋体", 12, 'bold'))
        start_time_p1.grid(row=0, column=2, sticky=E)
        # 开始时间
        # 年
        combox1 = ttk.Combobox(frame1, width=5)
        combox1['value'] = year_select
        combox1.current(11)
        combox1.grid(row=0, column=3, sticky=E)
        #月
        combox2 = ttk.Combobox(frame1, width=3)
        combox2['value'] = month_select
        combox2.current(0)
        combox2.grid(row=0, column=4, sticky=E)
        # 日
        combox3 = ttk.Combobox(frame1, width=3)
        combox3['value'] = day_select
        combox3.current(0)
        combox3.grid(row=0, column=5, sticky=E)
        
        # 结束时间
        end_time = tk.Label(frame1, text='结束时间：', font=("宋体", 12, 'bold'))
        end_time.grid(row=0, column=6, sticky=E)
        # 年
        combox4 = ttk.Combobox(frame1, width=5)
        combox4['value'] = year_select
        combox4.current(11)
        combox4.grid(row=0, column=7, sticky=E)
        # 月
        combox5 = ttk.Combobox(frame1, width=3)
        combox5['value'] = month_select
        combox5.current(6)
        combox5.grid(row=0, column=8, sticky=E)
        #日
        combox6 = ttk.Combobox(frame1, width=3)
        combox6['value'] = day_select
        combox6.current(26)
        combox6.grid(row=0, column=9, sticky=E)
        # 输入框 获取关键字
        
        entry = tk.Entry(frame1, width=25, textvariable=kw)
        entry.grid(row=0, column=1, sticky=E)
        val1 = entry.get()
        
        
        web_label = tk.Label(frame1, text='选择网站：', font=("宋体", 12, 'bold'))
        web_label.grid(row=0, column=11, sticky=W, padx=20, pady=20)
        
        combox8 = ttk.Combobox(frame1, width=25)
        combox8['values'] = ('新疆政府采购网','网站2','网站3','网站4','网站5')
        combox8.current(0)
        combox8.grid(row=0, column=12, sticky=E)
        
        # 搜索按钮
        btn1 = tk.Button(frame1, text="搜索", width=15, command=lambda:func(text_p1, ZcyAnnouncement[0]))
        btn1.grid(row=0, column=13, sticky=E, padx=20, pady=20)
        window.bind("<Return>", lambda event=None: btn1.invoke())  # 提交按钮绑定回车
        # 订阅按钮
        btn2 = tk.Button(frame1, text="订阅", width=15, command=subscribe)
        btn2.grid(row=0, column=14, sticky=E, padx=20, pady=20)
        
        text_p1 = tk.Text(frame1, width=161, height=43, font=("宋体", 13))
        text_p1.grid(row=2, columnspan=50, sticky=W, padx=20, pady=20)
        text_p1.insert('insert', "————————————————————最新公告————————————————————"+ '\n' + '\n')
        # 多线程加速
        my_thread_p1 = threading.Thread(target=content_select, args=(ZcyAnnouncement[0],text_p1))
        my_thread_p1.start()
        # content_select(ZcyAnnouncement[0],text_p1)
        
        
        """
        
        **************第二页*************
        ***********订阅查询界面***********
        
        
        """
        frame2 = tk.Frame(tab)
        tab.add(frame2, text="订阅信息")
        counts = []
        with open("subscribe_keyword.txt", "r") as f:
            for count in f.readlines():
                counts.append(count.strip('\n'))
            lens = len(counts)
        lable1 = tk.Label(frame2, text="已订阅数："+str(lens), font=("宋体", 12, 'bold'))
        lable1.grid(row=0, sticky=W, padx=20, pady=20)
        combox9_p2 = ttk.Combobox(frame2, width=30)
        combox9_p2['values'] = counts
        combox9_p2.current(0)
        combox9_p2.grid(row=0, column=1, sticky=E)
        
        combox0_p2 = ttk.Combobox(frame2, width=7)
        combox0_p2['value'] = ['(进行中)', '(已结束)']
        combox0_p2.current(0)
        combox0_p2.grid(row=0, column=2, sticky=E)
        
        btn_p2_sure = tk.Button(frame2, text="确定", width=15, command=function_p2)
        btn_p2_sure.grid(row=0, column=11, sticky=E, padx=20, pady=20)
        
        # btn4 = tk.Button(frame2, text="订阅列表", width=15, command=get_subword_list)
        # btn4.grid(row=0, column=12, sticky=E, padx=20, pady=20)
        
        btn_p2_savedb = tk.Button(frame2, text="存至数据库", width=15, command=save_to_db)
        btn_p2_savedb.grid(row=0, column=12, sticky=E, padx=20, pady=20)
        
        progress_bar = ttk.Progressbar(frame2)
        # progress_bar['maximun'] = 100
        progress_bar['value'] = 0
        progress_bar.grid(row=0, column=13, sticky=E, padx=20, pady=20)
        # 订阅信息文本框
        text_p2 = tk.Text(frame2, width=161, height=45, font=("宋体", 13))
        text_p2.grid(row=6, columnspan=50, sticky=W, padx=20, pady=20)
        
        
        
        start_time_p2 = tk.Label(frame2, text='开始时间：', font=("宋体", 12, 'bold'))
        start_time_p2.grid(row=0, column=3, sticky=E)
        # 开始时间
        # 年
        combox11_p2 = ttk.Combobox(frame2, width=5)
        combox11_p2['value'] = year_select
        combox11_p2.current(11)
        combox11_p2.grid(row=0, column=4, sticky=E)
        #月
        combox12_p2 = ttk.Combobox(frame2, width=3)
        combox12_p2['value'] = month_select
        combox12_p2.current(0)
        combox12_p2.grid(row=0, column=5, sticky=E)
        # 日
        combox13_p2 = ttk.Combobox(frame2, width=3)
        combox13_p2['value'] = day_select
        combox13_p2.current(0)
        combox13_p2.grid(row=0, column=6, sticky=E)
        
        # 结束时间
        end_time = tk.Label(frame2, text='结束时间：', font=("宋体", 12, 'bold'))
        end_time.grid(row=0, column=7, sticky=E)
        # 年
        combox14_p2 = ttk.Combobox(frame2, width=5)
        combox14_p2['value'] = year_select
        combox14_p2.current(11)
        combox14_p2.grid(row=0, column=8, sticky=E)
        # 月
        combox15_p2 = ttk.Combobox(frame2, width=3)
        combox15_p2['value'] = month_select
        combox15_p2.current(6)
        combox15_p2.grid(row=0, column=9, sticky=E)
        #日
        combox16_p2 = ttk.Combobox(frame2, width=3)
        combox16_p2['value'] = day_select
        combox16_p2.current(26)
        combox16_p2.grid(row=0, column=10, sticky=E)
        
        """
        
        **************第三页*************
        ***********采购结果公告***********
        
        
        """
        frame3 = tk.Frame(tab)
        tab.add(frame3, text="采购结果公告")
        key_word_label_p3 = tk.Label(frame3, text='请输入关键词：', font=("宋体", 12, 'bold'))
        key_word_label_p3.grid(row=0, sticky=W, padx=20, pady=20)
        kw = tk.StringVar()
        start_time_p3 = tk.Label(frame3, text='开始时间：', font=("宋体", 12, 'bold'))
        start_time_p3.grid(row=0, column=2, sticky=E)
        # 开始时间
        # 年
        combox1_p3 = ttk.Combobox(frame3, width=5)
        combox1_p3['value'] = year_select
        combox1_p3.current(11)
        combox1_p3.grid(row=0, column=3, sticky=E)
        #月
        combox2_p3 = ttk.Combobox(frame3, width=3)
        combox2_p3['value'] = month_select
        combox2_p3.current(0)
        combox2_p3.grid(row=0, column=4, sticky=E)
        # 日
        combox3_p3 = ttk.Combobox(frame3, width=3)
        combox3_p3['value'] = day_select
        combox3_p3.current(0)
        combox3_p3.grid(row=0, column=5, sticky=E)
        
        # 结束时间
        end_time_p3 = tk.Label(frame3, text='结束时间：', font=("宋体", 12, 'bold'))
        end_time_p3.grid(row=0, column=6, sticky=E)
        # 年
        combox4_p3 = ttk.Combobox(frame3, width=5)
        combox4_p3['value'] = year_select
        combox4_p3.current(11)
        combox4_p3.grid(row=0, column=7, sticky=E)
        # 月
        combox5_p3 = ttk.Combobox(frame3, width=3)
        combox5_p3['value'] = month_select
        combox5_p3.current(6)
        combox5_p3.grid(row=0, column=8, sticky=E)
        #日
        combox6_p3 = ttk.Combobox(frame3, width=3)
        combox6_p3['value'] = day_select
        combox6_p3.current(26)
        combox6_p3.grid(row=0, column=9, sticky=E)
        # 输入框 获取关键字
        
        entry_p3 = tk.Entry(frame3, width=25, textvariable=kw)
        entry_p3.grid(row=0, column=1, sticky=E)
        
        
        web_label_p3 = tk.Label(frame3, text='选择网站：', font=("宋体", 12, 'bold'))
        web_label_p3.grid(row=0, column=11, sticky=W, padx=20, pady=20)
        
        combox8_p3 = ttk.Combobox(frame3, width=25)
        combox8_p3['values'] = ('新疆政府采购网','网站2','网站3','网站4','网站5')
        combox8_p3.current(0)
        combox8_p3.grid(row=0, column=12, sticky=E)
        
        # 搜索按钮
        btn1_p3 = tk.Button(frame3, text="搜索", width=15, command=lambda :func(text_p3, ZcyAnnouncement[1]))
        btn1_p3.grid(row=0, column=13, sticky=E, padx=20, pady=20)
        window.bind("<Return>", lambda event=None: btn1.invoke())  # 提交按钮绑定回车
        
        text_p3 = tk.Text(frame3, width=161, height=43, font=("宋体", 13))
        text_p3.grid(row=2, columnspan=50, sticky=W, padx=20, pady=20)
        text_p3.insert('insert', "————————————————————最新采购结果————————————————————"+ '\n' + '\n')
        # 多线程加速
        my_thread_p3 = threading.Thread(target=content_select, args=(ZcyAnnouncement[1], text_p3))
        my_thread_p3.start()
        

        tab.pack(expand=True, fill=tk.BOTH)
        window.mainloop()

if __name__ == "__main__":
    tbm = TestBenchMaker()
    tbm.initialGUI()
