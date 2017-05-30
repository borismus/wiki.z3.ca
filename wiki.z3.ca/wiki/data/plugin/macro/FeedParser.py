import feedparser

Dependencies = []

def execute(macro, args):
    url = args
    feed = feedparser.parse(url )

    if feed.has_key("channel"):
       mylink = feed["channel"].get("link", "No link")
       mytitle = feed["channel"].get("title", "No title")
       output = "<h1><a href=\"" + mylink + "\">" + feed.version + " Feed: " + mytitle + "</a></h1>"
    else:
       output = "<h1>" + feed.version + " Feed: No channel</h1>"

    if feed.has_key("items"):
       items = feed["items"]
       for item in items:
          mytitle = item.get("title", "")
          mysummary = item.get("summary", "")
          if item.has_key("link"):
             output = output + "\n<p><a href=\""+ item["link"] + "\">"+ mytitle + "</a>"
          else:
             output = output + "\n<p>" + mytitle
          output = output + " "+ mysummary + "</p>"
    else:
       output = output + "\n<p>No items</p>"

    return output
