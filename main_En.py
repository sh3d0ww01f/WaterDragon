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
    raw = json.loads(requests.post(url=url, data=data).text)
    for item in raw["rows"]:
        port.append(item["Port"])


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
    raw = json.loads(requests.post(url=url, data=data).text)
    bridgeport = raw["bridgePort"]
    ip = raw["ip"]
    id = 0
    for item in raw["rows"]:
        # print(item)
        print("ClientID:", item["Id"], split_str, "Remark:", item["Remark"], split_str, "Ifcrypto:", item["Cnf"]["Crypt"],
              split_str, "Verifykey:", item["VerifyKey"], split_str, "Ifconnect:", item['IsConnect'], split_str, "ListenPort:",
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
            print("add successfully!")
        else:
            print("Wrong:failed to add,please check if the information repeat!")
            delete(raw["rows"][-1]["Id"])


def add():
    OutsidePort = int(input("ListenPort:"))
    vkey = str(input("key:"))
    ifcrypt = int(input("Ifcrypt(1/0):"))
    remark = str(input("Remark:"))
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
    clientid = int(input("Choose the client ID that you want to del:"))
    raw = json.loads(delete(clientid))
    status = raw["status"]
    if (status == 1):
        print("Delete successfully")
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
        print("[+] Connect WebApi successfully")
        return 1
    except:
        print("[-] Wrong : Connect WebApi ,Retry please")
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
    id = input("choose a id that you want to choose of a socks5 client:")
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
    choose = input("Press the ID you want to stop:")
    resp = requests.post(f"https://api.github.com/repos/{username}/{repo}/actions/runs/{id_list[int(choose)]}/cancel",
                         headers=headers).status_code
    if (resp == 202):
        print("stop process successfully")


# ---------------------------------------------------------------------------------------------------


current = "menu"
s = string = """
            [+] press socks5 to enter socks5 manager(add、del、list) 
            [+] press manager to enter GithubAction process manager
            [+] press back to back to menu
            [+] press help to get HELP information
            """
print(s)
while True:
    text = input(current + ">")
    if (current == "menu" and text == "help"):
        print(string)
    elif (current == "socks5" and text == "help"):
        print("""
            [+] press add to add socks5 client
            [+] press del to delete socks5 client
            [+] press list to list all socks5 client 
            """)
    elif (current == "manager" and text == "help"):
        print("""
                    [+] press select to select a socks5 client and connect
                    [+] press stop to cancel a GithubAction process  
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