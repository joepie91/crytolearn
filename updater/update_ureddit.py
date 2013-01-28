import requests
import oursql
import datetime
import json, simplejson
import lib
import re

class UredditCrawler(object):
	def __init__(self):
		self.db = lib.Database("localhost", "root")
	
	def parse_catalog(self):
		data = requests.get("http://ureddit.com/api?type=catalog").json()
		
		for category in data["categories"]:
			self.parse_category(category['id'], category['value'])
	
	def parse_category(self, category_id, category_name):
		try:
			data = requests.get("http://ureddit.com/api?type=category&id=%s" % category_id).json()
		except simplejson.decoder.JSONDecodeError, e:
			return
		
		for _class in data["classes"]:
			if not self.db.topic_exists(3, _class['id']):
				self.parse_class(_class['id'], _class['value'], category_name)
			else:
				print "Skipped class %s" % _class['value']
	
	def parse_class(self, class_id, class_name, category_name):
		try:
			data = requests.get("http://ureddit.com/api?type=class&id=%s" % class_id).json()
		except simplejson.decoder.JSONDecodeError, e:
			print "Skipped %s due to JSON formatting error" % class_name
			return
		
		try:
			creation_date = datetime.datetime.strptime(data["created"], '%Y-%m-%d %H:%M:%S')
		except ValueError, e:
			creation_date = None
		
		# Hack to get the class page as this isn't returned by the API
		html_data = requests.get("http://ureddit.com/show_class.php?id=%s&show=true" % class_id).text
		matches = re.search('<a href="([^"]+)"><button class="button">class page<\/button><\/a>', html_data)
		
		if matches is not None:
			class_page = "http://ureddit.com%s" % matches.group(1)
		else:
			class_page = None
		
		inserted, topic_id = self.db.insert_topic(3, str(class_id), data["name"], needs_enrollment=True, description=data["description"], creation_date=creation_date)
		
		if inserted:
			print "Inserted %s" % data["name"]
		else:
			print "Skipped %s" % data["name"]
		
		inserted, item_id = self.db.insert_item(3, str(class_id), True, self.db.COURSE, data["name"], class_page, topic_id=topic_id, date=creation_date, description=data["description"])
		
		if inserted:
			print "\tInserted %s" % data["name"]
		else:
			print "\tSkipped %s" % data["name"]
	
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
			
crawler = UredditCrawler()
crawler.parse_catalog()
