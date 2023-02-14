import json
import hashlib
import base64
import time

global port, clientid
global port, clientid, client_all
import requests

client_all = {}
port, clientid = [], []
split_str = "\n|\n-->"
global api, auth_kkey
# -------------------------------------------------------------
api = "http://xxxxxxxx.xxx.xxxx.xxx:xx"
auth_kkey = "xxxxxxxxx"
token = "ghp_xxxxxxxxxxxxxxxxx"  # github_token
# ------------------------------------------------------------

CreatNew_name = "WaterDragon"
headers = {
    "Authorization": "token " + token,
    "Accept": "application/vnd.github.v3+json"
}
BaseInfo = "https://api.github.com/user"


# ------------------------------------------------------------nps--------------------------------
def getkey():
    a = requests.get(url=api + "/auth/gettime").text
    time = json.loads(a)["time"]
    raw = auth_kkey + str(time)
    auth_key = hashlib.md5(raw.encode()).hexdigest()
    return auth_key, time


def list_tunnel():
    url = api + "/index/gettunnel"
    auth_key, time = getkey()
    data = {
        "auth_key": auth_key,
        "timestamp": time,
        "offset": 0,
        "type": "socks5",
        "limit": 10,
        "search": ""
    }
    try:
        raw = json.loads(requests.post(url=url, data=data).text)
        for item in raw["rows"]:
            port.append(item["Port"])
    except:
        print("[-] 获取tunnel失败");exit(0)


def list_all():
    list_tunnel()
    url = api + "/client/list"
    auth_key, time = getkey()
    data = {
        "auth_key": auth_key,
        "timestamp": time,
        "start": 0,
        "limit": 10
    }
    try:
        raw = json.loads(requests.post(url=url, data=data).text)
        bridgeport = raw["bridgePort"]
        ip = raw["ip"]
        id = 0
    except:
        print("[-] 获取client失败");exit(0)
    for item in raw["rows"]:
        # print(item)
        print("客户端ID:", item["Id"], split_str, "备注:", item["Remark"], split_str, "加密情况:", item["Cnf"]["Crypt"],
              split_str, "认证秘钥:", item["VerifyKey"], split_str, "现在是否连接:", item['IsConnect'], split_str, "监听端口:",
              port[id], split_str,
              "command:./npc -server={0}:{1} -vkey={2} -type=tcp".format(ip, bridgeport, item["VerifyKey"]),
              "\n--------------------------")
        client_all.update({item["Id"]: {"remark": item["Remark"], "crypt": item["Cnf"]["Crypt"],
                                        "verifykey": item["VerifyKey"], "isconnect": item['IsConnect'],
                                        "command": "command:./npc -server={0}:{1} -vkey={2} -type=tcp".format(ip,
                                                                                                              bridgeport,
                                                                                                              item[
                                                                                                                  "VerifyKey"])}})
        id = id + 1


def add_new(OutsidePort, vkey, ifcrypt, remark):
    auth_key, time = getkey()
    client_data = {
        "auth_key": auth_key,
        "timestamp": time,
        "remark": remark,
        "u": "",
        "p": "",
        "vkey": vkey,
        "config_conn_allow": 1,
        "compress": 0,
        "crypt": ifcrypt
    }
    resp1 = requests.post(url=api + "/client/add", data=client_data).text
    if (json.loads(resp1)["status"] == 1):
        url = api + "/client/list"
        auth_key, time = getkey()
        data = {
            "auth_key": auth_key,
            "timestamp": time,
            "start": 0,
            "limit": 10
        }
        raw = json.loads(requests.post(url=url, data=data).text)
        try:
            tmp = raw["rows"][-1]["Id"]
        except:
            print("[-] 添加失败");exit(0)
        tunnel_data = {
            "auth_key": auth_key,
            "timestamp": time,
            "type": "socks5",
            "client_id": raw["rows"][-1]["Id"],
            "remark": "",
            "port": OutsidePort,
            "target": "",
            "local_path": "",
            "strip_pre": "",
            "password": ""
        }
        resp2 = requests.post(url=api + "/index/add", data=tunnel_data).text
        if json.loads(resp2)["status"] == 1:
            print("添加成功!")
        else:
            print("添加失败，请检查新添加信息是否与已有重复")
            delete(raw["rows"][-1]["Id"])


