# -*- coding: utf-8 -*-
import requests
import json
import re
import datetime as DT
import lib.functions as f
import time
import subprocess
import os


class agqr:
    AGQR_URL = "https://agqr.sun-yryr.com/api/today"

    def __init__(self):
        res = requests.get(self.AGQR_URL)
        res.encoding = "utf-8"
        self.isKeyword = False
        self.reload_date = DT.date.today()
        self.program_agqr = json.loads(res.text)
        print("agqr load at")
        print(DT.date.today())

    def reload_program(self):
        print("----------agqr reload------------------")
        print("agqr load at")
        print(DT.date.today())
        res = requests.get(self.AGQR_URL)
        res.encoding = "utf-8"
        self.program_agqr = json.loads(res.text)
        self.reload_date = DT.date.today()

    def change_keywords(self, keywords):
        if bool(keywords):
            word = "("
            for keyword in keywords:
                word += keyword
                word += "|"
            word = word.rstrip("|")
            word += ")"
            print(word)
            self.isKeyword = True
            self.keyword = re.compile(word)
        else:
            self.isKeyword = False

    def delete_keywords(self):
        self.change_keywords([])

    def search(self):
        if (self.isKeyword is False):
            return []
        res = []
        for prog in self.program_agqr:
            ck = False
            title = prog.get("title")
            pfm = prog.get("pfm")
            if (self.keyword.search(title)):
                ck = True
            if (ck is False) and (pfm is not None):
                if (self.keyword.search(pfm)):
                    ck = True
            if (ck):
                res.append({
                    "title": title.replace(" ", "_").replace("/", "_"),
                    "ft": prog.get("ft"),
                    "DT_ft": DT.datetime.strptime(prog.get("ft"), "%Y%m%d%H%M"),
                    "to": prog.get("to"),
                    "dur": int(prog.get("dur")),
                    "pfm": pfm
                })
        if (DT.datetime.now().strftime("%w") == "0"):
            res.append({
                "title": "WarikirenaiRadio",
                "ft": DT.datetime.now().strftime("%Y%m%d0700"),
                "DT_ft": DT.datetime.strptime(DT.datetime.now().strftime("%Y%m%d0700"), "%Y%m%d%H%M"),
                "to": DT.datetime.now().strftime("%Y%m%d0730"),
                "dur": int("30"),
                "pfm": "227"
            })
        if (DT.datetime.now().strftime("%w") == "6"):
            res.append({
                "title": "WarikirenaiRadioSat",
                "ft": DT.datetime.now().strftime("%Y%m%d1600"),
                "DT_ft": DT.datetime.strptime(DT.datetime.now().strftime("%Y%m%d1600"), "%Y%m%d%H%M"),
                "to": DT.datetime.now().strftime("%Y%m%d1630"),
                "dur": int("30"),
                "pfm": "227"
            })
        if bool(res):
            return res
        else:
            return []

    def rec(self, data):
        program_data = data[0]
        print("agqr start!")
        print(program_data)

        wait_start_time = data[1]
        SAVEROOT = data[2]

        dir_path = SAVEROOT + "/" + program_data["title"].replace(" ", "_").replace("/", "_")
        f.createSaveDir(dir_path)

        file_path = dir_path + "/" + program_data["title"].replace(" ", "_").replace("/", "_") + "_" + program_data["ft"][:12]
        cwd = ('rtmpdump -r rtmp://fms-base1.mitene.ad.jp/agqr/aandg1 ')
        cwd += ('--stop %s ' % str(program_data["dur"] * 60))
        cwd += ('--live -o "%s.flv"' % (file_path))
        time.sleep(wait_start_time)
        # rtmpdumpは時間指定の終了ができるので以下を同期処理にする
        subprocess.run(cwd, shell=True)
        # 変換をする
        cwd2 = ('ffmpeg -loglevel error -i "%s.flv" -vn -c:a aac -b:a 256k "%s.m4a"' % (file_path, file_path))
        subprocess.run(cwd2, shell=True)
        print("agqr finish!")
        if (f.is_recording_succeeded(file_path)):
            f.recording_successful_toline(program_data["title"])
            # fs = open(file_path+".m4a", "rb")
            # f.DropBox.upload(program_data["title"], program_data["ft"], fs.read())
            url = f.Swift.upload_file(filePath=file_path + ".m4a")
            f.Mysql.insert(
                title=program_data["title"].replace(" ", "_").replace("/", "_"),
                pfm=program_data["pfm"],
                timestamp=program_data["ft"] + "00",
                station="AGQR",
                uri=url
            )
            if (f.Swift.hadInit):
                cmd = 'rm "%s"' % (file_path + ".m4a")
                subprocess.run(cmd, shell=True)
            # fs.close()
        else:
            f.recording_failure_toline(program_data["title"])
        #os.remove(file_path + ".flv")
