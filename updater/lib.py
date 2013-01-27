import datetime, oursql

class Database(object):
	TOPIC = 1
	COURSE = 2
	VIDEO = 3
	ARTICLE = 4
	EXERCISE = 5
	QUIZ = 6
	TEST = 7
	BOOK = 8
	AUDIOBOOK = 9
	
	def __init__(self, host, user, password=None, database="learn"):
		self.database = oursql.connect(host=host, user=user, db=database)
	
	def insert_topic(self, provider, unique_id, title, override=False, **kwargs):
		defaults = {
			"needs_enrollment": False,
			"creation_date": None,
			"start_date": None,
			"end_date": None,
			"parent_id": 0,
			"description": ""
		}
		
		for kwarg, val in defaults.iteritems():
			try:
				if kwargs[kwarg] == None:
					kwargs[kwarg] = defaults[kwarg]
			except KeyError, e:
				kwargs[kwarg] = defaults[kwarg]
		
		c = self.database.cursor()
		
		if override == True:
			exists = False
		else:
			c.execute("SELECT `Id` FROM topics WHERE `Provider` = ? AND `ProviderId` = ? LIMIT 1", (provider, unique_id))
			results = c.fetchall()
			exists = (len(results) > 0)
			
		if exists == True:
			return (False, results[0][0])
		else:
			c.execute("INSERT INTO topics (`ParentId`, `Provider`, `ProviderId`, `Title`, `Description`, `Created`, `NeedsEnrollment`, `StartDate`, `EndDate`)"
				  "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", (kwargs['parent_id'], provider, unique_id, title, kwargs['description'], kwargs['creation_date'], 
				                                         kwargs['needs_enrollment'], kwargs['start_date'], kwargs['end_date']))
			
			return (True, c.lastrowid)
	
	def insert_item(self, provider, unique_id, has_topic, itemtype, title, item_url, override=False, **kwargs):
		defaults = {
			"views": None,
			"source_url": item_url,
			"topic_id": 0,
			"parent_id": 0,
			"description": "",
			"date": None
		}
		
		for kwarg, val in defaults.iteritems():
			try:
				if kwargs[kwarg] == None:
					kwargs[kwarg] = defaults[kwarg]
			except KeyError, e:
				kwargs[kwarg] = defaults[kwarg]
		
		c = self.database.cursor()
		
		if override == True:
			exists = False
		else:
			c.execute("SELECT `Id` FROM items WHERE `Provider` = ? AND `ProviderId` = ? LIMIT 1", (provider, unique_id))
			results = c.fetchall()
			exists = (len(results) > 0)
			
		if exists == True:
			return (False, results[0][0])
		else:
			c.execute("INSERT INTO items (`HasTopic`, `Type`, `Provider`, `ProviderId`, `Title`, `Description`, `ItemUrl`, `SourceUrl`, `Views`, `TopicId`, `ParentId`, `Date`)"
				  "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (has_topic, itemtype, provider, unique_id, title, kwargs["description"], item_url, kwargs["source_url"], 
									       kwargs["views"], kwargs["topic_id"], kwargs["parent_id"], kwargs["date"]))
			
			return (True, c.lastrowid)
