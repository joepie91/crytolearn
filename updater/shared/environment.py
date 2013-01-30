import oursql, sys

class Environment(object):
	def connect(self, host="localhost", username="root", password="", database="learn"):
		self.db = oursql.connect(host=host, user=username, passwd=password, db=database)
		self.connected = True
		
	def log(self, text, is_error=False):
		if is_error == False:
			sys.stdout.write(text + "\n")
		else:
			sys.stderr.write(text + "\n")
		
	def Scraper(self, scraper_class):
		s = scraper_class(self.db)
		s.env = self
		return s
