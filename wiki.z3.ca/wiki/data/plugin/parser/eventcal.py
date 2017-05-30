"""
    eventcal.py  Version 0.90  2005. 11. 15.
                                                                                                           
    This parser gives a parsed format of the event which will be shown at the EventCalendar macro.
                                                                                                           
    @copyright: 2005 by Seungik Lee <seungiklee<at>gmail.com>  http://cds.icu.ac.kr/~silee/
    @license: GPL
    
    For more information, please visit http://moinmoin.wikiwikiweb.de/MacroMarket/EventCalendar
    
    Usage: 
        To insert events, enclose the information about the event records with 'eventcal' parser.
        E.g., 
            {{{#!eventcal
                = [Title] =
                [Start Date] ... [End Date]
                [Start Time] ... [End Time]
            }}}
        
            [Title] should be enclosed with heading marker ('='), double quatation mark ("), wiki italic or bold ('', ''')
                Title can be omitted and it will be titled as 'No Title'
                e.g., == Title ==, === Title ===, "Title", ''Title'', '''Title'''
            
            [Start|End Date] should be in YYYY/MM/DD or YYYY-MM-DD. End date can be omitted.
                e.g, 2005/10/20, 2005-10-20
            
            [Start|End Time] should be in HH:MM in 24-hour format. Both of start|end Time can be omitted but not either of them.
                e.g., 08:00, 12:00, 18:00
            
            In the parsing block of eventcal, it pops out first two date formatted text (startdate and enddate), 
            two time formatted text (starttime, endtime), and quoted or heading titie. 
            
            It ignores further occurrence of the targeted string. 
            The order of each fields (date, time, title) does not matter .
            The start date|time should precede the end date|time in the occurrence respectively.

        You can separate the events starting a '##eventcal' line without any trailing characters.
        E.g., 
            {{{#!eventcal
            = 1st Event =
            StartDate1 ~ EndDate1
            ##eventcal
            = 2nd Event =
            StartDate2 ~ EndDate2
            ...
            }}}
            
    Features:
        Shows the event information in a parsed format.
        Validates the date, time format.


    Notes:
        Much buggy.. :please report bugs and suggest your ideas.
        


"""

import datetime, re
from MoinMoin.parser import wiki
import urllib
from MoinMoin import config

