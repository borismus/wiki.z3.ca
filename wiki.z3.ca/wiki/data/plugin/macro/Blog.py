"""
MoinMoin - Blog macro

(c) 2003 Mark Proctor, athico.com

(c) 2006 Carsten Grohmann

Overview
========
This is a simply Blog macro that utilises a javascript calendar and the
Include macro to hack together a pseudo bwiki (blog/wiki).
The calendar is used to choose the entries to show, the number of visible
entries is controlled by the select control "max entries".
The button to the left of "max entries" allows you to toggle between the
two modes "Show All" and "Show Published".
 -  "Show Published" only shows those days that contain entries up to the
    given "max entries", from the chosen calendar date.
 -  "Show All" Show all the dates, previous to the chosen calendar date,
     up to a maximum of "max entries".
     
     This is the mode you will need to use to enter new blog entries

Dependencies
============
 - C{Include}

To install
==========
 - Save this macro in your macros directory

To Use
======
 - C{<date>}       : in the format of yyyy-mm-dd
 - C{<showAll>}    : 1 or 0, where 1 shows all and 0 shows published
 - C{<entries>}    : the maximum visible number of entries
 - C{<maxEntriesInOptionList>} : the maximum value that C{<entries>} can be, this is used to restrict the web gui
 - C{<startDay>}   : The start Day for the calendar
   - values      : C{Su}, C{Mo}, C{Tu}, C{We}, C{Th}, C{Fr}, C{Sa}

Defaults Values
===============
 - C{<date>}                    : C{today}
 - C{<showAll>}                 : C{0}
 - C{<entries>}                 : C{5}
 - C{<maxEntriesInOptionList>}  : C{20}
 - C{<startDay>}                : C{Mo}

Example::
  [[Blog[<date>, <showAll>, <entries>, <maxEntriesInOptionList>]]
  [[Blog(, 1, 7)]] - Shows all days, up to 7 days, from todays date.
  [[Blog(2003-05-23, 0, 5)]] - Shows upto 5 published entries from the given date.
  [[Blog( , , , 10)]] - Shows upto 5(default) published(default) entries from todays date(default), but does not allow the user to speficy max entries to be more than 10.
  [[Blog( , , , , We)]] - Shows upto 5(default) published(default) entries from todays date(default), maxEntriesInOptionList(20) with start calendar  day Wednesday.
  [[Blog(2003-05-23, 0, 5, ,Sa)]] - Shows upto 5 published entries from the given date, with start calendar day Saturday

$Id: Blog.py,v 1.4 2006/06/15 17:39:04 carsten Exp $

@license: Licensed under GNU GPL - see COPYING for details.
@version: 1.1
@var re_entries: Precompiled regular expression to match the entries option
@var re_date:    Precompiled regular expression to match the date option
"""

from MoinMoin.Page import Page
import datetime, re
import MoinMoin.macro.Include

Dependencies = []

# compile regular expressions once at start time
re_entries=re.compile(r'(?P<entries>\d+)')
re_date=re.compile(r'(?P<year>\d\d\d\d)-(?P<month>\d?\d)-(?P<day>\d?\d)')

