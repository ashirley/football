#! /usr/bin/python
import cgi
import cgitb; cgitb.enable()

import os
os.environ["HOME"] = "/home/local/aks/public_html/football/matplotlibhome"

from core import *

import matplotlib
#matplotlib.use('Cairo')
matplotlib.use('Agg')

from pylab import *
from numpy import array, polyfit, polyval

usernames = []
gameLimit = 0
trendGameLimit = 0


def main():
  global usernames
  global gameLimit
  global trendGameLimit

  #testing
  usernames=["aks", "gjhw"]
  #usernames=["aks"]
  #usernames=["gjhw"]

  gameLimit=20
  trendGameLimit=20


  form = cgi.FieldStorage()
  if form.has_key("name"):
    usernames = form.getlist('name')

  if form.has_key("gameLimit"):
    gameLimit = int(form.getfirst('gameLimit'))

  if form.has_key("trendGameLimit"):
    trendGameLimit = int(form.getfirst('trendGameLimit'))

  ladderData = parseLadderFiles()

  #dict of username -> [(time, skill)]
  plotData = DefaultDict([])

  #augment games with skill info.
  from playerstats import Skill
  Skill(ladderData)

  for game in ladderData.games:
    plotData[game.red].append((game.time, game.getVar(game.red, "oldSkill") + game.getVar(game.red, "skillChangeTo")))
    plotData[game.blue].append((game.time, game.getVar(game.blue, "oldSkill") + game.getVar(game.blue, "skillChangeTo")))

  for user in usernames:
    userPlotData = createPlotDataForUser(plotData[user])
    line, = plot(userPlotData[0], userPlotData[1], label=user)

    color = getp(line, 'color')

    #plot a trend in a dashed line
    trendM = userPlotData[4]
    trendC = userPlotData[5]
    
    lastX  = userPlotData[0][-1]
    firstX = userPlotData[0][1]

    startX = lastX
    endX   = lastX + (lastX - firstX)
    startY, endY = polyval([trendM, trendC], [startX, endX])
    
    plot([startX, endX], [startY, endY], color + '--', label='_nolegend_')
    
    #print "y = %sx + %s"%(trendM, trendC)


  #draw a min score and max score line if we are only drawing one persons score.
  if len(usernames) == 1:
     pass
     #TODO why do these cause the x axis to go to 0
#    gca().axvline(x=userPlotData[2], color='g', label='_nolegend_')
#    gca().axvline(x=userPlotData[3], color='r', label='_nolegend_')
  
  setp(gca(), xticklabels=[])
  setp(gca(), xticks=[])
  gca().axhline(color='k', label='_nolegend_')
  legend()

  import tempfile
  tmpFile = tempfile.mkstemp(".png")[1]
  savefig(tmpFile)
  import shutil
  print "Content-Type: image/png\n";
  shutil.copyfileobj(open(tmpFile, 'rb'), sys.stdout)

def createPlotDataForUser(data):
  plotDataY = [] 
  plotDataX = [] 
  maxSkill = [0,0]
  minSkill = [0,0]

  lastSkill = 0

  if len(data) >= gameLimit:
    lastSkill = data[-gameLimit - 1][1]
    data = data[-gameLimit:]

  for skillAtTime in data:
    newSkill = skillAtTime[1]
    time = skillAtTime[0]

    plotDataX.append(int(time))
    plotDataY.append(int(lastSkill))

    plotDataX.append(int(time))
    plotDataY.append(int(newSkill))

    lastSkill=newSkill

    if (newSkill > maxSkill[1]):
      maxSkill[0] = time
      maxSkill[1] = newSkill
    if (newSkill < minSkill[1]):
      minSkill[0] = time
      minSkill[1] = newSkill

  #calculate final trend

  numpoints=trendGameLimit * 2
  #print len(plotDataX), trendGameLimit, numpoints, plotDataX, plotDataX[-numpoints:]
  #print len(plotDataY), trendGameLimit, numpoints, plotDataY, plotDataY[-numpoints:]

  trendM, trendC = polyfit(array(plotDataX[-numpoints:]), array(plotDataY[-numpoints:]), 1) # 1 means a linear result.
  return (plotDataX, plotDataY, maxSkill[0], minSkill[0], trendM, trendC)

class DefaultDict(dict):
    """Dictionary with a default value for unknown keys."""
    def __init__(self, default):
        self.default = default

    def __getitem__(self, key):
        if key in self: return self.get(key)
        return self.setdefault(key, copy.deepcopy(self.default))
    
    def __copy__(self):
        copy = DefaultDict(self.default)
        copy.update(self)
        return copy

main()
