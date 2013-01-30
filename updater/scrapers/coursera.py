import datetime, json, sys
import requests
import shared

class Coursera(shared.Scraper):
	provider_id = 2
	
	def run(self):
		self.retrieve_dataset()
		self.parse_dataset()
	
	def retrieve_dataset(self):
		self.dataset = requests.get("https://www.coursera.org/maestro/api/topic/list?full=1").json()

	def parse_dataset(self):
		for item in self.dataset:
			self.process_item(item)
		
	def process_item(self, item):
		inserted, row_id = self.insert_topic(str(item["id"]), item["name"], description=item["short_description"], needs_enrollment=True)
		
		if inserted:
			self.env.log("Inserted topic %s" % item["name"])
		else:
			self.env.log("Skipped topic %s" % item["name"])
		
		for course in item["courses"]:
			self.process_course(course, row_id)
	
	def process_course(self, course, topicid):
		try:
			start_date = datetime.datetime(course["start_year"], course["start_month"], course["start_day"])
		except TypeError, e:
			start_date = None
			
		title = self.generate_title(course['name'], start_date)
		
		inserted, row_id = self.insert_item(str(course["id"]), title, course["home_link"], has_topic=True, itemtype=self.COURSE, description=course["certificate_description"], start_date=start_date, topic_id=topicid)
		
		if inserted:
			self.env.log("Inserted item %s" % title)
		else:
			self.env.log("Skipped item %s" % title)
			
	def generate_title(self, name, date):
		if date is None:
			return "%s (date undetermined)" % name
		else:
			return "%s (starting %s)" % (name, date.strftime("%b %d, %Y"))
			