def add():
    OutsidePort = int(input("准备开放的端口:"))
    vkey = str(input("通信密钥:"))
    ifcrypt = int(input("是否加密(1/0):"))
    remark = str(input("备注:"))
    add_new(OutsidePort, vkey, ifcrypt, remark)


def delete(clientid):
    url = api + "/client/del"
    auth_key, time = getkey()
    client_data = {
        "auth_key": auth_key,
        "timestamp": time,
        "id": clientid
    }
    resp1 = requests.post(url=api + "/client/del", data=client_data).text
    return resp1


def ddel():
    clientid = int(input("输入要删除的客户端ID:"))
    raw = json.loads(delete(clientid))
    status = raw["status"]
    if (status == 1):
        print("删除成功")
    else:
        print(raw["msg"])


def checkc():
    url = api + "/client/list"
    auth_key, time = getkey()
    data = {
        "auth_key": auth_key,
        "timestamp": time,
        "start": 0,
        "limit": 10
    }
    try:
        raw = json.loads(requests.post(url=url, data=data).text)
        print("成功连接WebApi")
        return 1
    except:
        print("连接WebApi错误 请检查后再试")
        return 0


# ----------------------------------------------------------------------------------------------
# ------------------------------GITHUB_ACTION--------------------------------------------------------
def base64encode(text):
    return base64.b64encode(text).decode()


def JudgeIfExist_YML(owner, repo, headers, FileName):
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/" + FileName
    raw = requests.get(url, headers=headers)
    if (raw.status_code == 200):
        return json.loads(raw.text)[0]["sha"]
    else:
        return False


def UploadMainYml(owner, repo, headers, command):
    Judge = JudgeIfExist_YML(owner, repo, headers, ".github/workflows")
    if (Judge):
        with open("main.yml", 'r') as f:
            MainYml_text = base64encode(f.read().format(command).encode())
        url = f"https://api.github.com/repos/{owner}/{repo}/contents/.github/workflows/main.yml"
        data = {
            "message": "update",
            "content": MainYml_text,
            "sha": Judge
        }
        res = requests.put(url, data=json.dumps(data), headers=headers)
        if (res.status_code == 200):
            print("[+] Successfully Cover main.yml!")
        else:
            print("[-] Unknown error")
    else:
        with open("main.yml", 'r') as f:
            MainYml_text = base64encode(f.read().encode())
        url = f"https://api.github.com/repos/{owner}/{repo}/contents/.github/workflows/main.yml"
        data = {
            "message": "update",
            "content": MainYml_text,
        }

        res = requests.put(url, data=json.dumps(data), headers=headers)
        if (res.status_code == 201):
            print("[+] Successfully Upload main.yml!")
        else:
            print("[-] Unknown error")


def CreatNew(CreatNew_name, headers):
    data = {
        "name": CreatNew_name,
        "private": True,
        "description": "WaterDragon.Make you  flexible like water."
    }
    a = requests.post("https://api.github.com/user/repos", headers=headers, data=json.dumps(data))
    if (a.status_code == 201):
        print("[+] SUCCESSFULLY Creat Cloud repo!")
    elif (a.status_code == 422):
        print("[-] The name is existed!Please use it or change a NAME")


def Use(owner, repo, headers, command):
    
    onestep = requests.put(f"https://api.github.com/user/starred/{owner}/{repo}", headers=headers)
    if (onestep.status_code == 204):
        print("[+] Start Success")
    requests.delete(f"https://api.github.com/user/starred/{owner}/{repo}", headers=headers)


