from http.server import HTTPServer, BaseHTTPRequestHandler
from data import ActiveServer
from datetime import datetime
from io import BytesIO

import signal
import json
import sys
import gzip
# leave keys empty to allow everyone to use that feature
# good practice to set announce key to something

PING_KEY = ""        # no announce permissions but can ping
ANNOUNCE_KEY = "" # has ping permissions

active_servers = {}

class Serve(BaseHTTPRequestHandler):
  def do_GET(self):
    if self.path == '/flags':
      self.send_response(200)
      self.end_headers()
      with open('flags.json') as f:
        self.wfile.write(bytes(json.dumps(json.load(f)), "utf-8"))

      return
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
      obj = { "ActiveServers": [], "MasterMotd": "This is the official Aya Governor instance.", "SpecialMotd": "", "Authentication": { "CanHostServers": canHostServers, "CanReadMasterServer": canSeeServers } }
      if canSeeServers:
        for server in list(active_servers.keys()): 
          _obj = active_servers[server]
          if _obj.ttl < datetime.now().timestamp():
            del active_servers[server]
          else:
            t = json.loads(_obj.toJson())
            obj["ActiveServers"].append(t)
      self.send_response(200)
      self.end_headers()
      self.wfile.write(bytes(json.dumps(obj), "utf-8"))

      return
    elif self.path == '/':
      self.send_response(200)
      self.end_headers()
      self.wfile.write(bytes(json.dumps({ "Response": "ok" }), "utf-8"))

      return
    else:
      self.send_response(404)
      self.end_headers()

      return

  def do_POST(self):
    if self.path == '/announce':
      content_length = int(self.headers['Content-Length'])
      content_encoding = self.headers.get('Content-Encoding', '')
      
      data = self.rfile.read(content_length)
      
      if content_encoding == 'gzip':
        try:
          data = gzip.decompress(data)
        except Exception as e:
          self.send_response(400, "Bad Request - Failed to decompress gzip")
          self.end_headers()
          self.wfile.write(bytes("Failed to decompress gzip data", "utf-8"))
          return

      print(data);

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

      return
    else:
      self.send_response(400, "Bad Request")
      self.end_headers()
      return

def signal_handler(sig, frame):
  print("\ngracefully shutting down the server...")
  sys.exit(0)

if __name__ == "__main__":
  signal.signal(signal.SIGINT, signal_handler)
  print("starting master server on port", 7767)
  httpd = HTTPServer(('localhost', 7767), Serve)
  httpd.serve_forever()