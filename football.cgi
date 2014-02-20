#! /usr/bin/python
import cgi
import cgitb; cgitb.enable()

from core import *
from htmlCore import *

import urllib

def main():
  form = cgi.FieldStorage()

  #Check for a submission of a real game.
  #TODO check that all these are present
  if form.has_key("redplayer"):
    from time import time
    with open("ladder.txt", "a") as datafile:
      datafile.write("\n%s %s %s %s %.0f" % (form['redplayer'].value, form['redscore'].value, form['blueplayer'].value, form['bluescore'].value, time()))

  #Check for a submission of a speculative game
  oldSpeculativeGames = []

  if form.has_key("oldSpeculativeGames"):
    oldSpeculativeGames = str(form['oldSpeculativeGames'].value).split(",")

  
  speculativeGames = oldSpeculativeGames

  #TODO check that all these are present
  if form.has_key("specredplayer"):
    from time import time
    speculativeGames.append("%s %s %s %s %s" % (form['specredplayer'].value, form['specredscore'].value, form['specblueplayer'].value, form['specbluescore'].value,time()))
  

  #Parse the data and show the page
  ladderData = parseLadderFiles(speculativeGames)

  #mark all of the speculative games as such
  if len(speculativeGames) > 0:
    for game in ladderData.games[-len(speculativeGames):]:
      game.speculative=True

  #setup all the objects which can give us statistics for a player
  from playerstats import Totals, Skill
  playerstats = Totals(ladderData.games), Skill(ladderData.games)

  if form.has_key("redplayer") and form.has_key("jsonResponse"):
    # Put out a json response if we have just submitted a game and it was specifically requested.
    lastGame = ladderData.games[-1]
    printJSONHeader()
    print """
{
  "red" : {
    "name" : "%(redName)s",
    "score" : %(redScore)s,
    "skillChange" : %(redSkillChange)s
  },
  "blue" : {
    "name" : "%(blueName)s",
    "score" : %(blueScore)s,
    "skillChange" : %(blueSkillChange)s
  }
}""" % {"redName":lastGame.red, "redScore":lastGame.redScore, "redSkillChange":lastGame.getVar(lastGame.red, "skillChangeTo"), "blueName":lastGame.blue, "blueScore":lastGame.blueScore, "blueSkillChange":lastGame.getVar(lastGame.blue, "skillChangeTo")}
    return
        

  printHTMLHeader()
  print "<h1>The Table Football Ladder</h1>"

  #main table
  print "<form action=\"graphpage.cgi\" method=\"get\">"
  print "<table class=\"sortable\" id=\"players\">"
  print "<tr>", Player.tableHeadings()
  for stat in playerstats:
      print stat.toTableHeader()
  print "</tr>"

  #data rows
  players = ladderData.getAllUnexcludedPlayers()
  players.sort(lambda x, y: cmp(y.getLastGame().getVar(y.name, "newSkill"), x.getLastGame().getVar(x.name, "newSkill")))

  justPlayedList = form.getlist('justPlayed')
  if len(justPlayedList) == 0 and form.has_key("specredplayer"):
    justPlayedList = [form['specredplayer'].value, form['specblueplayer'].value]

  if len(justPlayedList) == 0 and form.has_key("redplayer"):
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
    
  print "<tr class='sortbottom'><td class='structural'/><td class='structural'><input type=\"submit\" value=\"Graph\" /></td></tr>"
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
    removeKey(qs, 'specredplayer')
    removeKey(qs, 'specblueplayer')
    removeKey(qs, 'specredscore')
    removeKey(qs, 'specbluescore')
    
    print "<p class='speculativeGameRemoval'><a href='?%s'>remove Speculative Games</a></p>" % urllib.urlencode(qs, True)


  print "<hr /><table class='structural'>"

  #add a real game
  print """<tr><td>
    <form method="post" action="">
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
      <!--<input type="hidden" name="jsonResponse" value="s" />-->
      <input type="submit" value="Submit"/>
    </form>
    </td>
    <td>
    <form method="get" action="" class="speculativeGameEntry">
      <h3>Add a Speculative game:</h3>
      <table>
        <tr>
          <th/>
          <th>Name</th>
          <th>Score</th>
        </tr>
        <tr>
          <th class='redHeader'>Red Player</th>
          <td><input type="text" name="specredplayer" value=""/></td>
          <td><input type="text" name="specredscore" value=""/></td>
        </tr>
        <tr>
          <th class='blueHeader'>Blue Player</th>
          <td><input type="text" name="specblueplayer" value=""/></td>
          <td><input type="text" name="specbluescore" value=""/></td>
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
