#!/usr/bin/env python

import requests, sys, re

query = sys.argv[1]

results = requests.post("http://learn.cryto.net/api/search", {"q": query}).json()

for result in results:
	name = result["title"].rstrip()
	description = result["description"].strip().replace("\n", " ")
	
	if len(description) > 200:
		description = re.match("^(.{0,300})\W", description).group(1) + "..."
	
	print "## %s\n%s" % (name, description)
	
	for item in result["items"]:
		name = item["title"].ljust(70)
		print "\t[%s] %s\t%s" % (item["type"], name, item["url"])

	print ""
