"""
Delicious bookmark viewer

Copyright (C) 2007 Boris Smus <boris@z3.ca>
Licence: GPL [see http://www.gnu.org/copyleft/gpl.html]
"""

import simplejson, urllib2

USER_NAME = 'miraage'
POST_COUNT = 7
JSON_URL = 'http://del.icio.us/feeds/json/%s/?raw;count=%d' % (USER_NAME, POST_COUNT)
TAG_URL = 'http://del.icio.us/%s/' % USER_NAME + '%s'

Dependencies = []

def execute(macro, args): 
    posts = simplejson.load(urllib2.urlopen(JSON_URL))

    html = []
    html.append(macro.formatter.number_list(1))
    for post in posts:
        html.append(macro.formatter.listitem(1))
        html.append(macro.formatter.url(1, post['u']))
	html.append(post['d'])
        html.append(macro.formatter.url(0))
        html.append(macro.formatter.text(" / "))
	for tag in post['t']:
	    html.append(macro.formatter.url(1, TAG_URL % tag))
	    html.append(tag)
	    html.append(macro.formatter.url(0))
	    html.append(macro.formatter.text(" "))
        html.append(macro.formatter.listitem(0))

    html.append(macro.formatter.number_list(0))

    return "".join(html)
