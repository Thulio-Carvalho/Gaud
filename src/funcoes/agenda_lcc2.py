#coding: utf-8
import requests
from bs4 import BeautifulSoup

def date_decode(date):
#    20181108T110000Z
#    08/11/2018 11:00
    day = "%s/%s/%s" % (date[6:8],date[4:6],date[0:4])
    hour = "%s:%s" %(date[9:11],date[11:13])
    return [day,hour]

def get_events():
    page = requests.get("https://calendar.google.com/calendar/htmlembed?src=computacao.ufcg.edu.br_80qc5chl59nmv2268aef8hp528@group.calendar.google.com&mode=AGENDA")

    soup = BeautifulSoup(page.content, 'html.parser')

    for name in soup.find_all('a', attrs={'class': 'event-link'}):
        page = BeautifulSoup(requests.get("https://calendar.google.com/calendar/"+name['href']).content, 'html.parser')
        event = [name.text.strip()]
        for time in page.find_all('time'):
            event.append(date_decode(time['datetime']))
#        event.append("https://calendar.google.com/calendar/"+name['href'])
        yield event

data = raw_input("Data: ")
print "\n".join(["%s (%s - %s)" % (i[0],i[1][1],i[2][1]) for i in get_events() if str(i[1][0]) == data])







"""
for foo in soup.find_all('div', attrs={'class': 'date-section date-section-odd date-section-3'}):

	for foo2 in foo.descendants:
		
		if "\n" != foo2 != "" and ("<" not in foo2 or "class" not in foo2):
			a = foo2.string
			if a != None:
				info.append(unicodedata.normalize('NFKD', a).encode('ascii','ignore'))
			
print info
print "\n".join(set(info))
""
for foo in soup.find_all('div', attrs={'class': 'view-container'}):
	date = []
	for foo2 in foo.descendants:
		text = list(foo2)[0]
		print text
		print type(text)
                if "href" in text:
                    print "site"
		if type(text) is unicode and text.lstrip():
			print foo2.lstrip()
			date.append(foo2.lstrip())
	print date

"""