class Blog:
    """
    This macro provides an html based blog for MoinMoin.

    Blog entries are per day possible and named like the day
    
    @cvar calendarHTML:   HTML code of the calendar part
    @cvar cssStyle:       The CSS declaration
    @cvar errorMessage:   Preformatted html error message
    @cvar headingLevel:   The level of depth of the heading of missing pages
    @cvar inputHeader:    Header of the html imput form
    @cvar javaScriptFunctions: Set of java script function to have a
                               more comfortable use of the blog calendar
    @cvar oneDay:         Timedelta object with one day length

    @ivar macro:          Reference to the macro instance
    @ivar maxEntriesInOptionList: Maximum numbers of entries in the option list
    @ivar re_blogEntries: Page specific regular expression to catch all blog
                          entries (subpages)
    @ivar startDay:       First day of the week; valid values are
                          "Su", "Mo", "Tu", "We", "Th", "Fr", "Sa"
    @ivar showAll:        Integer flag to show all entries or the existing only
    @ivar text:           The macro arguments
    @ivar thisPageName:   The of the current page
    """

    calendarHTML = """
        <TABLE CELLPADDING=0 CELLSPACING=0 BORDER=0 >
            <TR><TD>
              <CENTER>
              <FORM NAME="calControl" onsubmit="return false;" >
                <SELECT class="calendarButton" NAME="month" onchange="selectDate()">
                  <OPTION>January</OPTION>
                  <OPTION>February</OPTION>
                  <OPTION>March</OPTION>
                  <OPTION>April</OPTION>
                  <OPTION>May</OPTION>
                  <OPTION>June</OPTION>
                  <OPTION>July</OPTION>
                  <OPTION>August</OPTION>
                  <OPTION>September</OPTION>
                  <OPTION>October</OPTION>
                  <OPTION>November</OPTION>
                  <OPTION>December</OPTION>
                </SELECT>
                <INPUT NAME="year" class="calendarButton" TYPE=TEXT SIZE=4 MAXLENGTH=4>
                <INPUT TYPE="button" class="calendarButton" NAME="Go" value="Update Year" onClick="selectDate()">
              </FORM>
              </CENTER>
            </TD></TR>
            <TR><TD id="calendar" align="center" onsubmit="return false;" ></TD></TR>
	    <TR><TD>
	      <CENTER>
              <FORM NAME="calButtons">
                <INPUT class='calendarButton' TYPE=BUTTON NAME="previousYear" VALUE=" <<  "    onClick="setPreviousYear()">
                <INPUT class='calendarButton' TYPE=BUTTON NAME="previousYear" VALUE="  <  "    onClick="setPreviousMonth()">
                <INPUT class='calendarButton' TYPE=BUTTON NAME="previousYear" VALUE="Today"    onClick="setToday()">
                <INPUT class='calendarButton' TYPE=BUTTON NAME="previousYear" VALUE="  >  "    onClick="setNextMonth()">
                <INPUT class='calendarButton' TYPE=BUTTON NAME="previousYear" VALUE="  >> "    onClick="setNextYear()">
	      </FORM>
              </CENTER>
	    </TD></TR>
        </TABLE>
        <script>
         onload=function() {
            var date = global.date.split("-");
            document.calControl.month.selectedIndex = date[1]-1;
            document.calControl.year.value = date[0];
            makeCalendar();
            updateCalendar(date[1]-1, date[0]);
         };
        </script>
        """

    cssStyle = """
        <style type="text/css">
            .calendarButton {
                font-size:10;
                cursor:pointer;
                cursor:hand;
            }

            .calendarHeader {
                background-color:#C0DED1;
                font-size:12;
                text-decoration:none;
                cursor:pointer;
                cursor:hand;
            }
        
            .calendarValue {
                background-color:#FDFAD1;
                font-size:10;
                font-color:black;
                cursor:pointer;
                cursor:hand;
            }
        
            .calendarValueSelected {
                background-color:#FD0000;
                font-size:10;
                font-color:black;
                cursor:pointer;
                cursor:hand;
            }
        </style>
        """
        
    errorMessage = '<p><strong class="error">%s</strong></p>'

    headingLevel = 1

    inputHeader =  """
    <input class='calendarButton' type=button value='%s' onclick='global.showAll=%s;updateBlog();'>
    max entries:
    <select class='calendarButton'
    onchange='if (this.value&&(this.value != "")) {global.entries=this.value;  updateBlog();}'>
    """

    javaScriptFunctions  = """
<script>

var global = {};
global.page = "%s";
global.date = "%s";
global.entries = "%s";
global.showAll = "%s";

global.daysLookup = {"Su":0, "Mo":1, "Tu":2, "We":3, "Th":4, "Fr":5, "Sa":6};
global.days = ["Su", "Mo", "Tu", "We", "Th", "Fr", "Sa"];
global.startDay = "%s";

function gotoDate() {
    if (!this.date) return;
    global.date = this.date;
    updateBlog();
}

function updateBlog() {
    window.location.href = "/"+global.page+"?date="+global.date+"&entries="+global.entries+"&showAll="+global.showAll
}

function setToday() {
    var now   = new Date();
    var day   = now.getDate();
    var month = now.getMonth();
    var year  = now.getYear();
    if (year < 2000)    // Y2K Fix, Isaac Powell
    year = year + 1900; // http://onyx.idbsu.edu/~ipowell
    this.focusDay = day;
    document.calControl.month.selectedIndex = month;
    document.calControl.year.value = year;
    updateCalendar(month, year);
}

function isFourDigitYear(year) {
    if (year.length != 4) {
        alert ("Sorry, the year must be four-digits in length.");
        document.calControl.year.select();
        document.calControl.year.focus();
        return false;
    } else {
        return true;
    }
}

function selectDate() {
    var year  = document.calControl.year.value;
    if (isFourDigitYear(year)) {
        var day   = 0;
        var month = document.calControl.month.selectedIndex;
        updateCalendar(month, year);
    }
}

function setPreviousYear() {
    var year  = document.calControl.year.value;
    if (isFourDigitYear(year)) {
        var day   = 0;
        var month = document.calControl.month.selectedIndex;
        year--;
        document.calControl.year.value = year;
        updateCalendar(month, year);
   }
}
function setPreviousMonth() {
    var year  = document.calControl.year.value;
    if (isFourDigitYear(year)) {
        var day   = 0;
        var month = document.calControl.month.selectedIndex;
        if (month == 0) {
            month = 11;
            if (year > 1000) {
                year--;
                document.calControl.year.value = year;
            }
        } else {
            month--;
        }
        document.calControl.month.selectedIndex = month;
        updateCalendar(month, year);
   }
}
function setNextMonth() {
    var year  = document.calControl.year.value;
    if (isFourDigitYear(year)) {
        var day   = 0;
        var month = document.calControl.month.selectedIndex;
        if (month == 11) {
            month = 0;
            year++;
            document.calControl.year.value = year;
        } else {
            month++;
        }
        document.calControl.month.selectedIndex = month;
        updateCalendar(month, year);
   }
}
function setNextYear() {
    var year = document.calControl.year.value;
    if (isFourDigitYear(year)) {
        var day = 0;
        var month = document.calControl.month.selectedIndex;
        year++;
        document.calControl.year.value = year;
        updateCalendar(month, year);
   }
}

function makeCalendar() {
    var cal = document.getElementById("calendarTbody");
    if (cal) return;
    var i;
    var table = document.createElement("table");
    table.style.cssText = "border-left:1px solid black; border-top:1px solid black";
    table.cellSpacing = 0;
    table.cellPadding = 2;
    var thead = document.createElement("thead");

    var cell;
    var row = document.createElement("tr");

    var titleDays = [];
    var startDay = global.daysLookup[global.startDay];

    for (i=startDay;i<7;i++) {
        titleDays.push(global.days[i]);
    }

    for (i=0;i<startDay;i++) {
        titleDays.push(global.days[i]);
    }

    for  (i=0;i<titleDays.length;i++) {
        cell = document.createElement("td");
        cell.style.cssText = "border-right:1px solid black; border-bottom:1px solid black";
        cell.className = "calendarHeader";
        cell.innerHTML =  titleDays[i];
        row.appendChild(cell);
    }
    thead.appendChild(row);
    table.appendChild(thead);

    var tbody = document.createElement("tbody");
    tbody.id = "calendarTbody";
    row = document.createElement("tr");
    for (i=0; i<42; i++)  {
        if ( i%%7 == 0 ) { //start new line
            tbody.appendChild(row);
            row = document.createElement("tr");
        }
        cell = document.createElement("td");
        cell.className = "calendarValue";
        cell.style.cssText = "border-right:1px solid black; border-bottom:1px solid black";
        cell.innerHTML = "&nbsp;";
        cell.date = null;
        cell.onclick = gotoDate
        row.appendChild(cell);
    }
    tbody.appendChild(row);
    table.appendChild(tbody);

    var  calendar = document.getElementById("calendar");
    calendar.appendChild(table);
}

function updateCalendar(month, year) {
    month = parseInt(month);
    year = parseInt(year);
    var i = 0;
    var days = getDaysInMonth(month+1,year);
    var startDay = global.daysLookup[global.startDay];
    var firstOfMonth = new Date (year, month, 1).getDay();
    var startingPos =  (firstOfMonth >= startDay) ? firstOfMonth - startDay : 7 - (startDay - firstOfMonth);
    days += startingPos;

    var cal = document.getElementById("calendarTbody");

    var cells = cal.getElementsByTagName("td");
    var cell;
    for (i = 0; i < startingPos; i++) {
        cell = cells[i];
        cell.innerHTML = "&nbsp;";
        cell.date = null;
        cell.className = "calendarValue";
    }

    var value;
    month++;
    if (month<10) month = "0" + month;
    date = year+"-"+month+"-";
    for (i = startingPos; i < days; i++) {
        cell = cells[i];
        value = "";
        value = i-startingPos+1;
        if (value < 10) value = "0" + value;
        cell.date = year+'-'+(month)+'-'+value;
        cell.innerHTML = value;
        if (global.date != date+value) cell.className = "calendarValue";
        else cell.className = "calendarValueSelected";
    }

    for (i = days; i < 42; i++) {
        cell = cells[i];
        cell.date = null;
        cell.className = "calendarValue";
        cell.innerHTML = "&nbsp;";
    }
}

function getDaysInMonth(month,year)  {
    var days;
    if (month==1 || month==3 || month==5 || month==7 || month==8 || month==10 || month==12)  days=31;
    else if (month==4 || month==6 || month==9 || month==11) days=30;
    else if (month==2)  {
        if (isLeapYear(year)) { days=29; }
        else { days=28; }
    }
    return (days);
}

function isLeapYear (Year) {
    if (((Year %% 4)==0) && ((Year %% 100)!=0) || ((Year %% 400)==0)) {
    return (true);
    } else { return (false); }
}
</script>
"""

    oneDay = datetime.timedelta(days = 1)

    def __init__(self, macro, text):
        """
        Constructor to initialise this class with default values

        @param macro: Instance of the class Macro
        @param text:  The macro arguments
        """
        self.macro = macro
        self.text = text
        self.thisPageName = self.macro.formatter.page.page_name

        # set default values
        self.maxEntriesInOptionList = 20
        self.startDay = "Mo"
        self.showAll = "0"

        # compile regular expression to catch own sub pages
        self.re_blogEntries = re.compile(
            r'^%s/'                                                  # parent page
            r'BlogEntry-'
            r'(?P<year>\d{4,4})-(?P<month>\d{2,2})-(?P<day>\d{2,2})' # date of the entry
            % self.thisPageName ).match
        
    def dispatch(self):
        """
        Main function

        Process all stuff and format the content
        """
        
        #get incoming macro args, else set to []
        if self.text:
            args = self.text.split(",")
        else:
            args = []
    
        #remove all leading and trailing spaces
        args = map(lambda line: line.strip(), args)
    
        #set date
        if self.macro.form.has_key('date'):
            date = self.macro.form['date'][0]
        elif (len(args) > 0) and (args[0]):
            date = args[0]
        else:
            date = ""
    
        #set showAll
        if self.macro.form.has_key('showAll'):
            self.showAll = self.macro.form['showAll'][0]
        elif (len(args) > 1) and (args[1]):
            self.showAll = args[1]
    
        #set entries
        if self.macro.form.has_key('entries'):
            self.entries = self.macro.form['entries'][0]
        elif (len(args) > 2) and (args[2]):
            self.entries = args[2]
        else:
            self.entries = None
    
        #set max entries
        if (len(args) > 3) and (args[3]):
            self.maxEntriesInOptionList = int(args[3])
            if self.maxEntriesInOptionList < 0:
                self.maxEntriesInOptionList = 20

        #set start day
        if (len(args) > 4) and (args[4]):
            self.startDay = args[4]
    
        #set the number of visible entries
        if self.entries:
            args = re_entries.match(self.entries)
            if not args:
                return (self.errorMessage %('Invalid entries "%s"!')) % (self.macro.form['beforeDate'][0])
            self.entries = int(self.macro.form['entries'][0])
            if self.entries > self.maxEntriesInOptionList:
                self.entries = self.maxEntriesInOptionList
            if self.entries < 0:
                self.entries = 5
        else:
            self.entries = 5
    
        # get the date
        if not date == "":
            args = re_date.match(date)
            if not args:
                return (self.errorMessage %('Invalid date "%s"!')) % (self.macro.form['date'][0])
            try:
                self.blogDate = datetime.date(
                       int(args.group('year')),
                      int(args.group('month')),
                      int(args.group('day'))
                      )
            except ValueError:
                self.blogDate = datetime.date.today()
        else:
            self.blogDate = datetime.date.today()
    
        content  = self.getCSSStyle()
        content += self.getJavaScript()
        content += self.getCalendar()
    
        # get the entries to display
        if (self.showAll == '1'):
            content += self.getShowAll()
        else:
            content += self.getShowEntered()
    
        return content

    def getCalendar(self):
        """"
        Returns the calendar HTML block

        @see: L{self.calendarHTML}
        """
        return self.calendarHTML

    def getCSSStyle(self):
        """
        Returns the CSS declaration

        @see: L{self.cssStyle}
        """
        return self.cssStyle

    def getJavaScript(self):
        """
        Returns the java script code of all calendar functions

        @see: L{self.javaScriptFunctions}
        """

        return self.javaScriptFunctions %  (
            self.thisPageName,
            "%d-%02d-%02d" % (
                self.blogDate.year,
                self.blogDate.month,
                self.blogDate.day
                ),
            self.entries,
            self.showAll,
            self.startDay)

    def getShowAll(self):
        """
        Shows the existing entries and link to non-existing pages
        """

        entryDate = self.blogDate
        formatter = self.macro.formatter
        
        content = []
        content.append(self.inputHeader % ("Show Published", "0"))
        content.append(self._createMaxEntriesOptionList())

        for i in range(self.entries):
            entryTitle = '%d-%02d-%02d' % (
                entryDate.year,
                entryDate.month,
                entryDate.day
                )
            fullEntryPath = '%s/BlogEntry-%s' % (
                self.thisPageName,
                entryTitle
                )

            # we need this only to check the existence of a page
            dummyPage = Page(self.macro.request, fullEntryPath, formatter = formatter)

            # include existing pages using the Include() macro
            if dummyPage.exists():
                content.append(MoinMoin.macro.Include.execute(
                    self.macro,
                    '%s, "%s", 1' % (
                        fullEntryPath,
                        entryTitle
                    )))
            else:
                # create an heading for the empty page
                content.append(
                    formatter.heading(1, self.headingLevel) +
                    formatter.pagelink(1, fullEntryPath, generated=1) +
                    formatter.text(entryTitle) +
                    formatter.pagelink(0,fullEntryPath) +
                    formatter.heading(0, self.headingLevel)
                )

            # decrease date
            entryDate -= self.oneDay
            
        return "\n".join(content)

    def getShowEntered(self):
        """
        Shows the existing entries only.

        @note: This function uses the Include macro.
        @return: HTML page as string
        """
        content = []
        content.append(self.inputHeader % ("Show All", "1"))
        content.append(self._createMaxEntriesOptionList())
    
        # use precompiled regular expression to found all children
        child_page_list = self.macro.request.rootpage.getPageList(
            filter = self.re_blogEntries
            )
        
        child_page_list.sort()
        child_page_list.reverse()
        selectedDate = int( "%d%02d%02d" % (
            self.blogDate.year,
            self.blogDate.month,
            self.blogDate.day))
        pageCount = 0

        # process all child pages
        for pageName in child_page_list:

            # extract date from pagename
            formattedDate = pageName[-10:]

            pageDate = int("%s%s%s" % (
                formattedDate[:4],
                formattedDate[5:7],
                formattedDate[8:10]
                ))

            # skip too young pages
            if (pageDate > selectedDate):
                continue

            # include child page
            includeParams = """%s, "%s", 1""" % (pageName, formattedDate)
            content.append(MoinMoin.macro.Include.execute(self.macro, includeParams))

            # leave loop on maximum number of pages to show
            pageCount += 1
            if (pageCount  >= self.entries):
                break
                
        return "\n".join(content)

    def _createMaxEntriesOptionList(self):
        """
        Creates an html option list to select the number of entries that will be shown

        @return: Option list as string
        """
        # open option list
        content = """<option value=''>--Entries--</option>"""

        # create an entry for each value till maxEntriesInOptionList and make the current as selected
        for i in xrange(1, self.maxEntriesInOptionList +1):
            if i == self.entries:
                selected = "selected"
            else:
                selected = ""
            content += '<option %s value="%d">%d</option>' % (selected, i, i)

        # add closing tag
        content += "</select>"

        return content

def execute(macro, args):
    """
    Execute macro
    """

    return Blog(macro, args).dispatch()
