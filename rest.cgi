#! /usr/bin/python
import cgi
import cgitb; cgitb.enable()

from core import *
from htmlCore import *

import urllib

def main():
  form = cgi.FieldStorage()

  printJSONHeader()
  # Parse the data and show the page
  ladderData = parseLadderFiles()

  # setup all the objects which can give us statistics for a player
  from playerstats import Totals, Skill
  playerstats = Totals(ladderData.games), Skill(ladderData.games)
        

  players = ladderData.getAllUnexcludedPlayers()
  players.sort(lambda x, y: cmp(y.getLastGame().getVar(y.name, "newSkill"), x.getLastGame().getVar(x.name, "newSkill")))
  
  if form.has_key("mode"):
      if form['mode'].value == "ladder":
          print "["
          for player in players:
            print "{ \"name\":\"" + player.name + "\"," 
            
            totals = playerstats[0]
              
            print "\"total\":{ \"for\":" + str(totals.totalFor[player.name]) + ", \"against\":" + str(totals.totalAgainst[player.name]) + ", \"games\":" + str(totals.gameCount[player.name]) + " },"
            print "\"gamesToday\":" + str(totals.todayGameCount[player.name]) + ","
            
            skill = playerstats[1]
            
            print "\"skill\":" + str(skill.skill[player.name].lastSkill()) + ","
            print "\"weaselFactor\":" + str(skill.weasel[player.name]) + ","
            # TODO overrated (but there's lots of logic for this inside Skill)
            
            print "},"
          print "]"

      elif form['mode'].value == "records":
          # highest and lowest ever skill.
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
              
                # most significant ever.
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

      elif form['mode'].value == "recent":
          # recent games
          print "<tr><td>"
          showGameList(ladderData.games)
          print "</td><td>"
      elif form['mode'] == "recentSignificant":
          # recent significant games
          showGameList(
            [game for game in ladderData.games if game.isSignificant()],
            anchorName="RecentSignificantGames",
            headerName="Recent Significant Games",
            gameListStartParamName="significantGameListStart"
          )
          print "</td></tr>"
        
          print "</table>"





def removeKey(dict, key):
  if key in dict: del dict[key]

main()
