from core import Game
import cgi

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

def showGameList(games, anchorName="RecentGames", headerName="Recent Games", gameListStartParamName="gameListStart"):

  form = cgi.FieldStorage()
  gameListStart = 0
  if form.has_key("gameListStart"):
    gameListStart = int(form['gameListStart'].value)

  print "<a name='%s'><h3>%s</h3><table>" %(anchorName, headerName)
  print Game.tableHeadings()
 
  if gameListStart == 0:
    gamesToList = games[-10:] #last ten games
  else:
    gamesToList = games[-(10 + gameListStart): -gameListStart] #ten games before gameStartList

  gamesToList.reverse()

  for game in gamesToList:
    cssClass=game.tableClass()
    print "   <tr class='%s'>" % cssClass, game.toTableRow(), "</tr>"
  print "  </table></td>"

  #prev/next links

  #TODO preserve other get params.
  print "  <a href='?%s=%d#%s'>Prev</a>" % (gameListStartParamName, (gameListStart + 10), anchorName)
#  print "F"
#  for i in range(10):
#    print "  <a href=''>o</a>"
#  print "tball"
  if gameListStart > 10:
    print "<a href='?%s=%s#%s'>Next</a>" % (gameListStartParamName, (gameListStart - 10), anchorName)
  elif gameListStart > 0:
    print "<a href='?%s=0#%s'>Next</a>" % (gameListStartParamName, anchorName)
  else:
    print "Next"




