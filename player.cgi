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

  #setup all the objects which can give us statistics for a player (This needs to be here so we calculate the skill for the recent games.
  from playerstats import Totals, Skill
  playerstats = Totals(ladderData.games), Skill(ladderData.games)

  #recent games
  showGameList(player.games)

  print "<h2>Graph</h2>"
  print "<a href='graphpage.cgi?name=%s'><img src='graph.cgi?name=%s' /></a>" % (name, name)
  
  print "<h2>Per-player Stats</h2>"

  redGames=[]
  blueGames=[]

  redOpponents={}
  blueOpponents={}

  for game in player.games:
    if game.red == name:
      redGames.append(game)
      opponent = game.blue
      opponentDict = blueOpponents


    if game.blue == name:
      blueGames.append(game)
      opponent = game.red
      opponentDict = redOpponents

    oppGames = opponentDict.setdefault(opponent, {})

    scoreFor = game.getScoreFor(name)
    scoreAgainst = game.getScoreFor(opponent)
    skillChangeThisGame = game.getVar(player.name, "skillChangeTo")

    if scoreFor > scoreAgainst:
      oppGames.setdefault('won', []).append(game)
      if scoreAgainst == 0:
        oppGames.setdefault('bagelWin', []).append(game)
    if scoreFor == scoreAgainst:
      oppGames.setdefault('drawn', []).append(game)
    if scoreFor < scoreAgainst:
      oppGames.setdefault('lost', []).append(game)
      if scoreFor == 0:
        oppGames.setdefault('bagelLoss', []).append(game)

    if skillChangeThisGame > 7.5:
      oppGames.setdefault('significantWin', []).append(game)
    if skillChangeThisGame < -7.5:
      oppGames.setdefault('significantLoss', []).append(game)

    oppGames['goalsFor'] = oppGames.get('goalsFor', 0) + scoreFor
    oppGames['goalsAgainst'] = oppGames.get('goalsAgainst', 0) + scoreAgainst
    oppGames['skillChange'] = oppGames.get('skillChange', 0) + skillChangeThisGame


  opponents = list(set(redOpponents.keys() + blueOpponents.keys()))
  opponents.sort()

  print "<table class=\"sortable\" id=\"perPlayer\">"
  print "<tr><th>Name</th><th>Played</th><th>10-0 Win</th><th>Significant Win</th><th>Win</th><th>Drawn</th><th>Lost</th><th>Significant Loss</th><th>10-0 Loss</th><th>Goals for</th><th>Goals against</th><th>Goal delta</th><th>Goal delta/game</th><th>Skill change</th></tr>"

  totalPlayed = 0 
  totalBagelWin = 0
  totalSignificantWin = 0
  totalWon = 0
  totalDrawn = 0
  totalLost = 0
  totalSignificantLoss = 0
  totalBagelLoss = 0
  totalGoalsFor = 0
  totalGoalsAgainst = 0
  totalGoalsDifference = 0
  totalSkillChange = 0

  for opp in opponents:
    def aggregateLen (varName):
      return len(redOpponents.get(opp, {}).get(varName, [])) + len(blueOpponents.get(opp, {}).get(varName, []))

    def aggregateAdd (varName):
      return redOpponents.get(opp, {}).get(varName, 0) + blueOpponents.get(opp, {}).get(varName, 0)

    won = aggregateLen('won')
    drawn = aggregateLen('drawn')
    lost = aggregateLen('lost')

    goalsFor = aggregateAdd('goalsFor')
    goalsAgainst = aggregateAdd('goalsAgainst')
    
    skillChange = aggregateAdd('skillChange')

    played = won + drawn + lost
    bagelWin = aggregateLen('bagelWin')
    significantWin = aggregateLen('significantWin')
    bagelLoss = aggregateLen('bagelLoss')
    significantLoss = aggregateLen('significantLoss')

    goalsDifference = goalsFor - goalsAgainst
    goalsDifferencePerGame = float(goalsDifference)/float(played),

    totalPlayed += played
    totalBagelWin += bagelWin
    totalSignificantWin += significantWin
    totalWon += won
    totalDrawn += drawn
    totalLost += lost
    totalSignificantLoss += significantLoss
    totalBagelLoss += bagelLoss
    totalGoalsFor += goalsFor
    totalGoalsAgainst += goalsAgainst
    totalGoalsDifference += goalsDifference
    totalSkillChange += skillChange


    print "<tr><th>%s</th><td>%d</td><td>%d</td><td>%d</td><td>%d</td><td>%d</td><td>%d</td><td>%d</td><td>%d</td><td>%d</td><td>%d</td><td>%d</td><td>%.2f</td><td>%.2f</td></tr>" % (
    opp, 
    played,
    bagelWin,
    significantWin,
    won,
    drawn,
    lost,
    aggregateLen('significantLoss'),
    aggregateLen('bagelLoss'),
    goalsFor,
    goalsAgainst,
    goalsDifference,
    float(goalsFor-goalsAgainst)/float(won + drawn + lost),
    skillChange, 
    )

  print "<tr><th>Totals</th><td>%d</td><td>%d</td><td>%d</td><td>%d</td><td>%d</td><td>%d</td><td>%d</td><td>%d</td><td>%d</td><td>%d</td><td>%d</td><td>%.2f</td><td>%.2f</td></tr>" % (
    totalPlayed,
    totalBagelWin,
    totalSignificantWin,
    totalWon,
    totalDrawn,
    totalLost,
    totalSignificantLoss,
    totalBagelLoss,
    totalGoalsFor,
    totalGoalsAgainst,
    totalGoalsDifference,
    float(totalGoalsDifference)/float(totalPlayed),
    totalSkillChange, 
    )

  print "</table>"

  printHTMLFooter()

main()
