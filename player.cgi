#! /usr/bin/python
import cgi
import cgitb; cgitb.enable()

from core import *
from htmlCore import *

def main():
  form = cgi.FieldStorage()
  if form.has_key("name"):
    name = form['name'].value
  else:
    printHTMLHeader("Error")
    print "<h1>Error</h1><p>You must supply a name parameter</p>"
    printHTMLFooter()
    return

  ladderData = parseLadderFiles()
  player = ladderData.getPlayer(name)

  if not player:
    printHTMLHeader("Error")
    print "<h1>Error</h1><p>You must supply a name parameter which matches a non-excluded person who has played a game.</p>"
    printHTMLFooter()
    return

  printHTMLHeader("Player " + name)
  print "<H1>The Table Football Ladder for %s</H1>" % name

  #setup all the objects which can give us statistics for a player
  from playerstats import Totals, Skill
  playerstats = Totals(ladderData), Skill(ladderData)

  #recent games
  showGameList(player.games)


  print "<h2>Graph</h2>"
  print "<a href='graphpage.cgi?name=%s'><img src='graph.cgi?name=%s' /></a>" % (name, name)

  printHTMLFooter()

main()
