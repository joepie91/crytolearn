import requests
import oursql
import datetime
import json
import lib

class KhanUniversityCrawler(object):
	def __init__(self):
		self.db = lib.Database("localhost", "root")
		
	def retrieve_dataset(self):
		self.dataset = requests.get("http://www.khanacademy.org/api/v1/topictree").json()
		#self.dataset = json.loads(open("data.json", "r").read())

	def parse_dataset(self):
		self.process_item(self.dataset, 0)
		
	def process_item(self, item, level, parent=None):
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
				
			if item["title"] is not None:
				title = item["title"]
			else:
				title = ""
			
			inserted, rowid = self.db.insert_topic(1, unique_id, title, description=item["description"], needs_enrollment=False)
			item["_cl_id"] = rowid
			
			if inserted:
				print "Inserted %s" % title
			else:
				print "Skipped %s" % title
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
				itemtype = self.db.VIDEO
			elif item["kind"] == "Exercise":
				itemtype = self.db.EXERCISE
			elif item["kind"] == "Article":
				itemtype = self.db.ARTICLE
				
			try:
				source_url = item["ka_url"]
			except KeyError, e:
				if itemtype == self.db.ARTICLE:
					source_url = ""
				else:
					return
				
			try:
				item_url = item["url"]
			except KeyError, e:
				try:
					item_url = item["ka_url"]
				except KeyError, e:
					item_url = None
				
			if itemtype == self.db.ARTICLE:
				description = item["content"]
			else:
				try:
					description = item["description"]
				except KeyError, e:
					description = None
			
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
				views = None
				
			try:
				date = datetime.datetime.strptime(item["date_added"], "%Y-%m-%dT%H:%M:%SZ")
			except KeyError, e:
				date = None
			
			inserted, rowid = self.db.insert_item(1, unique_id, True, itemtype, title, item_url, source_url=source_url, description=description, views=views, topic_id=parent["_cl_id"], date=date)
			item["_cl_id"] = rowid
			
			if inserted:
				print "Inserted %s" % title
			else:
				print "Skipped %s" % title
		elif kind == "Separator":
			pass  # Ignore separators
		else:
			sys.stderr.write("Unrecognized kind: %s\n" % item["kind"])
			sys.stderr.write("%s\n" % (repr(item)))
		
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
