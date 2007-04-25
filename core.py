import datetime

def parseLadderFiles():
  def contains(list, string):
    return (string in list) or (string + "\n" in list)

  #open the excluded file:
  excludedFile=open('ladderExclude', 'r');
  
  excluded = [];
  
  for line in excludedFile:
    excluded.append(line);
  
  #open the ladder:
  file=open('ladder.txt', 'r');

  ladderData = LadderData();

  for line in file:
    list = line.split();
    if len(list) == 5:
      if not (contains(excluded, list[0]) or contains(excluded, list[2])):
          game  = Game(list[0],list[2],list[1],list[3], list[4]);
          ladderData.addGame(game);
  return ladderData

class Game:
  def __init__(self, r, b, rs, bs, time):
    self.red =  r
    self.blue = b
    self.redScore = int(rs)
    self.blueScore= int(bs)
    self.time = time
    self.vars = {r:{}, b:{}}
    self.speculative = False

  def getScoreFor(self, name):
    if self.red == name:
      return self.redScore
    
    if self.blue == name:
      return self.blueScore

    raise KeyError, "player " + name + " didn't play this game"

  def setVar(self, playerName, varName, varValue):
    if not playerName in self.vars.keys():
      raise KeyError, "player " + playerName + " didn't play this game"

    playerVars = self.vars[playerName]

    playerVars[varName] = varValue

  def getVar(self, playerName, varName):
    if not playerName in self.vars.keys():
      raise KeyError, "player " + playerName + " didn't play this game"

    playerVars = self.vars[playerName]

    if not varName in playerVars.keys():
      return ""

    return playerVars[varName]

  def tableHeadings():
    out = "<th class='redHeader'>Red player</th>"
    out +="<th class='redHeader'>Red Score</th>"
    out +="<th class='blueHeader'>Blue Score</th>"
    out +="<th class='blueHeader'>Blue Player</th>"
    out +="<th>Skill Change</th>"
    out +="<th>Date</th>"
      
    return out
  tableHeadings = staticmethod(tableHeadings)

  def toTableRow(self):
    out = "<td>%s</td>" % self.red
    out +="<td>%d</td>" % self.redScore
    out +="<td>%d</td>" % self.blueScore
    out +="<td>%s</td>" % self.blue

    skillChangeToRed = self.getVar(self.red, "skillChangeTo")
    skillChangeToBlue = self.getVar(self.blue, "skillChangeTo")

    if float(skillChangeToRed) > 0:
      out +="<td class='skillToRed'>%.3f</td>" % skillChangeToRed
    elif float(skillChangeToRed) < 0:
      out +="<td class='skillToBlue'>%.3f</td>" % skillChangeToBlue
    else:
        out +="<td>0</td>"

    dateStr = datetime.datetime.fromtimestamp(float(self.time))

    time = datetime.datetime.fromtimestamp(float(self.time))
    if datetime.date.fromtimestamp(float(self.time)) == datetime.date.today():
      dateStr = "%02d:%02d" % (time.hour, time.minute)
    elif datetime.date.fromtimestamp(float(self.time)) > (datetime.date.today() - datetime.timedelta(7)):
      dateStr = "%s %02d:%02d" % (("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")[time.weekday()], time.hour, time.minute)


    out +="<td>%s</td>" % dateStr
    return out;

  def tableClass(self):
    if self.speculative:
      return "speculativeGame"
    elif self.redScore == 0 or self.blueScore == 0:
      return "bagelGame"
    else:
      return ""

  def __repr__(self):
    return "Game(%s %d:%d %s)" % (self.red, self.redScore, self.blueScore, self.blue)

  def __str__(self):
    return "Game(%s %d:%d %s)" % (self.red, self.redScore, self.blueScore, self.blue)

#####################################################################

class Player:
  def __init__(self, name):
    self.games = []
    self.name = name;
    self.totalPoints = 0;
    self.totalPointsAgainst = 0;
  

  def tableHeadings():
    return "<th>name</th>"
  tableHeadings = staticmethod(tableHeadings)
  
  def toTableRow(self):
    out = "<td>"+self.name+"</td>"
    return out;

  def getLastGame(self):
    return self.games[-1]

  def played(self, game):
    if game.red == self.name:
      self.totalPoints += game.redScore;
      self.totalPointsAgainst += game.blueScore;
    elif game.blue== self.name:
      self.totalPoints += game.blueScore;
      self.totalPointsAgainst += game.redScore;
    else:
      raise KeyError, "player " + self.name + " didn't play this game"
 
    self.games.append(game);


#####################################################################

class LadderData:

  def __init__(self):
    self._players = {} 
    self.games = []
    self.vars = {}

  def addPlayer(self, name):
    #if players.contains name return
    if not self._players.has_key(name):
      newPlayer = Player(name);
      self._players[name] = newPlayer;

  #get player with given name
  def getPlayer(self, name, create=False):
    if not self._players.has_key(name):
      if create:
        newPlayer = Player(name)
        self._players[name] = newPlayer
	return newPlayer
      else:
        return None
    else:
      return self._players[name] 

  def getAllPlayers(self):
    return self._players.values()

  def addGame(self, game):
    red = self.getPlayer(game.red, True)
    red.played(game);
    self.addPlayer(game.blue);
    blue=self.getPlayer(game.blue, True);
    blue.played(game);
    self.games.append(game)
  
  def setVar(self, varName, varValue):
    self.vars[varName] = varValue

  def getVar(self, varName, default=""):
    if not varName in self.vars.keys():
      self.vars[varName] = default

    return self.vars[varName]

#####################################################################