def Enable_workflow(owner, repo, headers):
    raw = requests.get(f"https://api.github.com/repos/{owner}/{repo}/actions/workflows", headers=headers)
    #print(raw.text)
    workflow_id = json.loads(raw.text)["workflows"][0]["id"]
    r = requests.put(f"https://api.github.com/repos/{owner}/{repo}/actions/workflows/{workflow_id}/enable",
                     headers=headers)
    data = {
        "enabled": True
    }
    r = requests.put(f"https://api.github.com/repos/{owner}/{repo}/actions/permissions", data=json.dumps(data),
                     headers=headers)
    if (r.status_code == 204):
        print(f"[+] Enable workflow_id:{workflow_id}")
    else:
        print(r.text)
def checkd(BaseInfo, headers):
    resp = requests.get(BaseInfo, headers=headers)
    if (resp.status_code != 200):
        print("[-] Login failed ! :(")
        print("[-] Wrong github Access_Token.Plesse get the token: ")
        print("    https://github.com/settings/tokens and generate a token for this app")
        return 0
    else:
        return resp
def select():
    list_all()
    id = input("输入选择的客户端id:")
    return client_all[int(id)]["command"].split('command:')[1]


def run_action(username, repo, headers, command):
    CreatNew(repo, headers)  # Creat
    UploadMainYml(username, repo, headers, command)
    time.sleep(1)
    Enable_workflow(username, repo, headers)
    Use(username, repo, headers, command)


def stop(username, repo, headers):
    order = 0
    id_list = []
    raw = requests.get(f"https://api.github.com/repos/{username}/{repo}/actions/workflows", headers=headers)
    workflow_id = json.loads(raw.text)["workflows"][0]["id"]
    raw = requests.get(f"https://api.github.com/repos/{username}/{repo}/actions/workflows/{workflow_id}/runs",
                       headers=headers).text
    for item in json.loads(raw)["workflow_runs"][:10]:  # item["workflow_id"],
        print(order, ") id:", item["id"], "\n|目前状态:", item["status"], "\n|起始时间", item["run_started_at"])
        id_list.append(item["id"])
        order = order + 1
    choose = input("请输入要取消运行的ID前的序号:")
    resp = requests.post(f"https://api.github.com/repos/{username}/{repo}/actions/runs/{id_list[int(choose)]}/cancel",
                         headers=headers).status_code
    if (resp == 202):
        print("取消运行成功")


# ---------------------------------------------------------------------------------------------------


current = "menu"
s = string = """
            [+] 输入 socks5 进入socks5隧道管理(增、减、查看) 
            [+] 输入 manager 进入Github机器管理
            [+] 输入 back 回退
            [+] 输入 help 获取帮助
            """
print(s)
while True:
    text = input(current + ">")
    if (current == "menu" and text == "help"):
        print(string)
    elif (current == "socks5" and text == "help"):
        print("""
            [+] 输入 add 增加socks5隧道
            [+] 输入 del 删除已有socks5隧道
            [+] 输入 list 列出现存socks5隧道
            """)
    elif (current == "manager" and text == "help"):
        print("""
                    [+] 输入 select 选择已有socks5 并获取连接
                    [+] 输入 stop 取消运行现隧道
                    """)
    if (text == "socks5"):
        current = "socks5"
        if not checkc():
            current = "menu"
    elif (text == "manager"):
        current = "manager"
        resp = checkd(BaseInfo, headers)
        if (not resp):
            current = "menu"
            exit(0)
        response_raw = resp.text
        response = json.loads(response_raw)
        username = response["login"]
        repo_all = response["repos_url"]
        print("[+] Login successfully ! Welcome :)" + username)
    elif (text == "back"):
        current = "menu"
    if (current == "socks5"):
        if (text == "list"):
            list_all()
        elif (text == "add"):
            add()
        elif (text == "del"):
            ddel()
    if (current == "manager"):
        if (text == "select"):
            command = select()
            run_action(username, CreatNew_name, headers, command)
        if (text == "stop"):
            stop(username, CreatNew_name, headers)
