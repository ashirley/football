#! /usr/bin/python
import cgi
import cgitb; cgitb.enable()

from core import *
from htmlCore import *

def main():
  printHTMLHeader()
  print "<H1>The Table Football Ladder</H1>"

  oldSpeculativeGames = []

  form = cgi.FieldStorage()
  if form.has_key("oldSpeculativeGames"):
    oldSpeculativeGames = str(form['oldSpeculativeGames'].value).split(",")

  
  speculativeGames = oldSpeculativeGames

  #TODO check that all these are present
  if form.has_key("redplayer"):
    from time import time
    speculativeGames.append("%s %s %s %s %s" % (form['redplayer'].value, form['redscore'].value, form['blueplayer'].value, form['bluescore'].value,time()))
    
  # remove speculative games link
  if len(speculativeGames) > 0:
    #TODO keep other params
    print "<a href='?'>remove Speculative Games</a>"


  games, players = parseLadderFiles()

  #mark all of the speculative games as such
  if len(speculativeGames) > 0:
    for game in games[-len(speculativeGames):]:
      game.speculative=True

  #setup all the objects which can give us statistics for a player
  from playerstats import Totals, Skill
  playerstats = Totals(games), Skill(games)

  #start table
  print "<table class=\"sortable\" id=\"players\">"
  
  #headers
  print "<tr>", Player.tableHeadings()
  for stat in playerstats:
      print stat.toTableHeader()
  print "</tr>"

  #data rows
  players._players.sort(lambda x, y: cmp(x.getLastGame().getVar(x.name, "newSkill"), y.getLastGame().getVar(y.name, "newSkill")))
  for player in players._players:
    print "   <tr>",player.toTableRow()
    for stat in playerstats:
        print stat.toTableRow(player)
    print "</tr>"
    

  print "  </table>"
  

  #recent games
  showGameList(games)

  #add a real game

  print """
    <hr />
    <form method="GET" action="ladderEdit.cgi">
      <h3>Add a game:</h3>
      <table>
        <tr>
          <th/>
          <th>Name</th>
          <th>Score</th>
        </tr>
        <tr>
          <th class='redHeader'>Red Player</th>
          <td><input type="text" name="redplayer" value=""/></td>
          <td><input type="text" name="redscore" value=""/></td>
        </tr>
        <tr>
          <th class='blueHeader'>Blue Player</th>
          <td><input type="text" name="blueplayer" value=""/></td>
          <td><input type="text" name="bluescore" value=""/></td>
        </tr>
      </table>
      <input type="hidden" name="oldSpeculativeGames" value="%s" />
      <input type="submit" value="Submit"/>
    </form>
""" % ",".join(speculativeGames)

  #add a speculative game

  print """
    <form method="GET" action="">
      <h3>Add a Speculative game:</h3>
      <table>
        <tr>
          <th/>
          <th>Name</th>
          <th>Score</th>
        </tr>
        <tr>
          <th class='redHeader'>Red Player</th>
          <td><input type="text" name="redplayer" value=""/></td>
          <td><input type="text" name="redscore" value=""/></td>
        </tr>
        <tr>
          <th class='blueHeader'>Blue Player</th>
          <td><input type="text" name="blueplayer" value=""/></td>
          <td><input type="text" name="bluescore" value=""/></td>
        </tr>
      </table>
      <input type="hidden" name="oldSpeculativeGames" value="%s" />
      <input type="submit" value="Submit"/>
    </form>
""" % ",".join(speculativeGames)

  printHTMLFooter()

main()
