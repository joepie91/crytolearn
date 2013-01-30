#!/usr/bin/env python
import shared, scrapers

env = shared.Environment()
env.connect(host="localhost", username="root", password="", database="learn")

scraper = env.Scraper(scrapers.KhanAcademy)
scraper.run()
