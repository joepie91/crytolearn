import requests
import oursql
import datetime
import json
import sys, os
import shared

from bs4 import BeautifulSoup
import bs4
	
rsess = requests.Session()
rsess.headers['User-Agent'] = 'http://learn.cryto.net/ (scraper@cryto.net) - We mean no harm, thanks for making knowledge free :)'

class OpenCourseWare(shared.Scraper):
	def run(self):
		overview = rsess.get("http://www.ocwconsortium.org/en/courses/browsesource").text
		soup = BeautifulSoup(overview)
		
		for element in soup.find(id="pagecontent")("a"):
			#if "Hopkins" not in element.string:
			#	continue
			self.process_source(int(element["href"].split("/")[-1]), element.string)
		
	def process_source(self, source_id, source_name):
		data = rsess.get("http://www.ocwconsortium.org/en/courses/browsesource/browse/source/%d" % source_id).text
		soup = BeautifulSoup(data)
		
		courses = soup.select("table#cfResultsTable tr")
		
		for course in courses[:3]:
			links = course("a")
			
			if len(links) > 0:
				external = links[0]
				details = links[1]
				
				self.parse_course(external.string, external["href"], details["href"].split("/")[-1], source_name)
				
	def parse_course(self, course_name, course_url, course_id, source_name):
		self.env.log("Parsing %s" % course_url)
		
		# First fetch metadata from ocwconsortium.org
		ocw_data = self._metadata_ocw(course_id)
		ocw_data["providername"] = source_name
		ocw_data["url"] = course_url
		
		# Now fetch metadata from the particular course provider
		provider_data = self._metadata_provider(course_url)
		
		if provider_data != False:
			data = ocw_data.copy()
			data.update(provider_data)
			
			# TODO: insert data
			self.env.log(repr(data))
	
	def _metadata_ocw(self, course_id):
		soup = BeautifulSoup(rsess.get("http://www.ocwconsortium.org/en/courses/browsesource/course/%s" % course_id).text)
		metadata = soup.select("dl.coursepage")[0]
		
		if len(metadata) > 0:
			data = self._parse_ocw_dl(metadata.select("dd"), metadata.select("dt"))
		else:
			# No metadata provided by ocwconsortium.
			data = {}
			
		return data
	
	def _parse_ocw_dl(self, dd, dt):
		data = {}
		
		for i in xrange(0, len(dd)):
			label = dd[i].string.strip().rstrip(":")
			value = dt[i].string
			
			if value is not None:
				value = value.strip()
			
			if label == "Tags":
				if value == None:
					data["tags"] = []
				else:
					data["tags"] = [x.strip() for x in value.split(",")]
			elif label == "Source":
				data["providername"] = value
			elif label == "Language":
				data["language"] = value
			elif label == "Link":
				# We can ignore this, we already have it anyway
				pass
			elif label == "Author":
				if value == None:
					data["author"] = None
				else:
					data["author"] = value
			elif label == "License":
				if value == None:
					data["license"] = None
				else:
					data["license"] = value
			elif label == "Date Published":
				data["creation_date"] = datetime.datetime.strptime(value, "%b %d, %Y")
			else:
				self.env.log("UNKNOWN: %s => %s" % (label, value), True)
				
		return data
		
	def _metadata_provider(self, url):
		providers = {
			"oer.avu.org": self._metadata_avu,
			"ocw.capilanou.ca": self._metadata_capilano,
			"ocw.hokudai.ac.jp": self._metadata_hokkaido,
			"ocw.ie.edu": self._metadata_ie,
			"ocw.jhsph.edu": self._metadata_hopkins,
		}

		host = url.split("/")[2]
		data = {}
		
		for provider, func in providers.iteritems():
			if host.endswith(provider):
				return func(url)
				
		return False
	
	def _metadata_avu(self, url):
		# African Virtual University
		soup = BeautifulSoup(rsess.get(url + "?show=full").text)
		table = soup.select("table.ds-includeSet-table")[0]
		data = {"providername": "African Virtual University"}
		
		for row in table("tr"):
			cells = row("td")
			label = cells[0].string
			value = cells[1].string
			
			if label == "dc.identifier.uri":
				data["identifier_uri"] = value
			elif label == "dc.type":
				data["object_type"] = value
			elif label == "dc.date.accessioned":
				data["creation_date"] = datetime.datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")
			elif label == "dc.date.issued":
				data["issued_date"] = datetime.datetime.strptime(value, "%Y-%m-%d")
			elif label == "dc.date.available":
				data["available_date"] = datetime.datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")
			elif label == "dc.language.iso":
				data["language"] = value
			elif label == "dc.description.abstract":
				data["description"] = " ".join(x for y in cells[1]("p") for x in y.strings)
			elif label == "dc.contributor.author":
				data["author"] = value
			elif label == "dc.title":
				data["title"] = value
			else:
				self.env.log("UNKNOWN KEY: %s => %s" % (label, value), True)
			
		return data
	
	def _metadata_capilano(self, url):
		# Capilano University
		soup = BeautifulSoup(rsess.get(url).text)
		data = {"providername": "Capilano University"}
		
		data["title"] = soup.select("h1.documentFirstHeading")[0].string.strip()
		data["description"] = " ".join(x for y in soup.select("#about > p") for x in y.strings).strip()
		
		return data
		
	def _metadata_hokkaido(self, url):
		# Hokkaido University
		soup = BeautifulSoup(rsess.get(url).text)
		data = {"providername": "Hokkaido University"}
		
		data["title"] = soup.select("#MAIN h1")[0].string.strip()
		data["description"] = soup.select("#MAIN p")[0].string.strip()
	
		return data
		
	def _metadata_ie(self, url):
		# IE University
		course_id = url.split("=")[1]
		soup = BeautifulSoup(rsess.get("http://ocw.ie.edu/ocw/cur%s01_esp.html" % course_id.zfill(2)).text)
		data = {"providername": "IE University"}
		
		data["title"] = soup.select(".ari_18_negrita")[0].string.strip()
		data["description"] = " ".join(x.strip() for x in soup.select(".ari_12_negra")[-1].strings)
		data["author"] = soup.select(".ari_12_negra")[2].select(".ari_12_negrita")[0].string.strip()
	
		return data
		
	def _metadata_hopkins(self, url):
		# Johns Hopkins Bloomberg School of Public Health
		soup = BeautifulSoup(rsess.get(url).text)
		data = {"providername": "Johns Hopkins Bloomberg School of Public Health"}
		
		data["title"] = self.soup_to_text(soup.select("h1")[-1])
		data["author"] = self.soup_to_text(soup.select("#courseInfoBox p:nth-of-type(1)"))
		data["description"] = self.soup_to_text(soup.select("#courseImageAndInfoBox > p"))
		
		return data
