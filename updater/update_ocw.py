import requests
import oursql
import datetime
import json
import lib
from bs4 import BeautifulSoup
import bs4

def combine_dict(a, b):
	c = a.copy()
	c.update(b)
	return c
	
rsess = requests.Session()
rsess.headers['User-Agent'] = 'http://learn.cryto.net/ (scraper@cryto.net) - We mean no harm, thanks for making knowledge free :)'

class OpenCourseWareCrawler(object):
	def __init__(self):
		self.db = lib.Database("localhost", "root", password="")
	
	def parse_catalog(self):
		overview = rsess.get("http://www.ocwconsortium.org/en/courses/browsesource").text
		soup = BeautifulSoup(overview)
		
		for element in soup.find(id="pagecontent")("a"):
			self.parse_source(int(element["href"].split("/")[-1]), element.string)
		
	def parse_source(self, source_id, source_name):
		data = rsess.get("http://www.ocwconsortium.org/en/courses/browsesource/browse/source/%d" % source_id).text
		soup = BeautifulSoup(data)
		
		courses = soup.select("table#cfResultsTable tr")
		
		print "# " + source_name
		
		for course in courses[:2]:
			links = course("a")
			
			if len(links) > 0:
				external = links[0]
				details = links[1]
				
				self.parse_course(external.string, external["href"], details["href"].split("/")[-1])
				
	def parse_course(self, course_name, course_url, course_id):
		# First fetch metadata from ocwconsortium.org
		
		print course_url
		
		metadata_soup = BeautifulSoup(rsess.get("http://www.ocwconsortium.org/en/courses/browsesource/course/%s" % course_id).text)
		
		metadata = metadata_soup.select("dl.coursepage")[0]
		
		if len(metadata) > 0:
			data = self.parse_dl(metadata.select("dd"), metadata.select("dt"))
		else:
			# No metadata provided by ocwconsortium.
			data = {}
		
		# Now fetch metadata from the particular course provider
		provider_data = self.get_provider_data(course_url)
		
		if provider_data != {}:
			print repr(provider_data)
			
	def parse_dl(self, dd, dt):
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
				data["source"] = value
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
				print "UNKNOWN: %s => %s" % (label, value)
				
		return data
		
	def get_provider_data(self, url):
		providers = {
			"oer.avu.org": self._data_avu,
			"ocw.capilanou.ca": self._data_capilano,
			"ocw.hokudai.ac.jp": self._data_hokkaido,
			"ocw.ie.edu": self._data_ie,
			"ocw.jhsph.edu": self._data_hopkins,
		}

		""",
			
			
			
			"ocw.kaplan.edu": self._data_kaplan,
			"ocw.korea.edu": self._data_korea,
			"kyotomm.jp": self._data_kyoto,
			"ocw.kyushu-u.ac.jp": self._data_kyushu,
			
			"open-marhi.ru": self._data_moscow,
			"yctrtrc.ncku.edu.tw": self._data_chengkung,
			"ocw.nctu.edu.tw": self._data_chiaotung,
			"opencourse.ndhu.edu.tw": self._data_donghwa,
			"ocw.njit.edu": self._data_njit,
			"graduateschool.paristech.fr": self._data_paris,
			"peoples-uni.org": self._data_oaei,
			"ocw.sbu.ac.ir": self._data_shahid,
			"studentscircle.net": self._data_studentscircle,
			"ocw.tmu.edu.tw:8080": self._data_taipei,
			"openlearn.open.ac.uk": self._data_openuni,
			"www.ocw.titech.ac.jp": self._data_tokyo,
			"feedproxy.google.com": self._data_tudelft,
			"ocw.tufts.edu": self._data_tufts,
			"ocw.unu.edu": self._data_un,
			"ocw.uc3m.es": self._data_madrid,
			"ocw.ua.es": self._data_alicante,
			"ocw.unican.es": self._data_cantabria,
			"ocw.ugr.es": self._data_granada,
			"ocw.udem.edu.mx": self._data_monterrey,
			"ocw.um.es": self._data_murcia,
			"ocw.uniovi.es": self._data_oviedo,
			"ocw.usal.es": self._data_salamanca,
			"ocwus.us.es": self._data_sevilla,
			"ocw.unizar.es": self._data_zaragoza,
			"ocw.univalle.edu.co3": self._data_colombia,
			"ocw.uned.ac.cr": self._data_distancia,
			"www.icesi.edu.co": self._data_icesi,
			"ocw.innova.uned.es": self._data_innova,
			"upv.es": self._data_valencia,
			"ocw.upm.es": self._data_upm,
			"ocw.utpl.edu.ec": self._data_utpl,
			"ocw.uab.cat": self._data_uab,
			"ocw.ub.edu": self._data_ub,
			"ocw.uib.es": self._data_uib,
			"ocw.udl.cat": self._data_udl,
			"ocw.uv.es": self._data_uv,
			"e-ujier.uji.e": self._data_uji,
			"ocw.uoc.edu": self._data_uoc,
			"ocw.utm.my": self._data_utm,
			"ocw.uci.edu": self._data_uci,
			"opencontent.uct.ac.za": self._data_uct,
			"ocw.umb.edu:8080": self._data_boston,
			"open.umich.edu": self._data_michigan,
			"ocw.nd.edu": self._data_notredame,
			"ocw.usu.ac.id": self._data_usu,
			"ocw.tsukuba.ac.jp": self._data_tsukaba"""

		host = url.split("/")[2]
		data = {}
		
		for provider, func in providers.iteritems():
			if host.endswith(provider):
				data = func(url)
				
		return data
	
	def _data_avu(self, url):
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
				print "UNKNOWN KEY: %s => %s" % (label, value)
			
		return data
	
	def _data_capilano(self, url):
		# Capilano University
		soup = BeautifulSoup(rsess.get(url).text)
		data = {"providername": "Capilano University"}
		
		data["title"] = soup.select("h1.documentFirstHeading")[0].string.strip()
		data["description"] = " ".join(x for y in soup.select("#about > p") for x in y.strings).strip()
		
		return data
		
	def _data_hokkaido(self, url):
		# Hokkaido University
		soup = BeautifulSoup(rsess.get(url).text)
		data = {"providername": "Hokkaido University"}
		
		data["title"] = soup.select("#MAIN h1")[0].string.strip()
		data["description"] = soup.select("#MAIN p")[0].string.strip()
	
		return data
		
	def _data_ie(self, url):
		# IE University
		course_id = url.split("=")[1]
		soup = BeautifulSoup(rsess.get("http://ocw.ie.edu/ocw/cur%s01_esp.html" % course_id.zfill(2)).text)
		data = {"providername": "IE University"}
		
		data["title"] = soup.select(".ari_18_negrita")[0].string.strip()
		data["description"] = " ".join(x.strip() for x in soup.select(".ari_12_negra")[-1].strings)
		data["author"] = soup.select(".ari_12_negra")[2].select(".ari_12_negrita")[0].string.strip()
	
		return data
		
	def _data_hopkins(self, url):
		# Johns Hopkins Bloomberg School of Public Health
		soup = BeautifulSoup(rsess.get(url).text)
		data = {"providername": "Johns Hopkins Bloomberg School of Public Health"}
		
		data["title"] = " ".join(x.strip() for x in soup.select("h1")[-1].strings if type(x) != bs4.element.Comment)
		data["author"] = soup.select("#courseInfoBox p")[0].string.strip()
		data["description"] = soup.select("#courseImageAndInfoBox p")[-1].string.strip()
		
		return data
		
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
			
#crawler = OpenCourseWareCrawler()
#crawler.parse_catalog()
