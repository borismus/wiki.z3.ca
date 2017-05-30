# -*- coding: iso-8859-1 -*-
"""
    MoinMoin - extensions to ThemeBase

    @copyright: 2006 by Robert Schumann
    @license: GNU GPL, see COPYING for details.
"""

from MoinMoin.theme import ThemeBase

# The following are all for the menu functions
from MoinMoin import wikiutil
from MoinMoin.request import RequestCLI
from MoinMoin.Page import Page
from MoinMoin.action import AttachFile
from MoinMoin.parser.wiki import Parser
from StringIO import StringIO
import re

# TupleList is based on Dict from MoinMoin.wikidict
from UserList import UserList
class TupleList(UserList):
    ''' Mapping of keys to values in a wiki page

       How a TupleList definition page should look like:

       any text ignored
        key1:: value1
        * ignored, too
        key2:: value2 containing spaces
        ...
        keyn:: ....
       any text ignored      
    '''
    # Key:: Value - ignore all but key:: value pairs, strip whitespace
    regex = r'^ (?P<key>.+?):: (?P<val>.*?) *$'

    def __init__(self, request, name):
        """ Initialize, starting from <nothing>.

        Create a list of (key,val) from a wiki page.
        """
        UserList.__init__(self)
        self.name = name
        self.regex = re.compile(self.regex, re.MULTILINE | re.UNICODE)

        # Get text from page named 'name'
        p = Page(request, name)
        text = p.get_raw_body()

        for match in self.regex.finditer(text):
            key, val = match.groups()
            self.append( (key,val) )

class Theme(ThemeBase):

    name = "widget"

    def header(self, d, **kw):
        """ Assemble wiki header
        
        @param d: parameter dictionary
        @rtype: unicode
        @return: page header html
        """
        html = [
            # Pre header custom html
            u'<div id="wholepage">',
            self.emit_custom_html(self.cfg.page_header1),
            
            # Header
            u'<div id="header">',
            self.logo(),
            self.searchform(d),
            #u'<hr id="pageline">',
            #u'<div id="pageline"><hr style="display:none;"></div>',
            u'</div><!--end of #header-->',
            self.msg(d),
            
            # Post header custom html (not recommended)
            self.emit_custom_html(self.cfg.page_header2),
            u'<div id="locationline">',
            self.interwiki(d),
            self.username(d),
            self.title(d),
            self.editbar(d),
            #self.trail(d),
            u'</div><!--end of #locationline-->',
            # Start of page
            self.extraObject(d,'sidemenu'),
            self.startPage(),
        ]
        return u'\n'.join(html)

    def editorheader(self, d, **kw):
        """ Assemble wiki header for editor
        
        @param d: parameter dictionary
        @rtype: unicode
        @return: page header html
        """
        html = [
            # Pre header custom html
            self.emit_custom_html(self.cfg.page_header1),
            
            # Header
            u'<div id="header">',
            self.title(d),
            u'</div>',
            self.msg(d),
            
            # Post header custom html (not recommended)
            self.emit_custom_html(self.cfg.page_header2),
            
            # Start of page
            self.startPage(),
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
            # End of page
            self.endPage(),
            
            # Pre footer custom html (not recommended!)
            self.emit_custom_html(self.cfg.page_footer1),

            # Footer
            u'<div id="footer">',
            self.pageinfo(page),
            self.credits(d),
            self.showversion(d, **keywords),
            u'</div>',
            
            # Post footer custom html
            self.emit_custom_html(self.cfg.page_footer2),
            u'</div><!--end of wholepage-->',
            ]
        return u'\n'.join(html)

    def title(self,d):
       out = ThemeBase.title(self,d)
       return re.sub(r'<ul id="pagelocation">','<ul id="pagelocation"><li><a href="/">Home</a></li> ',out)

    def editbar(self, d):
    	page = d['page']
    	if not self.request.user.may.write(page.page_name):
    		return ''
    	return ThemeBase.editbar(self,d)

    def editbarItems(self, page):
        """ Return list of items to show on the editbar 

        This is separate method to make it easy to customize the
        edtibar in sub classes.
        """
        return [self.editorLink(page),
                self.infoLink(page),
                self.subscribeLink(page),
                self.attachmentsLink(page),
                self.actionsMenu(page),]

    def extraObject(self, d, location):
        """assemble html for side panel goodie"""
        rootPage = wikiutil.quoteWikinameURL('CategorySite/%s' % location)
        page_name = d['page_name']
        wrapHTML = "<div id=%(loc)s>\n %(menu)s\n</div><!-- end of %(loc)s div-->"\
                   % {'loc': location, 'menu': '%s'}
        menuSpec = TupleList(self.request, rootPage)

        # Look in the spec list for a regexp matching the current page name
        matching = [page for (regexp,page) in menuSpec if re.search(regexp,page_name)]
        if not matching:
            return ''
        else:
            return wrapHTML % self.findObjectHTML(rootPage,matching[0])
        

    def findObjectHTML(self, rootPage, dataPage):
        """ Given the name of an object containing target HTML (either
        wikiformatted, preformatted or attached HTML file) retrieve it.

        Wikiformatted files take a long time to load (double the page load time).
        """
        preformattedRegExp = re.compile(r'{{{(.*?)}}}',re.MULTILINE | re.DOTALL)
        targetPage = wikiutil.quoteWikinameURL('%s/%s' % (rootPage, dataPage))
        targetPage = Page(self.request, targetPage)
        menuHtml=''
        if targetPage.isStandardPage(includeDeleted=False):
            # Option 1: It's a page
            unformattedPage = targetPage.get_raw_body()
            if preformattedRegExp.search(unformattedPage):
                # Option 1a: It's preformatted
                menuHtml = re.search(preformattedRegExp, unformattedPage).groups()[0]
            else:
                # Option 1b: It's wikiformatted
                formattedwiki = StringIO()
                # The following is copied from MoinMoin._tests.test_parser_wiki
                request = RequestCLI()
                request.redirect(formattedwiki)
                page = Page(self.request, 'ThisPageDoesNotExistsAndWillNeverBeReally')
                page.set_raw_body(unformattedPage)
                from MoinMoin.formatter.text_html import Formatter
                page.formatter = Formatter(request)
                request.formatter = page.formatter
                page.formatter.setPage(page)
                
                Parser(unformattedPage, request).format(page.formatter)
                menuHtml = formattedwiki.getvalue()
        else:
            # Option 2: It's an attachment
            filePath = AttachFile.getFilename(self.request,rootPage,dataPage)
            try:
             fileHandle = open(filePath)
             try:
              menuHtml = fileHandle.read()
             finally:
              fileHandle.close()
            except:
             pass
        return menuHtml
        
def execute(request):
    """
    Generate and return a theme object
        
    @param request: the request object
    @rtype: MoinTheme
    @return: Theme object
    """
    return Theme(request)

