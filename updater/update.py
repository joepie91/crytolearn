import requests
import oursql
import datetime
import json

database = oursql.connect(host="localhost", user="root", db="learn")

def unicodedammit(input_string):
	if isinstance(input_string, str):
		return input_string.decode('utf-8')
	else:
		return input_string

class KhanUniversityCrawler(object):
	TOPIC = 1
	COURSE = 2
	VIDEO = 3
	ARTICLE = 4
	EXERCISE = 5
	QUIZ = 6
	TEST = 7
	BOOK = 8
	
	def __init__(self):
		pass
		
	def retrieve_dataset(self):
		#self.dataset = requests.get("http://www.khanacademy.org/api/v1/topictree").json()
		self.dataset = json.loads(open("data.json", "r").read())

	def parse_dataset(self):
		self.process_item(self.dataset, 0)
		
	def process_item(self, item, level, parent=None):
		global database
		
		c = database.cursor()
		
		try:
			kind = item["kind"]
		except KeyError, e:
			return
		
		if kind == "Topic":
			unique_id = item["id"]
			
			try:
				parent_id = parent["_cl_id"]
			except TypeError, e:
				parent_id = 0
				
			if item["description"] is not None:
				description = item["description"]
			else:
				description = ""
				
			if item["title"] is not None:
				title = item["title"]
			else:
				title = ""
			
			c.execute("SELECT `Id` FROM topics WHERE `ProviderId` = ? LIMIT 1", (unique_id,))
			results = c.fetchall()
			exists = (len(results) > 0)
			
			if not exists:
				c.execute("INSERT INTO topics (`ParentId`, `Provider`, `ProviderId`, `Title`, `Description`, `Created`, `NeedsEnrollment`)"
					  "VALUES (?, 1, ?, ?, ?, ?, 0)", (parent_id, unique_id, title, description, datetime.datetime.now()))
				
				print "Inserted topic %s" % title
				
				item["_cl_id"] = c.lastrowid
			else:
				print u"Skipped topic %s" % title
				item["_cl_id"] = results[0][0]
		elif kind in ("Video", "Exercise", "Article"):
			try:
				unique_id = item["readable_id"]
			except KeyError, e:
				try:
					unique_id = item["name"]
				except KeyError, e:
					try:
						unique_id = str(item["id"])
					except KeyError, e:
						print repr(item)
						sys.stderr.write("WARNING: No suitable identifier found for item\n")
						raise
						return
					
			if item["kind"] == "Video":
				itemtype = self.VIDEO
			elif item["kind"] == "Exercise":
				itemtype = self.EXERCISE
			elif item["kind"] == "Article":
				itemtype = self.ARTICLE
				
			try:
				source_url = item["ka_url"]
			except KeyError, e:
				if itemtype == self.ARTICLE:
					source_url = ""
				else:
					return
				
			try:
				item_url = item["url"]
			except KeyError, e:
				item_url = source_url
				
			if itemtype == self.ARTICLE:
				description = item["content"]
			else:
				try:
					description = item["description"]
				except KeyError, e:
					description = ""
					
			if description is None:
				description = ""
			
			try:
				title = item["title"]
			except KeyError, e:
				try:
					title = item["display_name"]
				except KeyError, e:
					title = "Untitled"
				
			try:
				views = item["views"]
			except KeyError, e:
				views = 0
			
			c.execute("SELECT `Id` FROM items WHERE `ProviderId` = ? LIMIT 1", (unique_id,))
			results = c.fetchall()
			exists = (len(results) > 0)
			
			if not exists:
				try:
					c.execute("INSERT INTO items (`HasTopic`, `Type`, `Provider`, `ProviderId`, `Title`, `Description`, `ItemUrl`, `SourceUrl`, `Views`, `TopicId`, `ParentId`)"
						  "VALUES (1, ?, 1, ?, ?, ?, ?, ?, ?, ?, 0)", (itemtype, unique_id, title, description, item_url, source_url, views, parent["_cl_id"]))
				except oursql.ProgrammingError, e:
					print repr((itemtype, unique_id, title, description, item_url, source_url, views, parent["_cl_id"]))
					print repr(description)
					raise
				
				print "Inserted item %s" % title
				
				item["_cl_id"] = c.lastrowid
			else:
				print "Skipped item %s" % title
				item["_cl_id"] = results[0][0]
		elif kind == "Separator":
			pass  # Ignore separators
		else:
			print "Unrecognized kind: %s" % item["kind"]
			print repr(item)
			date = datetime.datetime.strptime("2008-08-12T12:20:30Z", "%Y-%m-%dT%H:%M:%SZ")
		
		try:
			children = item["children"]
		except KeyError, e:
			pass
		else:
			for child in children:
				self.process_item(child, level + 1, item)
			
crawler = KhanUniversityCrawler()
crawler.retrieve_dataset()
crawler.parse_dataset()
