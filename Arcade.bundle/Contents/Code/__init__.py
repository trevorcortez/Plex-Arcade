import os,subprocess,re,signal
from PMS import *
from PMS.MediaXML import *
from PMS.Shorthand import _L, _R, _E, _D

GAMES_ROOT      = os.path.expanduser('~/Games')
PLUGIN_PREFIX   = "/applications/arcade"
CACHE_INTERVAL  = 3600
LONG_CACHE_INTERVAL  = 750000
API_KEY = "9d8ec266a4043716015d4be2857d62c89b69f462"

####################################################################################################
def Start():
  Plugin.AddRequestHandler(PLUGIN_PREFIX, HandleRequest, _L("Arcade"), "icon-default.png", "art-default.jpg")
  Plugin.AddViewGroup("InfoList", viewMode="InfoList", contentType="items")

####################################################################################################
def HandleRequest(pathNouns, count):
	if count == 0:
		return MainMenu().ToXML()
	elif count == 1:
		dir = MediaContainer("art-default.jpg", "Games", "Arcade", pathNouns[0])
		dir.SetAttr("content", "items")
		consolepath = os.path.join(GAMES_ROOT,pathNouns[0])
		for root, dirs, files in os.walk(consolepath):
			for game in files:
				if (game not in [".DS_Store"]):
					gameID = gameIDFor(game,consoleNameFor(pathNouns[0]))
					item = DirectoryItem("%s/%s/%s" % (PLUGIN_PREFIX,pathNouns[0],game), stripCrap(game), thumb=fetchDataForId("art",gameID), summary=fetchDataForId('description',gameID))
		#  			item.SetAttr("year", fetchDataForId('releaseDate',gameID))
					dir.AppendItem(item)
		return dir.ToXML()
	elif count == 2:
		gamePath = os.path.join(GAMES_ROOT,pathNouns[0],pathNouns[1])
#   		subprocess.call(['killall','-9','PlexHelper','>','/dev/null'])
# 	 	killall('PlexHelper')
 		subprocess.call(["open","-W",gamePath])
# 		subprocess.call('~/Library/Application\ Support/Plex/PlexHelper', shell=True)
		return
	else:
		return
			
####################################################################################################
def MainMenu():
  dir = MediaContainer("art-default.jpg", None, "Arcade")
  dir.SetAttr("content", "items")
  for console in os.listdir(GAMES_ROOT):
  	fullpath = os.path.join(GAMES_ROOT, console)
	if os.path.isdir(fullpath):
  		dir.AppendItem(DirectoryItem("%s/%s" % (PLUGIN_PREFIX,console), "%s" % console, thumb=_R("icon-default.png")))
  return dir
  
####################################################################################################
def gameIDFor(name,passedPlatform):
	name = stripCrap(name)
	url = "http://api.giantbomb.com/search/?api_key=%s&query=%s&resources=game&field_list=name,id&format=json" % (API_KEY, HTTP.Quote(name))
 	try:
 		json = HTTP.GetCached(url, LONG_CACHE_INTERVAL)
 		results = JSON.DictFromString(json)
		for game in results['results']:
			for possiblePlatform in  fetchDataForId('platforms',game['id']):
				if possiblePlatform['name'] == passedPlatform:
					return game['id']
		return "0"
	except:
		return "0"
		
####################################################################################################
def fetchDataForId(data,passedID):
	url = "http://api.giantbomb.com/game/%s/?api_key=%s&field_list=platforms,original_release_date,deck,image&format=json" % (passedID,API_KEY)
 	try:
 		json = HTTP.GetCached(url, LONG_CACHE_INTERVAL)
 		results = JSON.DictFromString(json)
 		if data == 'description':
 			return results['results']['deck']
		elif data == 'releaseDate':
			return results['results']['deck']
		elif data == 'art':
			return results['results']['image']['super_url']
		elif data == 'platforms':
			return results['results']['platforms']
	except:
		Log.Add("Couldn't get metadata for game id: %s" % passedID)
		if data == 'art':
			return "icon-default.png"
		else:
			return ""

####################################################################################################
def consoleNameFor(incoming):
	incoming = incoming.strip()
	if incoming.lower() in ['nintendo','nes','nintendo entertainment system']:
		return "NES"
	elif incoming.lower() in ['super nintendo','snes','super nintendo entertainment system']:
		return "SNES"
	elif incoming.lower() in ['gba','game boy advance','game boy advanced']:	
		return "Game Boy Advance"
	elif incoming.lower() in ['gb','game boy','gameboy']:	
		return "Game Boy"
	elif incoming.lower() in ['nintendo ds','ds','nintendods']:	
		return "Nintendo DS"
	elif incoming.lower() in ['n64','nintendo64','nintendo 64']:	
		return "Nintendo 64"
	elif incoming.lower() in ['genesis','sega genesis','sega']:	
		return "Genesis"
	else:
		return "NES"

####################################################################################################
def stripCrap(name):
	name = os.path.splitext(name)[0]
	name = re.sub(r'\(.*?\)', "", name)
	name = re.sub(r'\[.*?\]', "", name)
	return name.strip()

####################################################################################################
def killall(processname): 
	f = subprocess.Popen(['killall','-9',processname],shell=True)
