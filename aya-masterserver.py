from http.server import HTTPServer, BaseHTTPRequestHandler
from data import ActiveServer
from datetime import datetime
import json

# leave keys empty to allow everyone to use that feature
# good practice to set announce key to something

PING_KEY = ""        # no announce permissions but can ping
ANNOUNCE_KEY = "" # has ping permissions

active_servers = {}

class Serve(BaseHTTPRequestHandler):
  def do_GET(self):
    if self.path == '/ping':
      canSeeServers = True
      canHostServers = True

      if "Authorization" not in self.headers:
        if PING_KEY != "":
          canSeeServers = False
        if ANNOUNCE_KEY != "":
          canHostServers = False
      else:
        print(PING_KEY, self.headers["Authorization"])
        if PING_KEY != self.headers["Authorization"]:
          canSeeServers = False
        if ANNOUNCE_KEY != self.headers["Authorization"]:
          canHostServers = False
      obj = { "ActiveServers": [], "MasterMotd": "", "SpecialMotd": "", "Authentication": { "CanHostServers": canHostServers, "CanReadMasterServer": canSeeServers } }
      if canSeeServers:
        for server in active_servers: 
          _obj = active_servers[server]
          if _obj.ttl < datetime.now().timestamp():
            active_servers.pop(server, None)
          else:
            t = json.loads(_obj.toJson())
            obj["ActiveServers"].append(t)
      print(json.dumps(obj))
      self.send_response(200)
      self.end_headers()
      self.wfile.write(bytes(json.dumps(obj), "utf-8"))
    elif self.path == '/':
      self.send_response(200)
      self.end_headers()
      self.wfile.write(bytes("Hi", "utf-8"))
    else:
      self.send_response(404)
      self.end_headers()

  def do_POST(self):
    if self.path == '/announce':
      content_length = int(self.headers['Content-Length'])
      data = self.rfile.read(content_length)
      
      aserv = ActiveServer()
      ok = aserv.fromJson(data)
      if ok:
        if aserv.authorization != ANNOUNCE_KEY:
          pass
        
        aserv.machine_address = self.client_address[0]
        active_servers[self.client_address[0]] = aserv

        self.send_response(200)
        self.end_headers()
      else:
        self.send_response(403, "Server suppressed")
        self.end_headers()

      self.wfile.write(bytes("OK", "utf-8"))
    else:
      self.send_response(404, "Bad post.. You Suck")
      self.end_headers()


if __name__ == "__main__":
  print("Starting master server on port ", 7767)
  httpd = HTTPServer(('localhost', 7767), Serve)
  httpd.serve_forever()