import socket
import threading 
from request import *
from response import *

keep_running = True
BACKLOG = 1024
DATA_SIZE = 1024
ALIVE_TIME = 5

class HTTP_Server():
	def __init__(self, ip_port, vhost):
		self.ip = ip_port[0]
		self.port = ip_port[1]
		self.vhosts = {pair[0]:pair[1] for pair in vhost}
		self.cur_connections = []
		server_address = (self.ip, self.port)
		self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.server.bind(server_address)

	def run(self):
		self.server.listen(BACKLOG)
		while keep_running:
			connection, addr = self.server.accept()	
			threading.Thread(target=self.client_connection, args=(connection,addr, )).start()
		

	def client_connection(self, connection, address):
		try:
			data = connection.recv(DATA_SIZE)
		except (ConnectionError):	
			connection.close()
		if data:
			request = HTTP_request(data.decode())
			self.send_response(request, connection)
		
			while(request.keep_alive()):
				connection.settimeout(ALIVE_TIME)
				try:
					data = connection.recv(DATA_SIZE)
				except socket.timeout:
					break
				except (ConnectionError):
					break
				connection.settimeout(None)	

				if not data:
					break
				request = HTTP_request(data.decode())
				self.send_response(request, connection)

		connection.close()


	def send_response(self, request, connection):
		resp = HTTP_response(request)
		if not  (request.type == "GET" or request.type == "HEAD"):
			resp.add_status(501, "Not Implemented")
			connection.send(resp.head_text())
			return
		if not request.host().split(":")[0] in self.vhosts :
			connection.send(resp.not_found_resp("requested domain not found"))
		else:
			
			directory = self.vhosts[request.host().split(":")[0]]
			resp.send_document(directory, connection) 
	

				
	def shut_down(self):
		global keep_running

		keep_running = False
		self.server.close()


