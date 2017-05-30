# -*- coding: iso-8859-1 -*-
"""
    MoinMoin ubuntu theme

    @copyright: (c) 2003-2004 by Nir Soffer, Thomas Waldmann
    @license: GNU GPL, see COPYING for details.

    Borrows heavily from modern, a bit from Classic, and has a few 
    things of its own.
"""

from MoinMoin.theme import ThemeBase
from MoinMoin import wikiutil
from MoinMoin.Page import Page
import re

class Theme(ThemeBase):

    name = 'balanced2'

# Overriding theme/__init__.py #########################################

    # fake _ function to get gettext recognize those texts:
    _ = lambda x: x

    # TODO: remove icons that are not used any more.
    icons = {
        # key         alt                        icon filename      w   h
        # ------------------------------------------------------------------
        # navibar
        'help':       ("%(page_help_contents)s", "s-help.png",         20, 20),
        'find':       ("%(page_find_page)s",     "s-search.png",       20, 20),
        'diff':       (_("Diffs"),               "diff.png",         22, 22),
        'info':       (_("Info"),                "info.png",         22, 22),
        'edit':       (_("Edit"),                "edit.png",         20, 20),
        'unsubscribe':(_("Unsubscribe"),         "unsubscribe.png",  23, 21),
        'subscribe':  (_("Subscribe"),           "subscribe_dk.png", 23, 21),
        'raw':        (_("Raw"),                 "raw.png",          21, 23),
        'xml':        (_("XML"),                 "moin-xml2.png",      36, 14),
        'print':      (_("Print"),               "print.png",        20, 20),
        'view':       (_("View"),                "show.png",         20, 20),
        'home':       (_("Home"),                "home.png",         20, 20),
        'up':         (_("Up"),                  "parent.png",       20, 20),
        # FileAttach
        'attach':     ("%(attach_count)s",       "moin-attach.png",  7, 15),
        # RecentChanges
        'rss':        (_("[RSS]"),               "moin-rss.png",    36, 14),
        'deleted':    (_("[DELETED]"),           "deleted.png",      22, 22),
        'updated':    (_("[UPDATED]"),           "updated.png",      22, 22),
        'new':        (_("[NEW]"),               "new.png",          22, 22),
        'diffrc':     (_("[DIFF]"),              "diff.png",         22, 22),
        # General
        'bottom':     (_("[BOTTOM]"),            "bottom.png",       14, 10),
        'top':        (_("[TOP]"),               "top.png",          14, 10),
        'www':        ("[WWW]",                  "www.png",          16, 16),
        'mailto':     ("[MAILTO]",               "email.png",        23, 13),
        'news':       ("[NEWS]",                 "news.png",         16, 16),
        'telnet':     ("[TELNET]",               "telnet.png",       16, 16),
        'ftp':        ("[FTP]",                  "ftp.png",          16, 16),
        'file':       ("[FILE]",                 "ftp.png",          16, 16),
        # search forms
        'searchbutton': ("[?]",                  "s-search.png",       20, 20),
        'interwiki':  ("[%(wikitag)s]",          "inter.png",        16, 16),
    }
    del _

