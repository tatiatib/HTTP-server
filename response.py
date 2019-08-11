import datetime
import os
import mimetypes
import request
import magic

from urllib.parse import quote
from urllib.parse import unquote

ETAG = "11111"

class HTTP_response():
	def __init__(self, request):
		self. headers = b''
		self.body = b''
		self.request = request

	def add_status(self, status_code, reason_phrase):
		self.headers = bytes("{} {} {}\r\n".format(self.request.http_version, status_code, reason_phrase), "utf-8")

	def get_text(self):

		return self.headers + bytes(("\r\n"), "utf-8") + self.body + bytes(("\r\n"), "utf-8")

	def head_text(self):
		return self.headers + bytes(("\r\n"), "utf-8") 

	def add_header(self, header_field, value):
		self.headers += bytes("{}:{}\r\n".format(header_field, value), "utf-8")

	
	def send_document(self, directory, connection):
		file_name= self.request.document_root
		path = unquote(directory + "/" + file_name)
		if not file_name:
			self.body = generate_file_list(path)
			self.head = self.set_headers(path, len(self.body))
			if self.request.type == "HEAD":
				connection.send(self.head_text())

			else:
				connection.send(self.get_text())
			return
		
		if not os.path.exists(path) or os.path.isdir(path) :
			connection.send(self.not_found_resp("File not Found"))
		else:	
			if self.request.type == "HEAD":
				size = os.stat(path).st_size
				self.set_headers(path,size)
				connection.send(self.head_text())
				return

			if self.request.get_range():
				self.send_range_file(path, connection)
				return
			try:
				with open(path, "rb") as file :
					self.body = file.read()
				
				self.set_headers(path, len(self.body))
				connection.send(self.get_text())
			
			except IOError :
				print ("Could not read file")
				return
	

	def send_range_file(self, path, connection):
		file_range = self.request.get_range()
		start = int(file_range[file_range.index("=") + 1: file_range.index("-")])
		end = file_range[file_range.index("-")+1:]
		size = os.stat(path).st_size
		if start > size or (end != '' and int(end) > size):
			print("jer")
			self.add_status(416, "Requested Range Not Satisfiable")
			connection.send(self.head_text())
			return
		if not end:
			with open(path, "rb") as file:
				file.seek(start,1)
				self.body = file.read()
		else:
			end = int(end)
			with open(path, "rb") as file:
				file.seek(start,1)
				self.body += file.read(end - start +1)


		self.set_headers(path, len(self.body))
		connection.send(self.get_text())			
		

	def not_found_resp(self, resp_text):
		self.add_status(404, "Not Found")
		self.add_header("content-type", "text/html")
		self.add_header("Connection", "close")
		self.add_header("Server", "Tatia")
		self.body = bytes((resp_text), "utf-8")
		self.add_header("Content-length", len(self.body))
		self.add_header("ETAG",ETAG) #this should be  impelented 
		self.add_header("Date", datetime.datetime.now())
		return self.get_text()

	
	def set_headers(self, path, size):
		self.add_status(200, "OK")
		self.add_header("ETAG",ETAG)  
		if self.request.keep_alive():
			self.add_header("Connection", "keep-alive")
		else:
			self.add_header("Connection", "close")	
		self.add_header("Content-Type", magic.from_buffer(self.body, mime=True))
		self.add_header("Server", "Tatia")
		self.add_header("Content-length", size)
		self.add_header("Date", datetime.datetime.now())
		self.add_header("Keep-Alive", "timeout=5, max=1000")
		self.add_header("Accept-Ranges", "bytes")


def generate_file_list(directory):
	body = '<!DOCTYPE html>\n' \
			'<html>\n' \
			'<head>\n' \
			'<meta charset="UTF-8">\n' \
			'<title> Hello </title>\n' \
			'</head>\n' \
			'<body>\n' \

	for file in os.listdir(directory):
		body += '<li><a href={}>{}</a></li>\n'.format(quote(os.path.join(file)), file)

	body += '</body>\n'\
			'</html>'

	return bytes(body, "utf-8")


