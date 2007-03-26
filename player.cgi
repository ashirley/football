#! /usr/bin/python
import cgi
import cgitb; cgitb.enable()

from core import *
from htmlCore import *

def main():
  printHTMLHeader()

  form = cgi.FieldStorage()
  if form.has_key("name"):
    name = form['name'].value
  else:
    print "<h1>Error</h1><p>You must supply a name parameter</p>"
    printHTMLFooter()
    return

  print "<H1>The Table Football Ladder for %s</H1>" % name

  games, players = parseLadderFiles()
  player = players.get(name)

  if not player:
    print "<h1>Error</h1><p>You must supply a name parameter which matches a non-excluded person who has played a game.</p>"
    printHTMLFooter()
    return


  #setup all the objects which can give us statistics for a player
  from playerstats import Totals, Skill
  playerstats = Totals(games), Skill(games)

  #recent games
  showGameList(player.games)

  printHTMLFooter()


main()
