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
  
  def __init__(self, games):
    today = date.today()
    for game in games:
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
    forPerAgainst = "&infin;"
    if float(self.totalAgainst[player.name]) != 0:
      forPerAgainst = "%.3f" % (float(self.totalFor[player.name])/float(self.totalAgainst[player.name]))
    return "<td>%d</td><td>%d</td><td>%d(%d)</td><td>%.3f</td><td>%.3f</td><td>%s</td>" % (
        self.totalFor[player.name],
        self.totalAgainst[player.name],
        self.gameCount[player.name],
        self.todayGameCount[player.name],
        float(self.totalFor[player.name])/float(self.gameCount[player.name]),
        float(self.totalAgainst[player.name])/float(self.gameCount[player.name]),
        forPerAgainst,
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

  def __init__(self, games):
    for game in games:
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
    lastSkill = skillbuf.lastSkill()

    if skillbuf.isFull:
      overratedVal = lastSkill - skillbuf.avg()
      overrated = "%0.3f" % (overratedVal)
      if overratedVal > 0:
        overratedClass = "overrated"
      else:
        overratedClass = "underrated"
    else:
      overrated = "n/a"
      overratedClass = "NAoverrated"


    streak = skillbuf.getStreak()

    if streak == 0:
      lastSkillChange="n/a"
    elif streak < 0:
      lastSkillChange ="&darr;<span class=\"streak\">%d</span>" % (-1 * streak)
    else:
      lastSkillChange = "&uarr;<span class=\"streak\">%d</span>" % (streak)

    return "<td>%0.3f</td><td class='%s'>%s</td><td>%.3f</td><td>%s</td>" % (self.weasel[player.name], overratedClass, overrated, lastSkill, lastSkillChange)
    
  def toTableHeader():
    return "<th>Weasel Factor</th><th>Over-rated</th><th>Skill</th><th>&Delta;</th>"
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
    "The player's Skill after they have played their last game"
    return self.getSkill(len(self.list)-1)
    
  def penultimateSkill(self):
    "The player's skill before they player their last game. They must have played 2 games to call this"
    return self.getSkill(len(self.list)-2)
    
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

  def getStreak(self):
    """The player's skill streak.
       This is:
         0        if they havn't played enough games (0 or 1) or their last game didn't change their skill (unlikely!)
         positive if they have an upwards streak
         negative if they have a downwards streak
    """
    if len(self.list) < 2 or self.lastSkill() == self.penultimateSkill():
      return 0
    
    op = 0
    sign = 0
    if self.penultimateSkill() < self.lastSkill():
      op = lambda x, y: x < y
      sign = +1
    else:
      op = lambda x, y: x > y
      sign = -1

    i = 2
    while op(self.getSkill(len(self.list) - (i + 1)), self.getSkill(len(self.list) - i)):
      i += 1

    return sign * (i-1)

  def size(self):
    return len(self.list)

