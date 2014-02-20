#! /usr/bin/python
import cgi
import cgitb; cgitb.enable()
from copy import deepcopy

import os
os.environ["HOME"] = os.path.join(os.path.dirname(os.path.realpath(__file__)), "matplotlibhome")

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

  ladderData = parseLadderFiles()

  #testing
  #usernames=["aks", "gjhw"]
  #usernames=["aks"]
  #usernames=["gjhw"]

  usernames=[]


  form = cgi.FieldStorage()
  if form.has_key("name"):
    usernames = form.getlist('name')

  #default to 20 games for 1 user or all games for more than one.
  gameLimit=20
  trendGameLimit=20
  if usernames == []:
    usernames=[p.name for p in ladderData.getAllPlayers()]
    gameLimit=0
    trendGameLimit=50

  if form.has_key("gameLimit"):
    gameLimit = int(form.getfirst('gameLimit'))

  if form.has_key("trendGameLimit"):
    trendGameLimit = int(form.getfirst('trendGameLimit'))
  
  #dict of username -> [(time, skill)]
  plotData = DefaultDict([])

  #augment games with skill info.
  from playerstats import Skill
  Skill(ladderData.games)

  for game in ladderData.games:
    plotData[game.red].append((game.time, game.getVar(game.red, "oldSkill") + game.getVar(game.red, "skillChangeTo")))
    plotData[game.blue].append((game.time, game.getVar(game.blue, "oldSkill") + game.getVar(game.blue, "skillChangeTo")))


  plotDataPerUser = {}

  data = {'firstX':[], 'lastX':[], 'lastY':[], 'highestSkill':[], 'lowestSkill':[], 'earliestGameLimit':[]}
  if gameLimit > 0:
    for user in usernames:
      date = plotData[user]
      if len(data) > gameLimit:
        data = data[-limit:]
  else:
    #include all games.
    data['earliestGameLimit'].append(0)
    
  #This could be sped up significantly, these max calls could be done in createPlotDataForUser to reduce the number of times we iterate over the list.
  for user in usernames:
    userPlotData = createPlotDataForUser(plotData[user], gameLimit)
    plotDataPerUser[user] = userPlotData

    data['firstX'].append(userPlotData['x'][1])
    data['lastX'].append(userPlotData['x'][-1])
    data['lastY'].append(userPlotData['y'][-1])
    data['highestSkill'].append(userPlotData['maxSkill'])
    data['lowestSkill'].append(userPlotData['minSkill'])

  globalFirstX = min(data['firstX'])
  globalLastX = max(data['lastX'])
  globalLowestLastY = max(data['lastY'])
  globalHighestLastY = max(data['lastY'])
  globalHighestSkill = max(data['highestSkill'])
  globalLowestSkill = min(data['lowestSkill'])


  for user in usernames:
    userPlotData = plotDataPerUser[user]
    line, = plot(userPlotData['x'], userPlotData['y'], label=user)
    #line, = plot(userPlotData[0][:-1], userPlotData[1][:-1], label=user)

    color = getp(line, 'color')

    #plot a trend in a dashed line
    trendM = userPlotData['trendM']
    trendC = userPlotData['trendC']
    
    lastX  = userPlotData['x'][-1]
    startX = lastX

    #don't go too far to the right or up and down with the trend line.
    endX1  = lastX + (globalLastX - globalFirstX)

    endY = 0
    if trendM > 0:
      endY = globalHighestLastY + (globalHighestSkill - globalLowestSkill) 
    else:
      endY = globalLowestLastY - (globalHighestSkill - globalLowestSkill) 

    endX = 0
    if trendM != 0:
      endX2  = (endY - trendC) / trendM
      endX   = min(endX1, endX2)
    else:
      endX = endX1

    startY, endY = polyval([trendM, trendC], [startX, endX])
    plot([startX, endX], [startY, endY], color + '--', label='_nolegend_')
    
    #print "y = %sx + %s"%(trendM, trendC)


  #draw a min score and max score line if we are only drawing one persons score.
  if len(usernames) == 1:
     pass
     #TODO why do these cause the x axis to go to 0
#    gca().axvline(x=userPlotData['maxSkillTime'], color='g', label='_nolegend_')
#    gca().axvline(x=userPlotData['minSkillTime'], color='r', label='_nolegend_')
  
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

def createPlotDataForUser(data, limit):
  plotDataY = [] 
  plotDataX = [] 
  maxSkill = [0,0]
  minSkill = [0,0]

  prevSkill = 0

  if len(data) > limit and limit != 0:
    prevSkill = data[-limit - 1][1]
    data = data[-limit:]

  for skillAtTime in data:
    newSkill = skillAtTime[1]
    time = skillAtTime[0]

    plotDataX.append(int(time))
    plotDataY.append(int(prevSkill))

    plotDataX.append(int(time))
    plotDataY.append(int(newSkill))

    prevSkill=newSkill

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
  return {'x': plotDataX, 
          'y': plotDataY, 
          'maxSkillTime': maxSkill[0], 
          'minSkillTime': minSkill[0],
          'maxSkill': maxSkill[1], 
          'minSkill': minSkill[1],
          'trendM': trendM, 
          'trendC': trendC}



class DefaultDict(dict):
    """Dictionary with a default value for unknown keys."""
    def __init__(self, default):
        self.default = default

    def __getitem__(self, key):
        if key in self: return self.get(key)
        return self.setdefault(key, deepcopy(self.default))
    
    def __copy__(self):
        copy = DefaultDict(self.default)
        copy.update(self)
        return copy

main()
