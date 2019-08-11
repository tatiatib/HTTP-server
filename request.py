

class HTTP_request():
	def __init__(self, data):
		data = data.split ("\r\n")
		request_line = data[0].split(" ")
		self.http_version = request_line[2]
		self.document_root = request_line[1][1:]
		self.type = request_line[0]
		self.headers = {}
		data = data[1:-2]
		for line in data:
			line = line.split(":", 1)
			self.headers[line[0].lower()] = line[1][1:] 
		

		
	def type(self):
		return self.type[0]

		
	def host(self):
		return self.headers["host"]

	def keep_alive(self):
		if "connection" in self.headers:
			if self.headers["connection"] == "keep-alive":
				return True
		
		return False

	def get_range(self):
		if "range" in self.headers:
			return self.headers["range"]

	