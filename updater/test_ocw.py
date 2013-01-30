import update_ocw

c = update_ocw.OpenCourseWareCrawler()
print c.get_provider_data("http://ocw.jhsph.edu/courses/AdolHealthDev/?source=rss")
