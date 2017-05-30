# -*- coding: iso-8859-1 -*-
"""
	MentalWealth is a MoinMoin theme
	by robin.escalation@ACM.org.
	
	Licensed under GPL.
	Do not remove credit or claim it as your own.

	For more info see the readme.html.
"""
from MoinMoin.theme import ThemeBase
from MoinMoin.wikiutil import link_tag as link
from MoinMoin.wikiutil import quoteWikinameURL as quoteURL

class Theme(ThemeBase):
	name = 'mentalwealth'

	def editbar(self, d):
		"""
			Assemble the page edit bar.

			This is rewritten here to get rid of fugly drop-down menu.
			(Obviating the need for the actionsMenu() method).

			Also I tried to reduce the number of aliases 'cause I find
			that hard to follow.
			
			@param d: parameter dictionary
			@rtype: unicode
			@return: iconbar html
		"""
		# short circuit
		if not self.shouldShowEditbar(d['page']):
			return ''

		# use cached copy if possible
		cacheKey = 'editbar'
		cached = self._cache.get(cacheKey)
		if cached:
			return cached

		# initialisations & optimisation
		_ = self.request.getText
		page = d['page']
		quotedname = quoteURL(page.page_name)
		
		# each action in this list is a line on the editbar panel
		links = []

		# parent page
		parent = page.getParentPage()
		if parent:
			links += [parent.link_to(self.request, _('Show Parent', formatted=False))]
		
		# the rest we will do cleverly :-)
		# these are the possible actions and their text labels
		choices = [	['edit',			'edit'],
					['diff',			'show changes'],
					['info',			'get info'],
					['raw',				'show raw text'],
					['print',			'show print view'],
					['refresh',			'delete cache'],
					['AttachFile',		'attach file'],
					['SpellCheck',		'check spelling'],
					['LikePages',		'show like pages'],
					['LocalSiteMap',	'show local site map'],
					['RenamePage',		'rename page'],
					['DeletePage',		'delete page']
					]
		
		# determine which actions we can use
		available = self.request.getAvailableActions(page)
		for action, label in choices:
			if action == 'refresh' and not page.canUseCache():
				continue
			if action == 'edit' and not (page.isWritable() and self.request.user.may.write(page.page_name)):
				continue
			if action[0].isupper() and not action in available:
				continue

			links += [link(self.request, '%s?action=%s' % (quotedname, action),
						_(label, formatted=False))]
			
		# delegate this next part so I can stop rewriting code ;-)
		links += [self.subscribeLink(page)]

		# wrap it all up nicely
		html = u'<ul class="editbar">\n%s\n</ul>\n' %\
			   '\n'.join(['<li>%s</li>' % item for item in links if item != ''])

		# cache for next call
		self._cache[cacheKey] = html
		return html

	def header(self, d, **kw):
		"""
			Assemble page header, which includes our sidebar.
			
			@param d: parameter dictionary
			@rtype: string
			@return: page header html
		"""
		_ = self.request.getText

		# there are 5 main panels: each one follows this markup
		html = u'<div class="sidepanel"><h1>%s</h1>%s</div>'
		
		# "search" panel hack so I don't have to rewrite searchform()
		searchpanel = self.searchform(d).replace('<input id="titlesearch"',
												 '<br><input id="titlesearch"')

		# bundle up all our parts
		parts = [	self.emit_custom_html(self.cfg.page_header1),
					'<div id="header">%s</div>' % self.logo(),
					self.emit_custom_html(self.cfg.page_header2),
					u'<div id="sidebar">',
					html % (_('Search'),     searchpanel),
					html % (_('Navigation'), self.navibar(d)),
					html % (_('Recent'),     self.trail(d)),
					html % (_('This Page'),  self.editbar(d)),
					html % (_('User'),       self.username(d)),
					self.credits(d),
					u'</div>',
					self.msg(d),		
					self.startPage()
					]
		return u'\n'.join(parts)
	
	def footer(self, d, **kw):
		"""
			Assemble page footer
			
			@param d: parameter dictionary
			@keyword ...:...
			@rtype: string
			@return: page footer html
		"""
		parts = [	u'<div id="pagebottom"></div>',
					self.pageinfo(d['page']),
					self.endPage(),
					self.emit_custom_html(self.cfg.page_footer1),
					self.emit_custom_html(self.cfg.page_footer2),
					]
		return u'\n'.join(parts)

def execute(request):
	"""
		Generate and return a theme object.
	"""
	return Theme(request)
