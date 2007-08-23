#! /usr/bin/python
import cgi
import cgitb; cgitb.enable()

from core import *
from htmlCore import *

import urllib

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
    
  ladderData = parseLadderFiles(speculativeGames)

  #mark all of the speculative games as such
  if len(speculativeGames) > 0:
    for game in ladderData.games[-len(speculativeGames):]:
      game.speculative=True

  #setup all the objects which can give us statistics for a player
  from playerstats import Totals, Skill
  playerstats = Totals(ladderData), Skill(ladderData)

  #start table
  print "<form action=\"graphpage.cgi\" method=\"GET\">"
  print "<table class=\"sortable\" id=\"players\">"
  
  #headers
  print "<tr>", Player.tableHeadings()
  for stat in playerstats:
      print stat.toTableHeader()
  print "</tr>"

  #data rows
  players = ladderData.getAllPlayers()[:]
  players.sort(lambda x, y: cmp(y.getLastGame().getVar(y.name, "newSkill"), x.getLastGame().getVar(x.name, "newSkill")))
  for player in players:
    print "   <tr>",player.toTableRow()
    for stat in playerstats:
        print stat.toTableRow(player)
    print "</tr>"
    
  print "</table>"
  print "<input type=\"submit\" value=\"Graph\" />"
  print "</form>"

  #significant games
  #ladderData.games
  #significantGames [ game for game in ladderData.games when ]
  significantGames = []
  games = ladderData.games[:]
  games.reverse()
  for game in games:
    if (game.getVar(game.red, "skillChangeTo") > 7.5):
      significantGames.append(game)

    if len(significantGames) > 10:
      break

  # remove speculative games link
  if len(speculativeGames) > 0:
    qs = cgi.parse_qs(os.environ["QUERY_STRING"])
    removeKey(qs, 'oldSpeculativeGames')
    removeKey(qs, 'redplayer')
    removeKey(qs, 'blueplayer')
    removeKey(qs, 'redscore')
    removeKey(qs, 'bluescore')
    
    print "<p><a href='?%s'>remove Speculative Games</a></p>" % urllib.urlencode(qs, True)

  #recent games
  showGameList(ladderData.games)

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
    <form method="GET" action="" class="speculativeGameEntry">
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

def removeKey(dict, key):
  if key in dict: del dict[key]

main()
