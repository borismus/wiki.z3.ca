class Parser:
    """
        Send HTML code raw
    """

    def __init__(self, raw, request, **kw):
        self.html = raw
        self.request = request

    def format(self, formatter):
        """ Send the "parsed" text.
        """
        #this is pretty easy since converting HTML to HTML is a no-brainer
        self.request.write(formatter.rawHTML(self.html))
