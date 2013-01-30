import datetime, json, sys
import requests, oursql
import shared

class KhanAcademy(shared.Scraper):
	provider_id = 1
	
	def run(self):
		self.retrieve_dataset()
		self.process_item(self.dataset, 0)
		
	def retrieve_dataset(self):
		self.dataset = requests.get("http://www.khanacademy.org/api/v1/topictree").json()
		
	def process_item(self, item, level, parent=None):
		try:
			kind = item["kind"]
		except KeyError, e:
			return
		
		if kind == "Topic":
			self.process_topic(item, level, parent=parent)
		elif kind in ("Video", "Exercise", "Article", "Scratchpad"):
			self.process_object(item, level, parent=parent)
		elif kind == "Separator":
			pass  # Ignore separators
		else:
			self.env.log("Unrecognized kind: %s" % repr(item["kind"]), True)
		
		try:
			children = item["children"]
		except KeyError, e:
			return
			
		for child in children:
			self.process_item(child, level + 1, item)
			
	def process_topic(self, item, level, parent=None):
		unique_id = item["id"]
			
		try:
			parent_id = parent["_cl_id"]
		except TypeError, e:
			parent_id = 0
			
		# Check if a title is set
		if item["title"] is not None:
			title = item["title"]
		else:
			# No title was set - log this as an error and default to 'Untitled'.
			self.env.log("No title found for item: %s" % repr(item), True)
			title = "Untitled"
		
		# Check if a description is set, and default to no description if not
		if item["description"] is not None:
			description = item["description"]
		else:
			description = None
		
		# Insert the topic
		inserted, row_id = self.insert_topic(unique_id, title, description=description, needs_enrollment=False)
		
		# Set the ID of the newly inserted row so that all objects in this topic know the ID of their topic.
		item["_cl_id"] = row_id
		
		if inserted:
			self.env.log("Inserted %s" % title)
		else:
			self.env.log("Skipped %s" % title)
			
	def process_object(self, item, level, parent=None):
		unique_id = None
		
		# First check for the 'readable_id' property
		try:
			unique_id = item["readable_id"]
		except KeyError, e:
			pass
		
		# If no identifier was found, check for the 'name' property
		if unique_id is None:
			try:
				unique_id = item["name"]
			except KeyError, e:
				pass
		
		# If still no identifier was found, check for the 'id' property
		if unique_id is None:
			try:
				unique_id = str(item["id"])
			except KeyError, e:
				pass
		
		# If we *still* do not have an identifier, log the error and bail out
		if unique_id is None:
			self.env.log("No suitable identifier found for item: %s" % repr(item), True)
			return
		
		# Determine the object type
		if item["kind"] == "Video":
			itemtype = self.VIDEO
		elif item["kind"] == "Exercise":
			itemtype = self.EXERCISE
		elif item["kind"] == "Article":
			itemtype = self.ARTICLE
		elif item["kind"] == "Scratchpad":
			itemtype = self.SANDBOX
		
		source_url = None
		
		# Determine the source URL via the 'ka_url' property
		try:
			source_url = item["ka_url"]
		except KeyError, e:
			pass
		
		# If no source URL was found, try the 'url' property
		if source_url is None:			
			try:
				source_url = item["url"]
			except KeyError, e:
				pass
		
		# If still no source URL was found...
		if source_url is None:
			if itemtype == self.ARTICLE:
				# Articles can lack a URL.
				source_url = None
			else:
				# There was no source URL, but this wasn't an article. Log the error and bail out.
				self.env.log("No source URL found for non-article object: %s" % repr(item), True)
				return
		
		# Determine the (external) item URL
		try:
			item_url = item["url"]
		except KeyError, e:
			# Apparently there was no external item URL. Use the source URL as item URL - this will most likely be correct.
			item_url = source_url
		
		# If the object is an article, we'll want to use the actual article content as description.
		if itemtype == self.ARTICLE:
			description = item["content"]
		else:
			# Otherwise, we'll check if there's a 'description' property. If not, leave empty.
			try:
				description = item["description"]
			except KeyError, e:
				description = None
		
		title = None
		
		# First check the 'title' property for an object title.
		try:
			title = item["title"]
		except KeyError, e:
			pass
		
		# As second option, check the 'display_name' property.
		if title is None:
			try:
				title = item["display_name"]
			except KeyError, e:
				# Apparently it really does not have a title. Log the error and default to 'Untitled'.
				self.env.log("No object title found for item: %s" % repr(item), True)
				title = "Untitled"
		
		# If a 'views' property is present, include it.
		try:
			views = item["views"]
		except KeyError, e:
			views = None
		
		# If a creation date is present, include it.
		try:
			date = datetime.datetime.strptime(item["date_added"], "%Y-%m-%dT%H:%M:%SZ")
		except KeyError, e:
			date = None
		
		# Check if there is a parent ID
		try:
			parent_id = parent["_cl_id"]
		except KeyError, e:
			# No parent ID present - log this as an error and default to 0.
			self.env.log("No parent ID found for item: %s" % repr(item), True)
			parent_id = 0
		
		# Insert the item
		inserted, row_id = self.insert_item(unique_id, title, item_url, itemtype=itemtype, has_topic=True, source_url=source_url, description=description, views=views, topic_id=parent_id, date=date)
		
		# Store the resulting row ID in the item so that the children know the ID of their parent.
		item["_cl_id"] = row_id
		
		if inserted:
			self.env.log("Inserted %s" % title)
		else:
			self.env.log("Skipped %s" % title)
