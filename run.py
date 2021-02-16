import requests, json, time
import win32com.client
import cybos_util
import pymysql, pymongo
from datetime import datetime

class RunCrawling:
    cybos_obj = None
    chart_obj = None
    rcv_data = dict()
    db_conn = None
    mongo_conn = None
    def getToken(self, id_var, pw_var):
        time.sleep(0.3)
        try:
            post_data = {"username":id_var, "password":pw_var}
            req1 = requests.post("http://192.168.229.1:898/api/token/", data=post_data)
            print(req1.text)
            json_data = json.loads(req1.text)
            access_token = json_data["access"]
            return access_token
        except:
            return self.getToken(id_var, pw_var)

    def __init__(self, api_id, api_pw):
        self.cybos_obj = win32com.client.Dispatch("CpUtil.CpCybos")
        self.chart_obj = cybos_util.CpStockChart()
        isConnect = self.cybos_obj.IsConnect
        self.mongo_conn = pymongo.MongoClient('192.168.229.1', 27018)
        if isConnect==0:
            print("PLUS가 정상적으로 연결되지 않았습니다.")
            exit()

        page_num = 1
        content_length = -1
        start_flag = False
        headers = {"Authorization" : "Bearer " + self.getToken(api_id, api_pw)}
        key_arr = self.mongo_conn["candle_db"].collection_names()
        while content_length!=0:
            headers = {"Authorization" : "Bearer " + self.getToken(api_id, api_pw)}
            req2 = requests.get("http://192.168.229.1:898/api/stockcode/?page=" + str(page_num), headers=headers)
            json_data = json.loads(req2.text)
            content_length = len(json_data["results"])

            for elem in json_data["results"]:
                code = elem["code"]B
                if len(str(code)) != 6:
                    print("code updated..")
                    code = "0"*(6-len(str(code))) + str(code)
                code = "A" + str(code)
                print("target code : " + str(code))
                
                # 프로그램 에러 혹은 종료로 인해 다시 시작할 때 중복되는 코드 패스 
                if ("stock__" + code) in key_arr:
                    print('이미 있습니다 code : ' + code)
                    continue
                start_time = time.time()
                try:
                    self.chart_obj.RequestMT(code, ord('m'), 1, 200000, self, 0,  False)
                except:
                    print("code error...!!")
                    continue
                self.rcv_data["data_count"] = len(self.rcv_data["date"])
                print(self.rcv_data["data_count"])
                mdb = self.mongo_conn.candle_db["stock__" + code]
                for i in range(0, self.rcv_data["data_count"]):
                    try:
                        mdb.insert_one({"open":self.rcv_data["open"][i], "close":self.rcv_data["close"][i], "high":self.rcv_data["high"][i], "low":self.rcv_data["low"][i], "volume":self.rcv_data["volume"][i], "created":datetime.strptime(str(self.rcv_data["date"][i]), "%Y%m%d%H%M").strftime("%Y-%m-%d %H:%M:00")})
                    except:
                        time.sleep(10)
                        self.mongo_conn = pymongo.MongoClient('192.168.229.1', 27018)
                        mdb = self.mongo_conn.candle_db["stock__" + code]
                        mdb.insert_one({"open":self.rcv_data["open"][i], "close":self.rcv_data["close"][i], "high":self.rcv_data["high"][i], "low":self.rcv_data["low"][i], "volume":self.rcv_data["volume"][i], "created":datetime.strptime(str(self.rcv_data["date"][i]), "%Y%m%d%H%M").strftime("%Y-%m-%d %H:%M:00")})
                        print("reconnect completed..")
                end_time = time.time()
                print("time_wrap : " + str(end_time-start_time))
            page_num += 1

RunCrawling("{id}", "{pw}")
