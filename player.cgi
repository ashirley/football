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

    if scoreFor > scoreAgainst:
      oppGames.setdefault('won', []).append(game)
    if scoreFor == scoreAgainst:
      oppGames.setdefault('drawn', []).append(game)
    if scoreFor < scoreAgainst:
      oppGames.setdefault('lost', []).append(game)

    oppGames['goalsFor'] = oppGames.get('goalsFor', 0) + scoreFor
    oppGames['goalsAgainst'] = oppGames.get('goalsAgainst', 0) + scoreAgainst
    oppGames['skillChange'] = oppGames.get('skillChange', 0) + game.getVar(player.name, "skillChangeTo")


  opponents = list(set(redOpponents.keys() + blueOpponents.keys()))
  opponents.sort()

  print "<table class=\"sortable\" id=\"perPlayer\">"
  print "<tr><th>Name</th><th>Played</th><th>Won</th><th>Drawn</th><th>Lost</th><th>Goals for</th><th>Goals against</th><th>Goal delta</th><th>Goal delta/game</th><th>Skill change</th></tr>"
  for opp in opponents:
    won = len(redOpponents.get(opp, {}).get('won', [])) + len(blueOpponents.get(opp, {}).get('won', []))
    drawn = len(redOpponents.get(opp, {}).get('drawn', [])) + len(blueOpponents.get(opp, {}).get('drawn', []))
    lost = len(redOpponents.get(opp, {}).get('lost', [])) + len(blueOpponents.get(opp, {}).get('lost', []))

    goalsFor = redOpponents.get(opp, {}).get('goalsFor', 0) + blueOpponents.get(opp, {}).get('goalsFor', 0)
    goalsAgainst = redOpponents.get(opp, {}).get('goalsAgainst', 0) + blueOpponents.get(opp, {}).get('goalsAgainst', 0)
    
    skillChange = redOpponents.get(opp, {}).get('skillChange', 0) + blueOpponents.get(opp, {}).get('skillChange', 0)

    print "<tr><th>%s</th><td>%d</td><td>%d</td><td>%d</td><td>%d</td><td>%d</td><td>%d</td><td>%d</td><td>%.2f</td><td>%.2f</td></tr>" % (
    opp, 
    won + drawn + lost,
    won,
    drawn,
    lost,
    goalsFor,
    goalsAgainst,
    goalsFor-goalsAgainst,
    float(goalsFor-goalsAgainst)/float(won + drawn + lost),
    skillChange, 
    )

  print "</table>"

  printHTMLFooter()

main()
