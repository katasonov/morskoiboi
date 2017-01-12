from google.appengine.ext import deferred
from google.appengine.ext import ndb

from datetime import datetime, date, time
import random
import string
import logging
from collections import OrderedDict


class IPlayersProcessor:
	def do(players):
		pass

'''
Stores player data
'''
class PlayerRecord(ndb.Model):

	#technical information
	nickname = ndb.StringProperty(required=True)
	email = ndb.StringProperty(default=None)
	clientUid = ndb.StringProperty(required=True)
	appVersion = ndb.IntegerProperty(default=1)
	osType = ndb.StringProperty(required=True)
	osVersion = ndb.StringProperty(required=True)
	pushNotificationUid = ndb.StringProperty(default='')
	playService = ndb.StringProperty(required=True)
	language = ndb.StringProperty(default='')

	#game information
	shots = ndb.IntegerProperty(default=100)

	#statistic information    
	totalPlayTime = ndb.IntegerProperty(default=0) #in seconds
	totalWins = ndb.IntegerProperty(default=0)
	totalLoses = ndb.IntegerProperty(default=0)
	totalMadeShots = ndb.IntegerProperty(default=0)
	winsToGames = ndb.IntegerProperty(default=0)
	#This is virtual property needs only for ordering with query.
	#it should be calculated only as totalWins+totalLoses and
	#should not be changed manualy.
	totalGames = ndb.IntegerProperty(default=0)


	#temporary statistics
	totalPlayTimeT = ndb.IntegerProperty(default=0) #in seconds
	totalWinsT = ndb.IntegerProperty(default=0)
	totalLosesT = ndb.IntegerProperty(default=0)
	totalMadeShotsT = ndb.IntegerProperty(default=0)
	winsToGamesT = ndb.IntegerProperty(default=0)
	#This is virtual property needs only for ordering with query.
	#it should be calculated only as totalWinsT+totalLosesT and
	#should not be changed manualy.
	totalGamesT = ndb.IntegerProperty(default=0)


	shotsFromShop = ndb.IntegerProperty(default=0)

	creationDate = ndb.DateTimeProperty(auto_now_add=True)

	def to_dict(self):
		d = OrderedDict()
		
		d['nickname'] = self.nickname

		d['totalPlayTime'] = self.totalPlayTime
		d['totalWins'] = self.totalWins
		d['totalLoses'] = self.totalLoses
		d['totalMadeShots'] = self.totalMadeShots
		d['totalGames'] = self.totalGames
		d['wintofights'] = self.winsToGames

		d['totalPlayTimeT'] = self.totalPlayTimeT
		d['totalWinsT'] = self.totalWinsT
		d['totalLosesT'] = self.totalLosesT
		d['totalMadeShotsT'] = self.totalMadeShotsT
		d['totalGamesT'] = self.totalGamesT
		d['wintofightsT'] = self.winsToGamesT

		d['shots'] = self.shots
		d['shotsFromShop'] = self.shotsFromShop

		d['clientUid'] = str(self.clientUid)
		d['email'] = self.email
		d['language'] = self.language
		d['appVersion'] = self.appVersion
		d['osType'] = self.osType
		d['osVersion'] = self.osVersion
		d['playService'] = self.playService
		d['creationDate'] = str(self.creationDate)

		d['pushNotificationUid'] = self.pushNotificationUid

		return d	

def DoForAllPlayers(playersProcessor=None, cursor=None):

	logging.info("DoForAllPlayers:")
	players, next_curs, more = PlayerRecord.query().fetch_page(\
		100, start_cursor=cursor)

	if len(players) > 0:
		playersProcessor.do(players)

		deferred.defer(
			DoForAllPlayers, playersProcessor=playersProcessor, cursor=next_curs)
	logging.info("DoForAllPlayers.")




class MessageRecord(ndb.Model):
	language = ndb.StringProperty(default='')
	title = ndb.StringProperty(default='')
	message = ndb.TextProperty(required=True)
	clientUid = ndb.StringProperty(default='')
	messageType = ndb.StringProperty(default='')
	creationDate = ndb.DateTimeProperty(auto_now_add=True)

	def to_dict(self):
		d = {
			'id':str(0 if self.key is None else self.key.integer_id()),
			'title':self.title, 
			'message':self.message,
			'language':self.language,
			'clientUid':self.clientUid,
			'type':self.messageType,
			'creationDate':str(self.creationDate)
			}
		return d

class SettingsRecord(ndb.Model):
	tempStatTitle = ndb.StringProperty(default='')
	tempStatActive = ndb.BooleanProperty(default=False)
	tempStatStartDate = ndb.DateTimeProperty(auto_now_add=True)
	tempStatStopDate = ndb.DateTimeProperty(auto_now_add=True)

	def setTempStatTitle(self, title):
		self.tempStatTitle = title

	def getTempStatTitle(self):
		return self.tempStatTitle

	def getTempStatStartDate(self):
		return self.tempStatStartDate;

	def getTempStatEndDate(self):
		return self.tempStatStopDate;

	def startTempStat(self):
		self.tempStatStartDate = datetime.now()
		self.tempStatStopDate = datetime.now()
		self.tempStatActive = True

	def stopTempStat(self):
		self.tempStatStopDate = datetime.now()
		self.tempStatActive = False

	def tempStatIsActive(self):
		return self.tempStatActive;

class AdminRecord(ndb.Model):
	password = ndb.StringProperty(default='')

	def setPassword(self, newPass):
		self.password = newPass

	def login(self, password):		
		if self.password == password:
			return True

		return False


class ExtendedAudioBackground(ndb.Model):
	uploadKey = ndb.BlobKeyProperty(default=None)
	active = ndb.BooleanProperty(default=False)

	def getActive(self):
		return self.active;

	def getUploadKey(self):
		return self.uploadKey;

	def setActive(self, active):
		self.active = active

	def setUploadKey(self, key):
		self.uploadKey = key
