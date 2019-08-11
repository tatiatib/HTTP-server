import json
import threading
import sys
import signal
from http_server import *

file = sys.argv[1]

running_servers = []
def signal_handler(code, frame):
	print("Server is shutting down")
	for s in running_servers:
		s.shut_down()
  
	sys.exit()

def main():
	threads = []
	servers = {}

	try:
		with open(file) as data_file:    
			data = data_file.read()
			data = json.loads(data)
	except FileNotFoundError:
		print ("File not found")
	
	configs = data["server"]

	for server in configs:
		ip_port = (server["ip"], server["port"])
		if ip_port in servers:
			servers[ip_port].append((server["vhost"], server["documentroot"]))
		else:
			servers[ip_port] = [(server["vhost"], server["documentroot"])]

	signal.signal(signal.SIGINT, signal_handler)
	# print('Press Ctrl+C')

	for ip_port in servers:
		server = HTTP_Server(ip_port, servers[ip_port])
		running_servers.append(server)
		threading.Thread(target = server.run).start()


if __name__ == '__main__':
	main()