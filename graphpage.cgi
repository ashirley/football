#! /usr/bin/python
import cgi
import cgitb; cgitb.enable()

import urllib, os

from core import *
from htmlCore import *

def main():
  printHTMLHeader("Graph")

  qs = os.environ["QUERY_STRING"]
  qsDict = cgi.parse_qs(qs)
  
  ladderData = parseLadderFiles()
    
  print "<img src='graph.cgi?%s' />" % urllib.urlencode(qsDict, True)

  print "<form method='GET'>"

  #name

  preSelected = qsDict.get('name', [])
  print "<div class='graphPageForm'><div>Players</div><select multiple='true' name='name'>"
  for player in ladderData.getAllPlayers():
    print "<option value='%s'" % player.name
    if player.name in preSelected: print "selected='true'"
    print ">%s</option>" % player.name
  print "</select></div>"

  #gameLimit
  print "<div class='graphPageForm'><div>Number of games shown: <input name='gameLimit'"
  if 'gameLimit' in qsDict:
    print "value='%d'" % int(qsDict['gameLimit'][0])
  print " /></div>"

  #trendGameLimit
  print "<div>Number of games used for trend line: <input name='trendGameLimit'"
  if 'trendGameLimit' in qsDict:
    print "value='%d'" % int(qsDict['trendGameLimit'][0])
  print " /></div>"

  print "<div><input type='submit' value='Update' /></div></div>"
  print "</form>"

  printHTMLFooter()

main()
