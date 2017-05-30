# -*- coding: iso-8859-1 -*-
"""
    MoinMoin - rightsidebar theme

    Created by and for crw.
    Later it was rewritten by Nir Soffer for MoinMoin release 1.3.

    @copyright: 2005 by Nir Soffer
    @license: GNU GPL, see COPYING for details.  
"""

from MoinMoin.theme import ThemeBase
from MoinMoin.macro import MonthCalendar
from MoinMoin import wikiutil

class Theme(ThemeBase):

    name = "zyf_rightsidebar_darkblue"

    def wikipanel(self, d):
        """ Create wiki panel """
        _ = self.request.getText
        html = [
            u'<div class="sidepanel">',
            u'<h1>%s</h1>' % _("Wiki"),
            self.navibar(d),
            u'</div>',
            ]
        return u'\n'.join(html)
    
    def pagepanel(self, d):
        """ Create page panel """
        _ = self.request.getText
        if self.shouldShowEditbar(d['page']):
            html = [
                u'<div class="sidepanel">',
                u'<h1>%s</h1>' % _("Page"),
                self.editbar(d),
                u'</div>',
                ]
            return u'\n'.join(html)
        return ''   
        
    def userpanel(self, d):
        """ Create user panel """
        _ = self.request.getText

        html = [
            u'<div class="sidepanel">',
            u'<h1>%s</h1>' %  _("User"),
            self.username(d),
            u'</div>'
            ]
        return u'\n'.join(html)
        
    def calpanel(self, d):
        """ Create calendar panel """
        _ = self.request.getText
        
        
    def header(self, d):
        """
        Assemble page header
        
        @param d: parameter dictionary
        @rtype: string
        @return: page header html
        """
        _ = self.request.getText

        html = [
            # Custom html above header
            self.emit_custom_html(self.cfg.page_header1),

            # Header
            u'<div id="header">',
            self.logo(),
            u'<div id="locationline">',
            self.interwiki(d),
            self.title(d),
            u'</div>',
            self.trail(d),
            u'</div>',
            
            # Custom html below header (not recomended!)
            self.emit_custom_html(self.cfg.page_header2),

            # Sidebar
            u'<div id="sidebar">',
            self.searchform(d),
            self.wikipanel(d),
            self.pagepanel(d),
            self.userpanel(d),
            u'</div>',

            self.msg(d),
            
            # Page
            self.startPage(),
            ]
        return u'\n'.join(html)
    
    def editorheader(self, d):
        """
        Assemble page header for editor
        
        @param d: parameter dictionary
        @rtype: string
        @return: page header html
        """
        _ = self.request.getText

        html = [
            # Custom html above header
            self.emit_custom_html(self.cfg.page_header1),

            # Header
            #u'<div id="header">',
            #self.searchform(d),
            #self.logo(),
            #u'</div>',
            
            # Custom html below header (not recomended!)
            self.emit_custom_html(self.cfg.page_header2),

            # Sidebar
            u'<div id="sidebar">',
            self.wikipanel(d),
            self.pagepanel(d),
            self.userpanel(d),
            u'</div>',

            self.msg(d),
            
            # Page
            self.startPage(),
            #self.title(d),
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
            self.pageinfo(page),
            self.endPage(),
            
            # Pre footer custom html (not recommended!)
            self.emit_custom_html(self.cfg.page_footer1),
            
            # Footer
            u'<div id="footer">',
            self.credits(d),
            self.showversion(d, **keywords),
            u'</div>',
            
            # Post footer custom html
            self.emit_custom_html(self.cfg.page_footer2),
            ]
        return u'\n'.join(html)
        
    def searchform(self, d):
        """
        assemble HTML code for the search forms
        
        @param d: parameter dictionary
        @rtype: unicode
        @return: search form html
        """
        _ = self.request.getText
        form = self.request.form
        updates = {
            'search_label' : _('Search:'),
            'search_value': wikiutil.escape(form.get('value', [''])[0], 1),
            'search_full_label' : _('Text', formatted=False),
            'search_title_label' : _('Titles', formatted=False),
            }
        d.update(updates)

        html = u'''
<form id="searchform" method="get" action="">
<div>
<input type="hidden" name="action" value="fullsearch">
<input type="hidden" name="context" value="180">
<label for="searchinput">%(search_label)s</label>
<input id="searchinput" type="text" name="value" value="%(search_value)s" size="20"
    onfocus="searchFocus(this)" onblur="searchBlur(this)"
    onkeyup="searchChange(this)" onchange="searchChange(this)" alt="Search">
<br />
<input id="titlesearch" name="titlesearch" type="submit"
    value="%(search_title_label)s" alt="Search Titles">
<input id="fullsearch" name="fullsearch" type="submit"
    value="%(search_full_label)s" alt="Search Full Text">
</div>
</form>
<script type="text/javascript">
<!--// Initialize search form
var f = document.getElementById('searchform');
f.getElementsByTagName('label')[0].style.display = 'none';
var e = document.getElementById('searchinput');
searchChange(e);
searchBlur(e);
//-->
</script>
''' % d
        return html


def execute(request):
    """ Generate and return a theme object
        
    @param request: the request object
    @rtype: MoinTheme
    @return: Theme object
    """
    return Theme(request)

