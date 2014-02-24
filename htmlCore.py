from core import Game
import cgi
import urllib
import os

def printJSONHeader():
  print "Content-Type: application/json\n\n";

def printHTMLHeader(title=""):
  if title != "":
    title = title + " - "
  print "Content-Type: text/html\n\n";
  print """<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
  <title>%sTable Football Ladder (v2 beta)</title>
  <script src="js/sorttable.js" type="text/javascript"></script>
  <link rel="stylesheet" type="text/css" href="football.css" />
</head>
                                                         
  <body>
""" % (title)

def printHTMLFooter():
  print """
  <hr/>
  <!-- I bloody hate CSS why is this so hard? -->
  <table class="structural" width="100%"><tr><td align="left">&copy;2007 <a href="mailto:aks@corefiling.co.uk">Andrew Shirley</a></td><td id="devLink"><p>Try the development branch at <a href="http://www.int.corefiling.com/~aks/football-dev/football.cgi">http://www.int.corefiling.com/~aks/football-dev/football.cgi</a></p><p>or contribute at <a href="https://github.com/ashirley/football">https://github.com/ashirley/football</a></p></td></tr></table>
  <hr/>
  </body>
</html>
"""

#TODO consider not going too far into the past. This might be more applicable now we have a list of only a players game.
#TODO refactor out len(games)
def showGameList(games, anchorName="RecentGames", headerName="Recent Games", gameListStartParamName="gameListStart"):

  form = cgi.FieldStorage()
  gameListStart = 0
  if form.has_key(gameListStartParamName):
    gameListStart = int(form[gameListStartParamName].value)

  #TODO guard against daft limits 
  if gameListStart > len(games) - 10:
    gameListStart = len(games) - 10

  if gameListStart < 0:
    gameListStart = 0

  print "<h3><a id='%s'></a>%s</h3><table>" %(anchorName, headerName)
  print Game.tableHeadings()

  if len(games) < 10:
    listLength = len(games)
  else:
    listLength = 10
 
  if gameListStart == 0:
    gamesToList = games[-listLength:] #last ten games
  else:
    gamesToList = games[-(listLength + gameListStart): -gameListStart] #ten games before gameStartList

  gamesToList.reverse()

  for game in gamesToList:
    print "   <tr class='%s'>" % game.tableClass(), game.toTableRow(), "</tr>"
  print "  </table>"

  #prev/next links
  if len(games) > 10:
    qs = os.environ["QUERY_STRING"]
    qsDict = cgi.parse_qs(qs)
    
    gamesLeft = len(games) - 10 - gameListStart
    if gamesLeft > 10:
      qsDict[gameListStartParamName] = [gameListStart + 10]
      print "  <a href='?%s#%s'>Prev</a>" % (urlencodeXHTML(qsDict), anchorName)
    elif gamesLeft > 0:
      # we aren't at the start but we shouldn't go back a full 10.
      qsDict[gameListStartParamName] = [len(games) - 10]
      print "  <a href='?%s#%s'>Prev</a>" % (urlencodeXHTML(qsDict), anchorName)
    else:
      # there is none left.
      print "Prev"
  
    print "<span class='navNumInert'>F</span>"
  
    if gameListStart < len(games) - 10:
      #o's for games past of gameListStart
      for i in range(100 + gameListStart, gameListStart, -10):
        if i >= len(games) - 10:
          #this is too far back
          if i < len(games):
            #but only just, put a link to the very end.
            qsDict[gameListStartParamName] = [len(games) - 10]
            print "  <a href='?%s#%s' class='navNumFuture'>o</a>" % (urlencodeXHTML(qsDict), anchorName)
          continue
        else:
          #we can go back farther
          qsDict[gameListStartParamName] = [i]
          print "  <a href='?%s#%s' class='navNumFuture'>o</a>" % (urlencodeXHTML(qsDict), anchorName)
    
    #the current o
    print "<span class='navNumCur'>o</span>"
    
    if gameListStart > 0:
      #o's for games future of gameListStart
      for i in range(gameListStart - 10, gameListStart - 110, -10):
        if i <= 0:
          #this is as far forward as we can go.
          qsDict[gameListStartParamName] = [0]
          print "  <a href='?%s#%s' class='navNumFuture'>o</a>" % (urlencodeXHTML(qsDict), anchorName)
          break
        else:
          #we can go forward farther
          qsDict[gameListStartParamName] = [i]
          print "  <a href='?%s#%s' class='navNumFuture'>o</a>" % (urlencodeXHTML(qsDict), anchorName)
    print "<span class='navNumInert'>tball</span>"
  
    if gameListStart > 10:
      qsDict[gameListStartParamName] = [gameListStart - 10]
      print "<a href='?%s#%s'>Next</a>" % (urlencodeXHTML(qsDict), anchorName)
    elif gameListStart > 0:
      # we aren't at the end but we shouldn't go forward a full 10.
      qsDict[gameListStartParamName] = [0]
      print "<a href='?%s#%s'>Next</a>" % (urlencodeXHTML(qsDict), anchorName)
    else:
      # there is none left.
      print "Next"

#The standard urllib.urlencode spat raw ampersands everywhere (as opposed to &amp;) which fails XHTML validation
def urlencodeXHTML(qsDict):
  query = []
  for qName in qsDict:
    for qVal in qsDict[qName]:
      query.append(qName + "=" + str(qVal))
  return "&amp;".join(query)

def showSquareTable(data):
  """
   Create a table with a cell for each of the items in data. This will create an NxN table where the unused cells are on the right of the bottom row.
  """
  from math import sqrt, ceil
  N = int(ceil(sqrt(len(data))))

  print "<table height='100%' width='100%'>\n"

  for i in range(0, N):
    print "<tr>"
    for j in range(0, N):
      print "<td>"
      try:
        print data[i*N+j]
      except IndexError:
        pass
      print "</td>"
    print "</tr>"
  
  print "</table>"
