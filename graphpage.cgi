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

  print "<form method='get'>"

  #name

  preSelected = qsDict.get('name', [])

  #bollocks to css, tables just work (tm)


  print "<table class='structural'><tr>"
  print "<td rowspan='4'><p>Players</p><br/><select multiple='true' name='name'>"
  for player in ladderData.getAllPlayers():
    print "<option value='%s'" % player.name
    if player.name in preSelected: print "selected='true'"
    print ">%s</option>" % player.name
  print "</select></td></tr>"

  #gameLimit
  print "<tr><td>Number of games shown:</td><td><input name='gameLimit'"
  if 'gameLimit' in qsDict:
    print "value='%d'" % int(qsDict['gameLimit'][0])
  print " /></td></tr>"

  #trendGameLimit
  print "<tr><td>Number of games used for trend line:</td><td><input name='trendGameLimit'"
  if 'trendGameLimit' in qsDict:
    print "value='%d'" % int(qsDict['trendGameLimit'][0])
  print " /></td></tr>"

  print "<tr><td><input type='submit' value='Update' /></td></tr>"
  print "</form>"

  printHTMLFooter()

main()
