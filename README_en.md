# WaterDragon  v1.0
## Use Github Action to achieve proxy function
### Core
This project  **is based on NPS[https://github.com/ehang-io/nps] + Github Action**
## Tips:If you use it ,you can get a large number of IP because GithubAction is supported by MicroSoftCloud,it's really a "fertile soil"
# Usage

#### 1.Install NPS on our vps
download it first [https://github.com/ehang-io/nps/releases/tag/v0.26.10](https://github.com/ehang-io/nps/releases/tag/v0.26.10)
download appropriate version, I download `linux_amd64_server.tar.gz` for example
execute `tar -axvf linux_amd64_server.tar.gz`to unzip 
![](https://raw.githubusercontent.com/sh3d0ww01f/WaterDragon/main/img/222.png)
#### 2.Then we should modify config
`cd conf`
`vim nps.conf`
we change these two files in total
###### ①. Change web_password
**change it as complex as we can** it is password of nps-gui,but I will  use its WebApi instead of nps-gui, so if you use adopt deafult password,you maybe get attack by others
###### ②.Open WebApi Mode
![](https://raw.githubusercontent.com/sh3d0ww01f/WaterDragon/main/img/333.png)
remove the comment before `auth_key`,and change the value of `auth_key`
**advice:**change `auth_crypt_key` 
**then remember the auth_key we changed  and hold it in reserve for next step**
##### ③.http_proxy_port
Advice:U had batter to change it ,because it maybe conflict with the service which listen 80 port  **such as apache，nginx**
##### ④.web_port
**Some information of api**, it listen 8080 port if you never change it ,otherwise the address of Api is: vps_ip:web_port
then we execute `cd .. ` and ` ./nps`
If NPS can start successfully ,you can  let it runs in the background:`nohup ./nps &`
#### 3.Get Github_Token
##### GOTO[https://github.com/settings/tokens](https://github.com/settings/tokens)and Operate according to the images below


![](https://raw.githubusercontent.com/sh3d0ww01f/WaterDragon/main/img/444.png)
![](https://raw.githubusercontent.com/sh3d0ww01f/WaterDragon/main/img/555.png)
![](https://raw.githubusercontent.com/sh3d0ww01f/WaterDragon/main/img/666.png)
**You need to remember them for next step**
#### Modify Script
Firstly,we download the script:
`git clone https://github.com/sh3d0ww01f/WaterDragon.git`
and then modify file named `main.py`
![](https://raw.githubusercontent.com/sh3d0ww01f/WaterDragon/main/img/777.png)
   ①**type the address of your Api :api(http://vps_ip:web_port，if u neven change web_port, the Api is http://vps_ip:8080)**
 ②**type your auth_key behind**
 ③**type your token **
# Run the script
`python3 main.py`
![](https://raw.githubusercontent.com/sh3d0ww01f/WaterDragon/main/img/111en.png)
**①.Type socks5 to enter socks5 manager, we need to add it first**
![](https://raw.githubusercontent.com/sh3d0ww01f/WaterDragon/main/img/222en.png)
if "Connect WebApi successfully" appear,it means the config of your api is corrent
**②.type add to add a new socsk5 client**
![](https://raw.githubusercontent.com/sh3d0ww01f/WaterDragon/main/img/333en.png)
**you can set ListenPort wantonly as long as you can connect it.Besides 1 (encryption)，0(No encryption)**
**③.Now we creat socks5 client , let us use it **
type	`back` to back 'menu',and then type **`manager` to enter Github Action Manager**
![](https://raw.githubusercontent.com/sh3d0ww01f/WaterDragon/main/img/444en.png)
type `select` to select the socks5 client you want to connect 
I choose No. 19 as an example
![](https://raw.githubusercontent.com/sh3d0ww01f/WaterDragon/main/img/555en.png)

when it appear `start success` , it means start successfully

![](https://raw.githubusercontent.com/sh3d0ww01f/WaterDragon/main/img/4444.png)
then we connect it 

# Result
![ ](https://raw.githubusercontent.com/sh3d0ww01f/WaterDragon/main/img/1.png)
![](https://raw.githubusercontent.com/sh3d0ww01f/WaterDragon/main/img/2.png)
![](https://raw.githubusercontent.com/sh3d0ww01f/WaterDragon/main/img/3.png)
![](https://raw.githubusercontent.com/sh3d0ww01f/WaterDragon/main/img/4.png)
![](https://raw.githubusercontent.com/sh3d0ww01f/WaterDragon/main/img/5.png)
# How to Stop Action
![](https://raw.githubusercontent.com/sh3d0ww01f/WaterDragon/main/img/666en.png)
![](https://raw.githubusercontent.com/sh3d0ww01f/WaterDragon/main/img/777en.png)
then we type "0" to stop the GithubAction which in_progress
if "stop process succcessfully" ,that means stop successfully
