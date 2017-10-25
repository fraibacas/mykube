#!/usr/bin/env python
 
from http.server import BaseHTTPRequestHandler, HTTPServer
import os

# HTTPRequestHandler class
class testHTTPServer_RequestHandler(BaseHTTPRequestHandler):
 
  # GET
  def do_GET(self):
        # Send response status code
        self.send_response(200)
 
        # Send headers
        self.send_header('Content-type','text/html')
        self.end_headers()
 
        # Send message back to client
        message = "HELLO FROM <h1>{}</h1> MICROSERVICE!".format(os.environ.get("MICROSERVICE", "UNKNOWN"))
        # Write content as utf-8 data
        self.wfile.write(bytes(message, "utf8"))
        return
 
def run():
  server_address = ('0.0.0.0', 80)
  httpd = HTTPServer(server_address, testHTTPServer_RequestHandler)
  print('running server...')
  httpd.serve_forever()

run()