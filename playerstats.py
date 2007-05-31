from __future__ import division
from datetime import date

def initHash(hash, key, value = 0.0):
  if not (key in hash):
    hash[key] = value
    
def addToHashValue(hash, key, value):
  initHash(hash, key)
  hash[key] += value

class Totals:
  totalFor = {}
  totalAgainst = {}
  gameCount = {}
  todayGameCount = {}
  
  def __init__(self, ladderData):
    today = date.today()
    for game in ladderData.games:
      #NB. we call addToHashValue so that the hashes are initialised correctly
      #red player
      addToHashValue(self.totalFor, game.red, game.redScore)
      addToHashValue(self.totalAgainst, game.red, game.blueScore)
      addToHashValue(self.gameCount, game.red, 1)
      
      #blue player
      addToHashValue(self.totalFor, game.blue, game.blueScore)
      addToHashValue(self.totalAgainst, game.blue, game.redScore)
      addToHashValue(self.gameCount, game.blue, 1)

      isToday = 0
      if today == date.fromtimestamp(float(game.time)):
        isToday = 1

      addToHashValue(self.todayGameCount, game.red, isToday)
      addToHashValue(self.todayGameCount, game.blue, isToday)

  def toTableRow(self, player):
    return "<td>%d</td><td>%d</td><td>%d(%d)</td><td>%.3f</td><td>%.3f</td><td>%.3f</td>" % (
        self.totalFor[player.name],
        self.totalAgainst[player.name],
        self.gameCount[player.name],
        self.todayGameCount[player.name],
        float(self.totalFor[player.name])/float(self.gameCount[player.name]),
        float(self.totalFor[player.name])/float(self.totalAgainst[player.name]),
        float(self.totalAgainst[player.name])/float(self.gameCount[player.name]),
      )

  def toTableHeader():
    return "<th>For</th><th>Against</th><th>Games</th><th>for/game</th><th>against/game</th><th>for/against</th>"
  toTableHeader = staticmethod(toTableHeader)

#This algorithm is copied from the perl, don't ask me what it does!
class Skill:
  gradient=25
  max=180

  skill = {}
  weasel = {}

  def updateSkillAndWeasel(self, player, playerOldSkill, skillChange, opponent):
    #print player + "(" + str(self.skill[player].size()) + ") played " + opponent + "(" + str(self.skill[opponent].size()) + ")";
    skillBuf = self.skill[player]
    skillBuf.put({'oldskill':playerOldSkill, 'skill':playerOldSkill + skillChange, 'played':opponent})

    if skillBuf.justFull:
      #update weasel factor for first ten games
      for i in range(10):
        self.updateWeasel(skillBuf, i)
    elif skillBuf.size() == 10:
      #update this game, this is number > 10
      self.updateWeasel(skillBuf)
    #else # this is game < 10 we don't know what skill to use here yet.
        

  def updateWeasel(self, skillBuf, i = -1):
    if i == -1:
      i = skillBuf.size() - 1

    initHash(self.weasel, skillBuf.getPlayed(i))
    self.weasel[skillBuf.getPlayed(i)] += skillBuf.getOldSkill(i) - skillBuf.oldAvg()
    #print "updateing Weasel for " + skillBuf.getPlayed(i) + " to " + str(self.weasel[skillBuf.getPlayed(i)]);
    #print str(self.weasel[skillBuf.getPlayed(i)]) + " += " + str(skillBuf.getOldSkill(i)) + " - " + str(skillBuf.oldAvg())

  def __init__(self, ladderData):
    for game in ladderData.games:
      initHash(self.skill, game.blue, CircularSkillBuffer(10))
      initHash(self.skill, game.red, CircularSkillBuffer(10))
    
      redOldSkill = self.skill[game.red].lastSkill();
      blueOldSkill = self.skill[game.blue].lastSkill();
      
      skillDiffBlue = redOldSkill - blueOldSkill
      probBlue = 1 / (1 + 10 ** (skillDiffBlue / self.max))
      strengthBlue = game.blueScore / (game.redScore + game.blueScore)
      skillChangeToBlue = self.gradient * (strengthBlue - probBlue)

      game.setVar(game.red, "oldSkill", redOldSkill)
      game.setVar(game.blue, "oldSkill", blueOldSkill)
      game.setVar(game.red, "skillChangeTo", -skillChangeToBlue)
      game.setVar(game.blue, "skillChangeTo", skillChangeToBlue)
      game.setVar(game.red, "newSkill", redOldSkill - skillChangeToBlue)
      game.setVar(game.blue, "newSkill", blueOldSkill + skillChangeToBlue)

      if skillChangeToBlue > 7.5 or -skillChangeToBlue > 7.5:
        ladderData.getVar("significantGames", []).append(game)

      self.updateSkillAndWeasel(game.blue, blueOldSkill, skillChangeToBlue, game.red)
      self.updateSkillAndWeasel(game.red, redOldSkill, -skillChangeToBlue, game.blue)
    
    #now update the weasel score for games where one or more people havn't played 10 games yet.
    for player in self.skill:
      skillBuf = self.skill[player]

      if not skillBuf.isFull:
        for i in range(skillBuf.size()):
          self.updateWeasel(skillBuf, i)
        
      
  
  def toTableRow(self, player):
    #print self.skill[player.name].lastSkill()
    #print self.weasel[player.name]
    
    skillbuf = self.skill[player.name]

    if skillbuf.isFull:
      overratedVal = skillbuf.lastSkill() - skillbuf.avg()
      overrated = "%0.3f" % (overratedVal)
      if overratedVal > 0:
        overratedClass = "overrated"
      else:
        overratedClass = "underrated"
    else:
      overrated = "n/a"
      overratedClass = "NAoverrated"

    return "<td>%0.3f</td><td>%0.3f</td><td class='%s'>%s</td>" % (self.skill[player.name].lastSkill(), self.weasel[player.name], overratedClass, overrated)
    
  def toTableHeader():
    return "<th>Skill</th><th>Weasel Factor</th><th>Over-rated</th>"
  toTableHeader = staticmethod(toTableHeader)



class CircularSkillBuffer:
  
  def __init__(self, size):
    self.list = []
    self.maxSize = size
    self.isFull = False

  def put(self, val):
    if len(self.list) == (self.maxSize - 1):
      self.justFull = True
      self.isFull = True
    else:
      self.justFull = False
      
    self.list.append(val);
    if len(self.list) > self.maxSize:
      self.list = self.list[1:]

  def sum(self):
    total = 0
    for val in self.list:
      total += val['skill']
    return total

  def avg(self):
    return self.sum() / len(self.list)

  def oldSum(self):
    total = 0
    for val in self.list:
      total += val['oldskill']
    return total

  def oldAvg(self):
    return self.oldSum() / len(self.list)

  def lastSkill(self):
    return self.getSkill(len(self.list)-1)
    
  def getPlayed(self, index):
    if len(self.list) == 0:
      return 0
    return self.list[index]['played']

  def getSkill(self, index):
    if len(self.list) == 0:
      return 0
    return self.list[index]['skill']

  def getOldSkill(self, index):
    if len(self.list) == 0:
      return 0
    return self.list[index]['oldskill']

  def size(self):
    return len(self.list)