# Public functions #####################################################

    def header(self, d, **kw):
        """ Assemble wiki header
        
        @param d: parameter dictionary
        @rtype: unicode
        @return: page header html
        """
        html = [
            # Header
            u'<div id="mastwrap">',
			u'<div id="masthead">',
            self.searchform(d),
            self.sisternav(),
            u'</div> <!-- of masthead -->',
			u'</div> <!-- of mastwrap -->',	
            u'<div id="outerColumnContainer"><div id="innerColumnContainer">',

			u'<div id="leftColumn"><div class="inside">Left',
            #self.leftsidemenu(d),
            u'</div></div> <!-- of leftColumn & inside -->',	
			
			u'<div id="rightColumn"><div class="inside">Right',
            #self.rightsidemenu(d),
            u'</div></div> <!-- of rightColumn & inside -->',
						
            u'<div id="contentColumn"><div class="inside">',
        ]
        return u'\n'.join(html)

    def footer(self, d, **keywords):
        """ Assemble wiki footer
        
        @param d: parameter dictionary
        @keyword ...:...
        @rtype: unicode
        @return: page footer html
        """
        page = d['page']
        html = [
            u'</div></div> <!-- of contentColumn & inside -->',			
			u'<div class="clear mozclear"></div>',
            u'</div></div> <!-- of outerColumnContainer & innerColumnContainer -->',
            # Footer
			u'<div id="footer" class="inside">',
            self.footerlinks(),
            u'</div>',
            ]
        return u'\n'.join(html)

    def extranav(self, d):
        """ Assemble the helpful extra navigation

	Of course in a normal theme these come from wikiconfig.py 
        
        @param d: parameter dictionary
        @rtype: unicode
        @return: extranav html
        """
        request = self.request
        _ = request.getText
        changesPage = wikiutil.getSysPage(request, 'RecentChanges')
        findPage = wikiutil.getSysPage(request, 'FindPage')
        
        extralinks = []
        # Set page to localized RC page
        title = changesPage.split_title(request)
        extralinks.append(changesPage.link_to(request, text=title))
        # Set page to localized find page
        title = findPage.split_title(request)
        extralinks.append(findPage.link_to(request, text=title))
            
        extralinks = [u'<li>%s</li>\n' % link for link in extralinks]
        html = u'<ul class="extranav">\n%s</ul>' % ''.join(extralinks)
        return html

    def leftsidemenu(self, d):
		""" Assemble the side menu """
		
		html = 'error'
		menuTag = "##MENU .*html" 
		menuPath = "C:\\APPS\\MMDE\\wiki\\data\\pages\\MenuPages\\attachments\\"  # FIXME: abstract out the path
		pageBody = self.request.page.get_raw_body()
		menuLineObj = re.search(menuTag, pageBody)
		# catch bad or missing tag
		if menuLineObj:
			menuLine = menuLineObj.group()
			fileName = re.sub("##MENU ","",menuLine)
		else:
			fileName = 'sidemenu-default.html'

		# catch non-existant files
		try:
			fullName = menuPath+fileName
			fileHandle = open(fullName)
		except IOError: 
			fileName = 'sidemenu-default.html'
			fullName = menuPath+fileName
			fileHandle = open(fullName)

		html = fileHandle.read()
		fileHandle.close()
		return html
	
    def rightsidemenu(self, d):
		""" Assemble the side menu """
		
		html = 'error'
		menuTag = "##MENU .*html" 
		menuPath = "C:\\APPS\\MMDE\\wiki\\data\\pages\\MenuPages\\attachments\\"  # FIXME: abstract out the path
		pageBody = self.request.page.get_raw_body()
		menuLineObj = re.search(menuTag, pageBody)
		# catch bad or missing tag
		if menuLineObj:
			menuLine = menuLineObj.group()
			fileName = re.sub("##MENU ","",menuLine)
		else:
			fileName = 'sidemenu-default.html'

		# catch non-existant files
		try:
			fullName = menuPath+fileName
			fileHandle = open(fullName)
		except IOError: 
			fileName = 'sidemenu-default.html'
			fullName = menuPath+fileName
			fileHandle = open(fullName)

		html = fileHandle.read()
		fileHandle.close()
		return html
		
    def navibar(self, d):
        """ Assemble the navibar

        @param d: parameter dictionary
        @rtype: unicode
        @return: navibar html
        """
        request = self.request
        found = {} # pages we found. prevent duplicates
        items = [] # navibar items
        item = u'<li class="%s">%s</li>'
        current = d['page_name']

        # Add user links to wiki links, eliminating duplicates.
        userlinks = request.user.getQuickLinks()
        for text in userlinks:
            # Split text without localization, user know what she wants
            pagename, link = self.splitNavilink(text, localize=0)
            if not pagename in found:
                cls = 'userlink'
                if pagename == current:
                    cls = 'userlink current'
                items.append(item % (cls, link))
                found[pagename] = 1

        # Assemble html
        items = u'\n'.join(items)
        html = u'''
<ul id="navibar">
%s
</ul>
''' % items
        return html

    def username(self, d):
        """ Assemble the username / userprefs link
        
        @param d: parameter dictionary
        @rtype: unicode
        @return: username html
        """
        request = self.request
        _ = request.getText
        preferencesPage = wikiutil.getSysPage(request, 'UserPreferences')
        helpPage = wikiutil.getSysPage(request, 'HelpContents')
        
        userlinks = []
        # Add username/homepage link for registered users. We don't care
        # if it exists, the user can create it.
        if request.user.valid:
            homepage = Page(request, request.user.name)
            title = homepage.split_title(request)
            homelink = homepage.link_to(request, text=title)
            userlinks.append(homelink)        
            # Set pref page to localized Preferences page
            title = preferencesPage.split_title(request)
            userlinks.append(preferencesPage.link_to(request, text=title))
            userlinks.append(helpPage.link_to(request, text=_("Help")))
        else:
            # Add prefpage links with title: Login
            userlinks.append(preferencesPage.link_to(request, text=_("Login")))
            
        userlinks = [u'<li>%s</li>\n' % link for link in userlinks]
        html = u'<ul id="username">\n%s</ul>' % ''.join(userlinks)
        return html

    def sisternav(self):
		""" Assemble fancy nav tabs to the sister sites   """
		
		html = u'''<div id="sisternav">
      <ul>
        <li id="current"><a href="/FrontPage" >Wiki</a></li>
      </ul>
  </div>'''

		return html

    def footerlinks(self):
        """ Copyright notices and local links """
        html = u'''
     &copy; Henrik Nilsen Omma
     <a href="/UserPreferences">Admin</a>
'''
	return html

def execute(request):
    """
    Generate and return a theme object
        
    @param request: the request object
    @rtype: MoinTheme
    @return: Theme object
    """
    return Theme(request)

