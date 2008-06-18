#! /usr/bin/python
import cgi
import cgitb; cgitb.enable()

from core import *
from htmlCore import *

import urllib

def main():
  form = cgi.FieldStorage()
  printHTMLHeader()
  #print "<H1>Quick add a game</H1>" this screws with <table height='100%'

  ladderData = parseLadderFiles([])
  players = ladderData.getAllPlayers()[:]
  
  buttons = []
  hidden=""

  if form.has_key('score2'):
    #we have all the info
    print "%s %s-%s %s" % (form['player1'].value, form['score1'].value, form['score2'].value, form['player2'].value)
    printHTMLFooter()
    return

  elif form.has_key('player2'):
    buttons = generateScoreButtons('score2')
    hidden  = "<input type='hidden' name='player1' value='%s'>" % form['player1'].value
    hidden += "<input type='hidden' name='score1' value='%s'>" % form['score1'].value
    hidden += "<input type='hidden' name='player2' value='%s'>" % form['player2'].value

  elif form.has_key('score1'):
    buttons = generatePlayerButtons(players, 'player2')
    hidden  = "<input type='hidden' name='player1' value='%s'>" % form['player1'].value
    hidden += "<input type='hidden' name='score1' value='%s'>" % form['score1'].value

  elif form.has_key('player1'):
    buttons = generateScoreButtons('score1')
    hidden = "<input type='hidden' name='player1' value='%s'>" % form['player1'].value

  else :
    buttons = generatePlayerButtons(players, 'player1')

  print "<form action='' method='GET'>"
  showSquareTable(buttons)
  print hidden
  print "</form>"

  printHTMLFooter()


def generatePlayerButtons(players, buttonName):
  #players.sort(lambda x, y: cmp(y.getLastGame().getVar(y.name, "newSkill"), x.getLastGame().getVar(x.name, "newSkill")))
  return ["<input type='submit' name='%s' value='%s' width='100%%' height='100%%' />" % (buttonName, player.name) for player in players ]

def generateScoreButtons(buttonName):
  return ["<input type='submit' name='%s' value='%s' width='100%%' height='100%%' />" % (buttonName, number) for number in [0, 1, 2, 3, 4, 5, 6, 7, 8, 9] ]


main()
