from core import Game
import cgi
import urllib
import os

def printHTMLHeader():
  print "Content-Type: text/html\n\n";
  print """
<head>
  <title>Table Football Ladder (v2 beta)</title>
  <script src="js/sorttable.js"></script>
  <link rel="stylesheet" type="text/css" href="football.css" />
</head>
                                                         
  <body>
"""

def printHTMLFooter():
  print """
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

  print "<a name='%s'><h3>%s</h3><table>" %(anchorName, headerName)
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
  print "  </table></td>"

  #prev/next links
  if len(games) > 10:
    qs = os.environ["QUERY_STRING"]
    qsDict = cgi.parse_qs(qs)
    
    gamesLeft = len(games) - 10 - gameListStart
    if gamesLeft > 10:
      qsDict[gameListStartParamName] = gameListStart + 10
      print "  <a href='?%s#%s'>Prev</a>" % (urllib.urlencode(qsDict, True), anchorName)
    elif gamesLeft > 0:
      # we aren't at the start but we shouldn't go back a full 10.
      qsDict[gameListStartParamName] = len(games) - 10
      print "  <a href='?%s#%s'>Prev</a>" % (urllib.urlencode(qsDict, True), anchorName)
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
            qsDict[gameListStartParamName] = len(games) - 10
            print "  <a href='?%s#%s' class='navNumFuture'>o</a>" % (urllib.urlencode(qsDict, True), anchorName)
          continue
        else:
          #we can go back farther
          qsDict[gameListStartParamName] = i
          print "  <a href='?%s#%s' class='navNumFuture'>o</a>" % (urllib.urlencode(qsDict, True), anchorName)
    
    #the current o
    print "<span class='navNumCur'>o</span>"
    
    if gameListStart > 0:
      #o's for games future of gameListStart
      for i in range(gameListStart - 10, gameListStart - 110, -10):
        if i <= 0:
          #this is as far forward as we can go.
          qsDict[gameListStartParamName] = 0
          print "  <a href='?%s#%s' class='navNumFuture'>o</a>" % (urllib.urlencode(qsDict, True), anchorName)
          break
        else:
          #we can go forward farther
          qsDict[gameListStartParamName] = i
          print "  <a href='?%s#%s' class='navNumFuture'>o</a>" % (urllib.urlencode(qsDict, True), anchorName)
    print "<span class='navNumInert'>tball</span>"
  
    if gameListStart > 10:
      qsDict[gameListStartParamName] = gameListStart - 10
      print "<a href='?%s#%s'>Next</a>" % (urllib.urlencode(qsDict, True), anchorName)
    elif gameListStart > 0:
      # we aren't at the end but we shouldn't go forward a full 10.
      qsDict[gameListStartParamName] = 0
      print "<a href='?%s#%s'>Next</a>" % (urllib.urlencode(qsDict, True), anchorName)
    else:
      # there is none left.
      print "Next"
