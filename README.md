# Cryto Learn

This is the source code for http://learn.cryto.net/. It consists of the following:

* The updating script, a few very rudimentary scrapers for various educational sources. Requires Python 2. Dependencies are [requests](http://docs.python-requests.org/en/latest/) and BeautifulSoup 4 (custom version included). Located in `updater/`.
* The frontend, a fairly hacky and messy PHP-based search interface. Needs cleaning up, but not an immediate priority. Requires PHP 5.3+ and uses [CPHP](http://github.com/joepie91/cphp). Located in `frontend/`.
* A simple shell search script, using the Cryto Learn API to search for the specified string and print results to stdout. Requires Python 2. Also very rudimentary.

Licensed under the WTFPL. It may or may not work on your system, use at your own risk, etc. etc.