class Parser:

    def __init__(self, raw, request, **kw):
        self.lines = raw
        self.request = request
        option_args = {}
        
        for arg in kw.get('format_args', '').split():
            try:
                key, value = arg.split('=')
                option_args[key.strip()] = value.strip()
            except ValueError:
                pass
                
        self.bgcolor = option_args.get('bgcolor', '')
        self.icon = option_args.get('icon', '')
        self.view = option_args.get('view', '')
        

    def format(self, formatter):
        """ Send the "parsed" text.
        """
        
        self.formatter = formatter
        
        # need help on regular expressions for more efficient/flexible form
        regex_date = r'(\d{4}[/-]\d{2}[/-]\d{2})'
        regex_time = r'(\d{2}[:]\d{2})'
        regex_title = r'["]+(\s*.*?)["]+|[\']{2,5}(\s*.*?)[\']{2,5}|^[=]+(\s*.*?)[=]+$'
        regex_bgcolor = r'^##bgcolor (\s*.*?)$'
        regex_icon = r'^##icon (\s*.*?)$'
        regex_view= r'^##view (\s*.*?)$'
        regex_eventcal = r'[\{]{3}#!eventcal[^\n]*(\s*.*?[^\}]+)[\}]{3}'
        
        msg = ''
        
        # compile regular expression objects
        pattern_date = re.compile(regex_date, re.UNICODE)
        pattern_time = re.compile(regex_time, re.UNICODE)
        pattern_title = re.compile(regex_title, re.UNICODE + re.DOTALL + re.MULTILINE)
        pattern_bgcolor = re.compile(regex_bgcolor, re.UNICODE + re.MULTILINE + re.IGNORECASE)
        pattern_icon = re.compile(regex_icon, re.UNICODE + re.MULTILINE + re.IGNORECASE)
        pattern_view = re.compile(regex_view, re.UNICODE + re.MULTILINE + re.IGNORECASE)
        pattern_eventcal = re.compile(regex_eventcal, re.UNICODE + re.MULTILINE + re.IGNORECASE)
        
        # ignores #!eventcal blocks
        lines = pattern_eventcal.sub(r'\n##eventcal\n\1\n##eventcal\n', self.lines)
        
        # split events
        linesall = lines.split(u'##eventcal\n')
        
        for lines in linesall:
        
            linetemp = lines.strip()
            if not linetemp: 
                continue
            
            title = ''
            startdate = ''
            enddate = ''
            starttime = ''
            endtime = ''
            icon = self.icon
            bgcolor = self.bgcolor
            view = self.view
            
            # retrieve view
            match = pattern_view.search(lines)
            if match:
                view = match.group(0)[7:]
            
            if view == 'none':
                # no need to check valididy
                self.printoutput(lines, '', '', '', '', 1, '', '', view)
                continue
            
            # retrieve date
            match = pattern_date.findall(lines)
            
            if not len(match):
                msg = 'at least one date field should be specified'
                self.printoutput(lines, 'Parse Error', msg, '', '', 0, bgcolor, icon, view)
                continue
            
            # (month, day)-only date should be handled later
            
            startdate = match[0]
            if len(match) > 1:
                enddate = match[1]
            
            # retrieve time
            match = pattern_time.findall(lines)
            
            if len(match) >= 2:
                starttime = match[0]
                endtime = match[1]
            elif len(match) == 0:
                starttime = ''
                endtime = ''
            else:
                msg = 'no or 2 time field should be specified'
                self.printoutput(lines, 'Parse Error', msg, '', '', 0, bgcolor, icon, view)
                continue
                
            # retrieve title
            match = pattern_title.search(lines)
            
            if not match:
                title = 'No title'
            else:
                for item in match.groups():
                    if item:
                        title = item
                        break
            
            # retrieve bgcolor
            match = pattern_bgcolor.search(lines)
            if match:
                bgcolor = match.group(0)[10:]
            
            # retrieve icon
            match = pattern_icon.search(lines)
            if match:
                icon = match.group(0)[7:]
                
            # if no enddate, it's 1-day event
            if (not enddate) and (starttime and endtime):
                enddate = startdate
           
            # check the validity of date/time
            try:
                syear, smonth, sday = getdatefield(startdate)
                if enddate:
                    eyear, emonth, eday = getdatefield(enddate)
            except:
                msg = 'invalid date format'
                self.printoutput(lines, 'Parse Error', msg, '', '', 0, bgcolor, icon, view)
                continue
            
            if startdate and enddate:
                if datetime.date(syear, smonth, sday) > datetime.date(eyear, emonth, eday):
                    msg = 'startdate should precede enddate'
                    self.printoutput(lines, 'Parse Error', msg, '', '', 0, bgcolor, icon, view)
                    continue
    
            if starttime and endtime:
                try:
                    shour, smin = gettimefield(starttime)
                    ehour, emin = gettimefield(endtime)
                except:
                    msg = 'invalid time format'
                    self.printoutput(lines, 'Parse Error', msg, '', '', 0, bgcolor, icon, view)
                    continue
            
                if startdate == enddate:
                    if datetime.time(shour, smin) > datetime.time(ehour, emin):
                        msg = 'starttime should precede endtime'
                        self.printoutput(lines, 'Parse Error', msg, '', '', 0, bgcolor, icon, view)
                        continue
            
            # format output
            fromstring = '%s %s' % (startdate, starttime)
            if enddate:
                tostring = '%s %s' % (enddate, endtime)
            else:
                tostring = ''
            
            startdateforbookmark = u'%d%02d%02d' % (syear, smonth, sday)
            
            self.printoutput(lines, title, fromstring, tostring, startdateforbookmark, 1, bgcolor, icon, view)
    
    def printoutput(self, lines, title='', fromstring='', tostring='', startdateforbookmark='', successflag=1, bgcolor='', icon='', view='table'):
        
        if view == u'footnote':
            self.outputfootnote(lines, title, fromstring, tostring, startdateforbookmark, successflag)
        elif view == u'erroronly':
            self.outputerroronly(lines, title, fromstring, tostring, startdateforbookmark, successflag)
        elif view == u'none':
            self.outputnone(lines, title, startdateforbookmark)
        else:
            self.outputtable(lines, title, fromstring, tostring, startdateforbookmark, successflag, bgcolor, icon)
            

    def outputtable(self, lines, title, fromstring, tostring, startdateforbookmark, successflag, bgcolor='', icon=''):
    
        formatter = self.formatter
        # title += u'[%s]' % self.args
        
        if startdateforbookmark:
            bookmark = u'%s%s' % (title.replace(' ', ''), startdateforbookmark)
            # bookmark = urllib.quote_plus(bookmark.encode(config.charset))
            html = u'<a name="%s"></a>' % bookmark
            self.request.write(formatter.rawHTML(html))
        
        html = [
            u'<table width="100%%" style="border-width:0px;"><tr><td width="100%%" style="border-width:0px; text-align: left; vertical-align: top;">',
            u'',
            ]

        html = u'\n'.join(html)
        self.request.write(formatter.rawHTML(html))
            
        wikiparser = wiki.Parser( lines, self.request )
        wikiparser.format( formatter )
        
        if tostring:
            fromto = '%s<br>~ %s' % (fromstring.strip(), tostring.strip())
        else:
            fromto = '%s' % fromstring.strip()
        
        if successflag:
            if icon:
                flag = icon
            else:
                flag = '(!)'
        else:
            flag = '{X}'
        
        if successflag:
            if bgcolor:
                bgcolor = u'background-color: %s;' % bgcolor
            else:
                bgcolor = u'background-color: #ddffdd;'
        else:
            bgcolor = u'background-color: #ff9933;'
        
        html = [
            u'</td>',
            u'<td style="border-width: 0px; padding: 0px; margin: 0px; border-top-width: 1px; width: 4px;">&nbsp;</td>',
            u'<td style="border-width:0px; border-left-width: 1px; vertical-align: bottom; padding: 0px; margin: 0px;"><table style="width: 140px; border-width:0px; padding: 0px; margin: 0px;">',
            u'<tr><td rowspan="2" style="width: 16px; border-width:1px; border-left-width: 0px; border-right-width: 0px; padding: 0px; margin: 0px; vertical-align: top;">',
            ]

        html = u'\n'.join(html)
        self.request.write(formatter.rawHTML(html))
        
        # flag        
        wikiparser = wiki.Parser( '%s' % flag, self.request )
        wikiparser.format( formatter )
        
        # title, fromto string
        html = [
            u'</td>',
            u'<td style="border-width:1px; border-left-width: 0px; border-bottom-width: 0px; line-height: 8px; padding: 0px; margin: 0px; %s"' % bgcolor,
            u'><font style="font-size: 8pt; font-weight: bold;">%s</font></td></tr>' % title.strip(),
            u'<tr><td style="border-width:1px; border-left-width: 0px; border-top-width: 0px; line-height: 8px; padding: 0px; margin: 0px; text-align: right;"',
            u'><font style="font-size: 7pt;">%s</font></td></tr></td></tr></table></td></tr></table>' % fromto,
            ]

        html = u'\n'.join(html)
        self.request.write(formatter.rawHTML(html))
   
    def outputerroronly(self, lines, title, fromstring, tostring, startdateforbookmark, successflag):
        
        formatter = self.formatter
        
        if tostring:
            fromto = '%s ~ %s' % (fromstring.strip(), tostring.strip())
        else:
            fromto = '%s' % fromstring.strip()
        
        if startdateforbookmark:
            bookmark = u'%s%s' % (title.replace(' ', ''), startdateforbookmark)
            # bookmark = urllib.quote_plus(bookmark.encode(config.charset))
            html = u'<a name="%s"></a>' % bookmark
            self.request.write(formatter.rawHTML(html))
            
        if successflag:
            wikiparser = wiki.Parser( lines, self.request )
            wikiparser.format( formatter )
        else:
                        
            html = [
                u'<table width="100%%" style="border-width:0px;"><tr><td width="100%%" style="border-width:0px; text-align: left; vertical-align: top;">',
                u'',
                ]
    
            html = u'\n'.join(html)
            self.request.write(formatter.rawHTML(html))
                
            wikiparser = wiki.Parser( lines, self.request )
            wikiparser.format( formatter )
            
            flag = '{X}'

            html = [
                u'</td>',
                u'<td style="border-width: 0px; padding: 0px; margin: 0px; border-top-width: 1px; width: 4px;">&nbsp;</td>',
                u'<td style="border-width:0px; border-left-width: 1px; vertical-align: bottom; padding: 0px; margin: 0px;"><table style="width: 140px; border-width:0px; padding: 0px; margin: 0px;">',
                u'<tr><td rowspan="2" style="width: 16px; border-width:1px; border-left-width: 0px; border-right-width: 0px; padding: 0px; margin: 0px; vertical-align: top;">',
                ]
    
            html = u'\n'.join(html)
            self.request.write(formatter.rawHTML(html))
            
            # flag        
            wikiparser = wiki.Parser( '%s' % flag, self.request )
            wikiparser.format( formatter )
            
            # title, fromto string
            html = [
                u'</td>',
                u'<td style="border-width:1px; border-left-width: 0px; border-bottom-width: 0px; line-height: 8px; padding: 0px; margin: 0px;"',
                u'><font style="font-size: 8pt; font-weight: bold;">%s</font></td></tr>' % title.strip(),
                u'<tr><td style="border-width:1px; border-left-width: 0px; border-top-width: 0px; line-height: 8px; padding: 0px; margin: 0px; text-align: right;"',
                u'><font style="font-size: 7pt;">%s</font></td></tr></td></tr></table></td></tr></table>' % fromto,
                ]
    
            html = u'\n'.join(html)
            self.request.write(formatter.rawHTML(html))

    def outputnone(self, lines, title, startdateforbookmark):
        
        formatter = self.formatter
        
        if startdateforbookmark:
            bookmark = u'%s%s' % (title.replace(' ', ''), startdateforbookmark)
            # bookmark = urllib.quote_plus(bookmark.encode(config.charset))
            html = u'<a name="%s"></a>' % bookmark
            self.request.write(formatter.rawHTML(html))
            
        wikiparser = wiki.Parser( lines, self.request )
        wikiparser.format( formatter )

    def outputfootnote(self, lines, title, fromstring, tostring, startdateforbookmark, successflag):
    
        formatter = self.formatter
        
        if tostring:
            fromto = '%s ~ %s' % (fromstring.strip(), tostring.strip())
        else:
            fromto = '%s' % fromstring.strip()

        footnote = u'(Event) %s: %s' % (title, fromto)
        lines = u'%s [[FootNote(%s)]]' % (lines.rstrip(), footnote)
        
        if startdateforbookmark:
            bookmark = u'%s%s' % (title.replace(' ', ''), startdateforbookmark)
            # bookmark = urllib.quote_plus(bookmark.encode(config.charset))
            html = u'<a name="%s"></a>' % bookmark
            self.request.write(formatter.rawHTML(html))
        
        wikiparser = wiki.Parser( lines, self.request )
        wikiparser.format( formatter )
        


def getdatefield(str_date):
    str_year = ''
    str_month = ''
    str_day = ''
    
    if len(str_date) == 6:
        # year+month
        str_year = str_date[:4]
        str_month = str_date[4:]
        str_day = '1'

    elif len(str_date) == 8:
        # year+month+day
        str_year = str_date[:4]
        str_month = str_date[4:6]
        str_day = str_date[6:]
    
    elif len(str_date) == 10:
        # year+?+month+?+day
        str_year = str_date[:4]
        str_month = str_date[5:7]
        str_day = str_date[8:]
    
    else:
        raise ValueError
    
    # It raises exception if the input date is incorrect
    temp = datetime.date(int(str_year), int(str_month), int(str_day))

    return temp.year, temp.month, temp.day


def gettimefield(str_time):
    str_hour = ''
    str_min = ''
    
    if len(str_time) == 4:
        # hour+minute
        str_hour = str_time[:2]
        str_min = str_time[2:]
    
    elif len(str_time) == 5:
        # hour+?+minute
        str_hour = str_time[:2]
        str_min = str_time[3:]
        
    else:
        raise ValueError
    
    # It raises exception if the input date is incorrect
    temp = datetime.time(int(str_hour), int(str_min))

    return temp.hour, temp.minute