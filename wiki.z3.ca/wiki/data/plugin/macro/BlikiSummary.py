"""
 Abridged RecentChanges-like summary of a blog-wiki (bliki) page

 Copyright (C) 2007 Boris Smus <boris@z3.ca>
 Licence: GPL [see http://www.gnu.org/copyleft/gpl.html]
"""

from MoinMoin.logfile import editlog
from MoinMoin import wikiutil
from MoinMoin.Page import Page

import time

Dependencies = ["time"]

DAY_IN_SECS = 86400
NUMBER_OF_CHANGES = 10
NUMBER_OF_DAYS = 20

def execute(macro, args):
    request = macro.request
    _ = request.getText
    log = editlog.EditLog(request)

    now = long(time.time())

    pages = []
    for page in log.reverse():
	if not request.user.may.read(page.pagename):
	    # ignore pages that aren't readable
	    continue

	# last edited time property
	edit_time = wikiutil.version2timestamp(page.ed_time_usecs)
	# the day modification of 
	page.edit_diff = time_diff(now, edit_time)

	if page.edit_diff[0] > NUMBER_OF_DAYS:
	    # all further pages are older
	    break
	
	if Page(request, page.pagename).exists() and \
	    page.pagename not in [p.pagename for p in pages]:
	    # if this page was edited today, it exists and we haven't yet
	    # seen it
	    pages.append(page)
	    if len(pages) > NUMBER_OF_CHANGES:
		break
	    prev_pagename = page.pagename
    #return `[page.pagename for page in pages]`

    html = []
    html.append(macro.formatter.number_list(1))
    for page in pages:
	html.append(macro.formatter.listitem(1))
	html.append(macro.formatter.pagelink(1, page.pagename, generated=1))
	html.append(macro.formatter.text(page.pagename))
	html.append(macro.formatter.pagelink(0))

	diff = page.edit_diff
	html.append(macro.formatter.text(" changed "))
	if diff[0] != 0:
	    # more than a day ago
	    html.append(macro.formatter.text(" %d day%s " % 
		(diff[0], (diff[0] > 1 and 's' or ''))))
	if diff[1] != 0:
	    html.append(macro.formatter.text(" %d hour%s " % 
		(diff[1], (diff[1] > 1 and 's' or ''))))
	else:
	    html.append(macro.formatter.text(" %d minute%s" % 
		(diff[2], (diff[2] > 1 and 's' or ''))))
	html.append(macro.formatter.text(" ago."))


	html.append(macro.formatter.listitem(0))
    html.append(macro.formatter.number_list(0))

    return "".join(html)

def time_diff(t1, t2):
    t = t1 - t2
    t,s = divmod(t,60) 
    t,m = divmod(t,60)
    d,h = divmod(t,24)
    return (d,h,m,s)
