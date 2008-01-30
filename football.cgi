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
  playerstats = Totals(ladderData.games), Skill(ladderData.games)

  #main table
  print "<form action=\"graphpage.cgi\" method=\"GET\">"
  print "<table class=\"sortable\" id=\"players\">"
  print "<tr>", Player.tableHeadings()
  for stat in playerstats:
      print stat.toTableHeader()
  print "</tr>"

  #data rows
  players = ladderData.getAllPlayers()[:]
  players.sort(lambda x, y: cmp(y.getLastGame().getVar(y.name, "newSkill"), x.getLastGame().getVar(x.name, "newSkill")))

  justPlayedList = form.getlist('justPlayed')
  #TODO rewrite this if!
  if len(justPlayedList) == 0:
    if form.has_key("redplayer"):
      justPlayedList = [form['redplayer'].value, form['blueplayer'].value]

  for player in players:
    if player.name in justPlayedList:
      print "   <tr class='justPlayed'>"
    else:
      print "   <tr>"
      
    print player.toTableRow()
    for stat in playerstats:
        print stat.toTableRow(player)
    print "</tr>"
    
  print "<tr><td class='structural'/><td class='structural'><input type=\"submit\" value=\"Graph\" /></td>"
  print "</table>"
  print "</form>"

  #highest and lowest ever skill.
  highestSkill = 0.0
  lowestSkill = 0.0

  for game in ladderData.games:
    blueSkill = game.getVar(game.blue, "newSkill")
    if blueSkill >= highestSkill:
      highestSkill = blueSkill
      highestSkillPlayer = game.blue
      highestSkillTime = game.time
    if blueSkill <= lowestSkill:
      lowestSkill = blueSkill
      lowestSkillPlayer = game.blue
      lowestSkillTime = game.time

    redSkill = game.getVar(game.red, "newSkill")
    if redSkill >= highestSkill:
      highestSkill = redSkill
      highestSkillPlayer = game.red
      highestSkillTime = game.time
    if redSkill <= lowestSkill:
      lowestSkill = redSkill
      lowestSkillPlayer = game.red
      lowestSkillTime = game.time

  print """<table><tr><th></th><th>Player</th><th>Skill</th><th>Date</th></tr>
  <tr><td>Highest ever skill</td><td><a href='player.cgi?name=%(highestPlayer)s'>%(highestPlayer)s</a></td><td>%(highestScore).3f</td><td>%(highestDate)s</td></tr>
  <tr><td>Lowest ever skill</td><td><a href='player.cgi?name=%(lowestPlayer)s'>%(lowestPlayer)s</a></td><td>%(lowestScore).3f</td><td>%(lowestDate)s</td></tr>
  </table>
  """ % {
    "highestPlayer" : highestSkillPlayer ,
    "highestScore" : highestSkill, 
    "highestDate" : formatTime(highestSkillTime), 
    "lowestPlayer" : lowestSkillPlayer ,
    "lowestScore" : lowestSkill, 
    "lowestDate" : formatTime(lowestSkillTime), 

  }


  # remove speculative games link
  if len(speculativeGames) > 0:
    qs = cgi.parse_qs(os.environ["QUERY_STRING"])
    removeKey(qs, 'oldSpeculativeGames')
    removeKey(qs, 'redplayer')
    removeKey(qs, 'blueplayer')
    removeKey(qs, 'redscore')
    removeKey(qs, 'bluescore')
    
    print "<p class='speculativeGameRemoval'><a href='?%s'>remove Speculative Games</a></p>" % urllib.urlencode(qs, True)


  print "<hr /><table class='structural'>"

  #add a real game
  print """<tr><td>
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
    </td>
    <td>
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
    </td></tr>
    """ % (",".join(speculativeGames), ",".join(speculativeGames))


  #recent games
  print "<tr><td>"
  showGameList(ladderData.games)
  print "</td><td>"

  #recent significant games
  showGameList(
    [game for game in ladderData.games if game.isSignificant()],
    anchorName="RecentSignificantGames",
    headerName="Recent Significant Games",
    gameListStartParamName="significantGameListStart"
  )
  print "</td></tr>"

  print "</table>"

  #most significant ever.

  mostSignificantChange = 0.0
  for game in ladderData.games:
    
    changeToBlue = game.getVar(game.blue, "skillChangeTo") 
    if changeToBlue > mostSignificantChange:
      mostSignificantChange = changeToBlue
      mostSignificantGame = game

    changeToRed = game.getVar(game.red, "skillChangeTo") 
    if changeToRed > mostSignificantChange:
      mostSignificantChange = changeToRed
      mostSignificantGame = game

  print "<h3>Most Significant ever</h3>"
  print "<table>"
  print Game.tableHeadings()
  print "<tr class='%s'>" % mostSignificantGame.tableClass(), mostSignificantGame.toTableRow(), "</tr>"
  print "</table>"


  printHTMLFooter()

def removeKey(dict, key):
  if key in dict: del dict[key]

main()
