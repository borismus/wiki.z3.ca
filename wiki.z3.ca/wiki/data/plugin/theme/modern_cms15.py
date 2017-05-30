"""
Modern based cms theme
======================

If you want to use a wiki as a tool to create a regular site easily,
this theme is for you. The wiki looks like a plain site to visitors or
users without edit rights, and a wiki to users with edits rights. 

This is also a replacement for the readonly theme that was part of release 1.2.


Problems
--------
Some actions are not available for visitors:

- Show Raw Text
- Show Print Preview
- Show Like Pages
- Show Local Site Map
- Delete Cache

Most of these are not really needed for a visitor. Print style sheet is
used transparently when you print a page. Like Pages and Local Site Map
should be available, but are not really needed if you have a good
search.

Missing page will suggest visitors to create a new page, but they will
always fail because they don't have acl rights. This should be fixed in
other place.


Install
-------

1. Put in your wiki/data/plugin/theme/

2. Prevent visitors from writing using acl::

    acl_rights_before = (u"WikiAdmin:read,write,delete,revert,admin "
                         u"EditorsGroup:read,write,delete,revert ")
    acl_rights_default = u"All:read "
                          
Remember that some ACL you put on a page will override the default ACL!

3. Make it the default and only theme on your site::

    theme_default = 'modern_cms'
    theme_force = True
    
    
Compatibility
--------------
Tested with release 1.5.1, should work with any 1.5 release.


Legal
-----
@copyright (c) 2005 Nir Soffer <nirs@freeshell.org>
@copyright (c) 2006 Thomas Waldmann
@license: GNU GPL, see COPYING for details

"""

from MoinMoin.theme import modern

class Theme(modern.Theme):
    
    name = "modern" # uses "modern" CSS and images

    def shouldShowEditbar(self, page):
        """ Hide the edit bar if you can't edit """
        if self.request.user.may.write(page.page_name):
            return modern.Theme.shouldShowEditbar(self, page)
        return False

    def pageLastName(self, name):
        """ This should be in the Page class, but its not """
        return name[name.rfind('/') + 1:]

    def shortenPagename(self, name):
        """ Shorten page names
        
        This is a modified copy from theme/__init__.py. Modified to
        show only the last name of a page, even if there is room for
        the full name.
        """
        name = self.pageLastName(name)
        maxLength = self.maxPagenameLength()
        if len(name) > maxLength:
            half, left = divmod(maxLength - 3, 2)
            name = u'%s...%s' % (name[:half + left], name[-half:])
        return name

    def footer(self, d, **keywords):
        """ same as modern footer, but no pageinfo """
        page = d['page']
        html = [
            # End of page
            self.endPage(),
            
            # Pre footer custom html (not recommended!)
            self.emit_custom_html(self.cfg.page_footer1),
            
            # Footer
            u'<div id="footer">',
            self.editbar(d),
            self.credits(d),
            self.showversion(d, **keywords),
            u'</div>',
            
            # Post footer custom html
            self.emit_custom_html(self.cfg.page_footer2),
            ]
        return u'\n'.join(html)

def execute(request):
    return Theme(request)

