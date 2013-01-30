import oursql

class Environment(object):
	def connect(self, host="localhost", username="root", password="", database="learn"):
		self.db = oursql.connect(host=host, user=username, passwd=password, db=database)
		self.connected = True
		
	def log(self, text):
		print text
		
	def Scraper(self, scraper_class):
		s = scraper_class(self.db)
		s.env = self
		return s
