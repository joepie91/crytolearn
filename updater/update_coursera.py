import requests
import oursql
import datetime
import json
import lib

class CourseraCrawler(object):
	def __init__(self):
		self.db = lib.Database("localhost", "root")
		
	def retrieve_dataset(self):
		#self.dataset = requests.get("https://www.coursera.org/maestro/api/topic/list?full=1").json()
		self.dataset = json.loads(open("coursera.json", "r").read())

	def parse_dataset(self):
		for item in self.dataset:
			self.process_item(item)
		
	def process_item(self, item):
		inserted, rowid = self.db.insert_topic(2, str(item["id"]), item["name"], description=item["short_description"], needs_enrollment=True)
		
		if inserted:
			print "Inserted %s" % item["name"]
		else:
			print "Skipped %s" % item["name"]
		
		for course in item["courses"]:
			self.process_course(course, rowid)
	
	def process_course(self, course, topicid):
		try:
			start_date = datetime.datetime(course["start_year"], course["start_month"], course["start_day"])
			title = "%s: %s-%s-%s" % (course["name"], str(course["start_year"]).zfill(4), str(course["start_month"]).zfill(2), str(course["start_day"]).zfill(2))
		except TypeError, e:
			start_date = None
			title = "%s (date undetermined)" % (course["name"])
		
		inserted, itemid = self.db.insert_item(2, str(course["id"]), True, self.db.COURSE, title, course["home_link"], description=course["certificate_description"], start_date=start_date, topic_id=topicid)
		
		if inserted:
			print "\tInserted %s" % title
		else:
			print "\tSkipped %s" % title
			
crawler = CourseraCrawler()
crawler.retrieve_dataset()
crawler.parse_dataset()
