import json
from datetime import datetime

class ActiveServer():
  def __init__(self) -> None:
    self.server_name = ""
    self.host = ""
    self.machine_address = ""
    self.player_count = 0
    self.player_limit = 0
    self.server_port = 0
    self.server_motd_preview = ""
    self.server_motd_content = ""
    self.custom_password = False
    self.ttl = 0
    self.authorization = ""

  # True if accepted,
  # False if they're trying to pull a fast one on us
  def fromJson(self, _json):
    data = json.loads(_json)
    if "PlayerCount" not in data or type(data["PlayerCount"]) is not int:
      print("bad playercount")
      return False
    if "PlayerLimit" not in data or type(data["PlayerLimit"]) is not int:
      print("bad playerlimit")
      return False 
    if "CustomPassword" not in data or type(data["CustomPassword"]) is not bool:
      print("missing custompassword")
      return False 
    if "ServerPort" not in data or type(data["ServerPort"]) is not int:
      print("missing serverport")
      return False 
    if "Authorization" not in data:
      print("missing authorization")
      return False 
    if "MotdContent" not in data:
      print("missing motdcontent")
      return False
    if "MotdPreview" not in data:
      print("missing motdpreview")
      return False 
    if "ServerName" not in data:
      print("missing servername")
      return False 
    print(_json)
    if "Host" not in data:
      print("missing host")
      return False
  
    self.server_name = data["ServerName"]
    self.server_motd_content = data["MotdContent"]
    self.server_motd_preview = data["MotdPreview"]
    self.player_count = data["PlayerCount"]
    self.player_limit = data["PlayerLimit"]
    self.authorization = data["Authorization"]
    self.custom_password = data["CustomPassword"]
    self.ttl = datetime.now().timestamp() + 120
    self.host = data["Host"]
    self.server_port = data["ServerPort"]
    return True
  
  def toJson(self) -> str:
    obj = {
      "ServerName": self.server_name,
      "MotdContent": self.server_motd_content,
      "MotdPreview": self.server_motd_preview,
      "PlayerCount": self.player_count,
      "PlayerLimit": self.player_limit,
      "CustomPassword": self.custom_password,
      "MachineAddress": self.machine_address,
      "ServerPort": self.server_port,
      "Host": self.host,
      "GUID": "x"
    }
    return json.dumps(obj)