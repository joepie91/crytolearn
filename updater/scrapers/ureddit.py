import datetime, json, simplejson, sys, re
import requests
import shared

class UniversityOfReddit(shared.Scraper):
	provider_id = 3
	
	def run(self):
		data = requests.get("http://ureddit.com/api?type=catalog").json()
		
		for category in data["categories"]:
			self.parse_category(category['id'], category['value'])
	
	def parse_category(self, category_id, category_name):
		try:
			data = requests.get("http://ureddit.com/api?type=category&id=%s" % category_id).json()
		except simplejson.decoder.JSONDecodeError, e:
			return
		
		for _class in data["classes"]:
			if not self.topic_exists(_class['id']):
				self.parse_class(_class['id'], _class['value'], category_name)
			else:
				self.env.log("Skipped class %s" % _class['value'])
	
	def parse_class(self, class_id, class_name, category_name):
		try:
			data = requests.get("http://ureddit.com/api?type=class&id=%s" % class_id).json()
		except simplejson.decoder.JSONDecodeError, e:
			self.env.log("Skipped %s due to JSON formatting error" % class_name, True)
			return
		
		if data["status"] == '1' or data["status"] == '3' or data["status"] == '5':
			try:
				creation_date = datetime.datetime.strptime(data["created"], '%Y-%m-%d %H:%M:%S')
			except ValueError, e:
				creation_date = None
			
			class_page = data["url"]
			
			inserted, topic_id = self.insert_topic(str(class_id), data["name"], needs_enrollment=True, description=data["description"], creation_date=creation_date)
			
			if inserted:
				self.env.log("Inserted topic %s" % data["name"])
			else:
				self.env.log("Skipped topic %s" % data["name"])
			
			inserted, item_id = self.insert_item(str(class_id), data["name"], class_page, itemtype=self.COURSE, has_topic=True, topic_id=topic_id, date=creation_date, description=data["description"])
			
			if inserted:
				self.env.log("Inserted item %s" % data["name"])
			else:
				self.env.log("Skipped item %s" % data["name"])
		else:
			self.env.log("Skipped %s due to status (%s)" % (data["name"], data["status_description"]))
