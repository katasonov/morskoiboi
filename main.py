from utils import *
import sys
import urllib

import webapp2

import logging
from google.appengine.ext import db

import os
import re
import json

from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers

from google.appengine.api import urlfetch

#from django.utils import simplejson as json

import datetime
import time

from google.appengine.ext import deferred

from google.appengine.api import memcache

import base64
import array

import urllib2

import jinja2

from google.appengine.ext import ndb


from datetime import datetime, date, time, timedelta		

import models

from models import PlayerRecord 
from models import MessageRecord
from models import AdminRecord
from models import SettingsRecord
from models import ExtendedAudioBackground

import csv

import cron_jobs


SERVER_API_KEY = 'AIzaSyAx7mw84u8Vpp6lfvM4dIoKe20QdpnlLyA'

class JSONEncoder(json.JSONEncoder):

	def default(self, o):
		# If this is a key, you might want to grab the actual model.
		if isinstance(o, db.Key):
			o = db.get(o)

		if isinstance(o, db.Model):
			return db.to_dict(o)
		elif isinstance(o, (datetime, date, time)):
			return str(o)  # Or whatever other date format you're OK with...


JINJA_ENVIRONMENT = jinja2.Environment(
	loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
	extensions=['jinja2.ext.autoescape'],
	autoescape=True)
	
gErrors = [
	"Ok", 
	"Undefined", 
	"Invalid arguments", 
	"Object not found", 
	"Operation is impossible",
	"Object exists"]

class PlayerAdd(webapp2.RequestHandler):
	
	def get(self):
		#logging.info('url: '+ self.request.query_string)
		ret = {}
		ret['error'] = gErrors[2]
		
		try:
			nickname = urllib.unquote(self.request.get('nickName').encode('utf-8')).decode("utf-8")
			email = urllib.unquote(self.request.get('email').encode('utf-8')).decode("utf-8")
			playService = urllib.unquote(self.request.get('playService').encode('utf-8')).decode("utf-8")
			appVersion = int(self.request.get('appVersion'))
			osType = str(self.request.get('osType'))
			osVersion = str(self.request.get('osVersion'))
			pushNotificationUid = str(self.request.get('pushNotificationUid'))
			shots = int(self.request.get('shots'))
			clientUid = str(self.request.get('clientUid'))
			language = str(self.request.get('language'))
		
			if  len(nickname) == 0 or len(playService) == 0 or len(osType) == 0 \
			or len(clientUid) == 0:                 
				ret['error'] = gErrors[2]
				raise 1
		
		
			#clientUid=id_generator()
			nkey = ndb.Key(PlayerRecord, clientUid)
			
			player = nkey.get()
			if not player:
				player = PlayerRecord(
					key=nkey,
					nickname=nickname, 
					email=email, 
					appVersion=appVersion,
					osType=osType,
					osVersion=osVersion,
					pushNotificationUid=pushNotificationUid,
					playService=playService,
					shots=shots,
					clientUid=clientUid,
					language=language)
				player.put()
			else:
				ret['error'] = gErrors[5]
				raise 2

			ret['error'] = gErrors[0]
		except:
			pass
			
		 
		self.response.set_status(200)
		self.response.out.write(json.dumps(ret))
		return
		

class PlayerGet(webapp2.RequestHandler):
	
	def get(self):
	
		ret = {}
		ret['error'] = gErrors[1]
		clientUid = str(self.request.get('clientUid'))
		
		if len(clientUid) != 0:
			nkey = ndb.Key(PlayerRecord, clientUid)
			player = nkey.get()
			if player is not None:
				ret['player'] = player.to_dict()
				ret['error'] = gErrors[0]
			else:
				ret['error'] = gErrors[3]
		self.response.set_status(200)
		self.response.out.write(json.dumps(ret, ensure_ascii=False))
		return

class PlayerSet(webapp2.RequestHandler):
	
	def get(self):

		ret = {}
		ret['error'] = gErrors[1]
		updated = False


		try:

			settingsArr = SettingsRecord.query().fetch(1)
			settings = None
			tmpStatActive = False
			if len(settingsArr) > 0:
				settings = settingsArr[0]
				tmpStatActive = settings.tempStatIsActive()

			clientUid = str(self.request.get('clientUid'))
			nkey = ndb.Key(PlayerRecord, clientUid)
			player = nkey.get()
			if player is None:
				raise 1
			
			nickname = urllib.unquote(self.request.get('nickName').encode('utf-8')).decode("utf-8")
			if nickname != '':
				logging.info('nickname: ' + nickname + '.')
				player.nickname = nickname
				updated = True
			email = urllib.unquote(self.request.get('email').encode('utf-8')).decode("utf-8")
			if email != '':
				player.email = email
				updated = True
			try:
				appVersion = int(self.request.get('appVersion'))
				player.appVersion = appVersion
				updated = True
			except:
				pass
			osType = str(self.request.get('osType'))
			if osType != '':
				player.osType = osType
				updated = True

			osVersion = str(self.request.get('osVersion'))
			if osVersion != '':
				player.osVersion = osVersion
				updated = True
			
			pushNotificationUid = str(self.request.get('pushNotificationUid'))
			if pushNotificationUid != '':			
				player.pushNotificationUid = pushNotificationUid
				updated = True
			try:
				shots = int(self.request.get('shots'))
				player.shots = shots if shots > 0 else 0
				updated = True
			except:
				pass
			try:
				totalLoses = int(self.request.get('totalLoses'))
				diff = totalLoses - player.totalLoses
				diff = 0 if diff < 0 else diff
				player.totalLoses += diff
				player.totalGames +=  diff
				player.winsToGames =  int((float(player.totalWins)/player.totalGames)*100)
				if tmpStatActive:
					player.totalLosesT += diff
					player.totalGamesT +=  diff
					player.winsToGamesT =  int((float(player.totalWinsT)/player.totalGamesT)*100)
				updated = True
			except:
				pass
			try:
				totalWins = int(self.request.get('totalWins'))
				diff = totalWins - player.totalWins
				diff = 0 if diff < 0 else diff
				player.totalWins += diff
				player.totalGames +=  diff
				player.winsToGames =  int((float(player.totalWins)/player.totalGames)*100)
				if tmpStatActive:
					player.totalWinsT += diff
					player.totalGamesT +=  diff
					player.winsToGamesT =  int((float(player.totalWinsT)/player.totalGamesT)*100)
				updated = True
			except:
				pass
			try:
				totalMadeShots = int(self.request.get('totalMadeShots'))
				diff = totalMadeShots - player.totalMadeShots
				diff = 0 if diff < 0 else diff
				player.totalMadeShots += diff
				if tmpStatActive:
					player.totalMadeShotsT += diff				
				updated = True
			except:
				pass
			try:
				totalPlayTime = int(self.request.get('totalPlayTime'))
				diff = totalPlayTime - player.totalPlayTime
				diff = 0 if diff < 0 else diff
				player.totalPlayTime += diff
				if tmpStatActive:
					player.totalPlayTimeT += diff
				updated = True
			except:
				pass
			language = str(self.request.get('language'))
			if language != '':
				player.language = language
				updated = True

			if updated == True:
				player.put()
				ret['error'] = gErrors[0]
			else:
				ret['error'] = gErrors[2]
		except:
			pass

		self.response.set_status(200)
		self.response.out.write(json.dumps(ret))
		return


class PlayerAddShots(webapp2.RequestHandler):
	
	def get(self):

		ret = {}
		ret['error'] = gErrors[1]
		updated = False

		try:
			clientUid = str(self.request.get('clientUid'))
			fromShop = str(self.request.get('fromShop'))

			nkey = ndb.Key(PlayerRecord, clientUid)
			player = nkey.get()
			if player is None:
				raise 1
			shots = int(self.request.get('shots'))
			player.shots = player.shots + shots
			player.shots = player.shots if player.shots > 0 else 0

			if fromShop == '1':
				player.shotsFromShop = player.shotsFromShop + shots
			player.put()
			ret['error'] = gErrors[0]
		except:
			pass

		self.response.set_status(200)
		self.response.out.write(json.dumps(ret))
		return


class PushNotificationBatchSender(models.IPlayersProcessor):

	def __init__(self, title, message):
		self.title = title
		self.message = message

	def do(self, players):
		if len(players) < 1:
				return
		logging.info("PushNotificationBatchSender:do:")
		logging.info("for " + str(len(players)) + " players")
		regIds=[]
		for p in players:
			if p.pushNotificationUid is not None and len(p.pushNotificationUid):
				pass
			regIds = regIds + [p.pushNotificationUid]
		url = "https://android.googleapis.com/gcm/send"
		headers = { 'Content-Type' : 'application/json', 
			'Authorization': 'key=' + SERVER_API_KEY }

		values = { 'registration_ids': regIds, 
			'data': {'title': self.title, 'message': self.message} }


		data = urllib.urlencode(values)
		logging.info('requesting push:')
		req = urllib2.Request(url, json.dumps(values), headers)
		response = urllib2.urlopen(req)
		the_page = response.read()
		#self.response.out.write(the_page)
		logging.info('push response: '+ the_page)

	

class MessageAdd(webapp2.RequestHandler):
	
	def get(self):
		#logging.info('url: '+ self.request.query_string)
		ret = {}
		ret['error'] = gErrors[2]
		
		#try:
		title = urllib.unquote(self.request.get('title').encode('utf-8')).decode("utf-8")
		message = urllib.unquote(self.request.get('message').encode('utf-8')).decode("utf-8")
		messageType = str(self.request.get('type'))
		language = str(self.request.get('language'))
		clientUid = str(self.request.get('clientUid'))

		if title is None:
			title = ''

		if not message:                 
			raise 1
	
		if messageType != '2':
			if clientUid != '':
				nkey = ndb.Key(PlayerRecord, clientUid)
				player = nkey.get()
				if not player:
					ret['error'] = gErrors[3]			
					raise 1
			
			message = MessageRecord(title=title, message=message, clientUid=clientUid,\
				language=language, messageType=messageType)

			message.put()
			#except:
			#	pass
		else:


			if clientUid == '':
				#making Push requests for all players
				models.DoForAllPlayers(PushNotificationBatchSender(title, message))
			else:
				nkey = ndb.Key(PlayerRecord, clientUid)
				player = nkey.get()
				if not player:
					ret['error'] = gErrors[3]			
					raise 1
				PushNotificationBatchSender(title, message).do([player])

			
		ret['error'] = gErrors[0]
		 
		self.response.set_status(200)
		self.response.out.write(json.dumps(ret))
		return

class MessageGet(webapp2.RequestHandler):
	
	def get(self):
		#logging.info('url: '+ self.request.query_string)
		ret = {}
		ret['error'] = gErrors[2]
		
		clientUid = str(self.request.get('clientUid'))
		language = str(self.request.get('language'))
		messageType = str(self.request.get('type'))
		number = self.request.get('number')
		
		if number == '':
			count = MessageRecord.query(MessageRecord.clientUid == clientUid, \
				MessageRecord.language == language, \
				MessageRecord.messageType == messageType).count()

			ret['totalNumber'] = count
			ret['error'] = gErrors[0]			
		else:
			try:
				number = int(number)
				messages = MessageRecord.query(MessageRecord.clientUid == clientUid, \
					MessageRecord.language == language, \
					MessageRecord.messageType == messageType). \
					order(-MessageRecord.creationDate).fetch(number)
				
				ret['messages'] = [m.to_dict() for m in messages]
				ret['error'] = gErrors[0]
				#return
			except:
				pass
		 
		self.response.set_status(200)
		self.response.out.write(json.dumps(ret, ensure_ascii=False))
		return

class MessageDelete(webapp2.RequestHandler):
	
	def get(self):
		#logging.info('url: '+ self.request.query_string)
		ret = {}
		ret['error'] = gErrors[0]
		
		mid = str(self.request.get('id'))

		if mid != '':
			try:
				mid = int(mid)
				nkey = ndb.Key(MessageRecord, mid)			
				nkey.delete()
			except:
				ret['error'] = gErrors[3]

		self.response.set_status(200)
		self.response.out.write(json.dumps(ret, ensure_ascii=False))
		return

import csv, codecs, cStringIO

class UnicodeWriter:
	"""
	A CSV writer which will write rows to CSV file "f",
	which is encoded in the given encoding.
	"""

	def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
		# Redirect output to a queue
		self.queue = cStringIO.StringIO()
		self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
		self.stream = f
		self.encoder = codecs.getincrementalencoder(encoding)()

	def writerow(self, row):
		self.writer.writerow([s.encode("utf-8") if isinstance(s, basestring) else str(s) for s in row])
		# Fetch UTF-8 output from the queue ...
		data = self.queue.getvalue()
		data = data.decode("utf-8")
		# ... and reencode it into the target encoding
		data = self.encoder.encode(data)
		# write to the target stream
		self.stream.write(data)
		# empty queue
		self.queue.truncate(0)

	def writerows(self, rows):
		for row in rows:
			self.writerow(row)

class PlayerGetCSV(webapp2.RequestHandler):
	def get(self):

		accessCookie = self.request.cookies.get("AccessCode")
		code = memcache.get('AccessCookie')
		if not (accessCookie is not None and code is not None and code == accessCookie):
			self.redirect("/admin")
			return


		self.response.headers['Content-Type'] = 'application/csv'
		self.response.headers['Content-Disposition'] = 'inline; filename="players.csv"'

		writer = UnicodeWriter(self.response.out, delimiter=';', encoding="utf-8")
		players = PlayerRecord.query().fetch()

		writer.writerow(PlayerRecord().to_dict().keys())
		for p in players:
			writer.writerow(p.to_dict().values())

class PlayerClearTempStatData(webapp2.RequestHandler):
	
	def get(self):

		deferred.defer(cron_jobs.ClearPlayerTempStatValues)
		self.response.out.write('Clearing successfully initiated.')

class MessageGetCSV(webapp2.RequestHandler):
	def get(self):

		accessCookie = self.request.cookies.get("AccessCode")
		code = memcache.get('AccessCookie')
		if not (accessCookie is not None and code is not None and code == accessCookie):
			self.redirect("/admin")
			return


		self.response.headers['Content-Type'] = 'application/csv'
		self.response.headers['Content-Disposition'] = 'inline; filename="messages.csv"'
		writer = UnicodeWriter(self.response.out, delimiter=';', encoding="utf-8")
		messages = MessageRecord.query().fetch()

		writer.writerow(MessageRecord().to_dict().keys())
		for m in messages:
			writer.writerow(m.to_dict().values())



class PlayerGetTop(webapp2.RequestHandler):
	def get(self):

		ret = {}
		ret['error'] = gErrors[0]

		order = str(self.request.get('order'))

		players = []
		tempStatRequested = False
		if order == 'totalWins':
			players = PlayerRecord.query().order(-PlayerRecord.totalWins).fetch(100)
		elif order == 'totalMadeShots':
			players = PlayerRecord.query().order(-PlayerRecord.totalMadeShots).fetch(100)
		elif order == 'totalPlayTime':
			players = PlayerRecord.query().order(-PlayerRecord.totalPlayTime).fetch(100)
		elif order == 'totalGames':
			players = PlayerRecord.query().order(-PlayerRecord.totalGames).fetch(100)
		elif order == 'wintofights':
			players = PlayerRecord.query().order(-PlayerRecord.winsToGames).fetch(100)
		elif order == 'totalWinsT':
			tempStatRequested = True
			players = PlayerRecord.query().order(-PlayerRecord.totalWinsT).fetch(100)
		elif order == 'totalMadeShotsT':
			tempStatRequested = True
			players = PlayerRecord.query().order(-PlayerRecord.totalMadeShotsT).fetch(100)
		elif order == 'totalPlayTimeT':
			tempStatRequested = True
			players = PlayerRecord.query().order(-PlayerRecord.totalPlayTimeT).fetch(100)
		elif order == 'totalGamesT':
			tempStatRequested = True
			players = PlayerRecord.query().order(-PlayerRecord.totalGamesT).fetch(100)
		elif order == 'wintofightsT':
			tempStatRequested = True
			players = PlayerRecord.query().order(-PlayerRecord.winsToGamesT).fetch(100)
		else:
			players = PlayerRecord.query().order(-PlayerRecord.totalGames).fetch(100)

		if tempStatRequested:
			settingsArr = SettingsRecord.query().fetch(1)
			settings = None
			if len(settingsArr) > 0:
				settings = settingsArr[0]
				ret['intervalStatTitle'] = 	settings.getTempStatTitle()
				ret['intervalStatStartDate'] = 	str(settings.getTempStatStartDate())
				if not settings.tempStatIsActive():
					ret['intervalStatEndDate'] = str(settings.getTempStatEndDate())
		
		ret['players'] = [p.to_dict() for p in players]
		self.response.set_status(200)
		self.response.out.write(json.dumps(ret, ensure_ascii=False))


class GetTime(webapp2.RequestHandler):
	
	def get(self):
		ret = {}
		ret['time'] = str(datetime.now())

		self.response.set_status(200)
		self.response.out.write(json.dumps(ret))


class GetAdminPanel(webapp2.RequestHandler):
	
	def get(self):

		accessCookie = self.request.cookies.get("AccessCode")
		upload_audio_url = blobstore.create_upload_url('/upload_audio')
		
		template_values = {'UploadAudioUrl': upload_audio_url}

		template = JINJA_ENVIRONMENT.get_template('login.html')
		if accessCookie is not None:
			code = memcache.get('AccessCookie')
			if code is not None and code == accessCookie:
				settingsArr = SettingsRecord.query().fetch(1)
				settings = None
				intervalStatTitle = ''
				needStartIntervalStat = True
				if len(settingsArr) > 0:
					settings = settingsArr[0]
					intervalStatTitle = settings.getTempStatTitle()
					needStartIntervalStat = not settings.tempStatIsActive()
				else:
					settings = SettingsRecord()
					settings.put()
				template_values['NeedStartIntervalStat'] =  needStartIntervalStat
				if needStartIntervalStat == False:
					template_values['IntervalStatTitle'] =  intervalStatTitle

				exAudioBgArr = ExtendedAudioBackground.query().fetch(1)
				exAudioBg = None
				if len(exAudioBgArr) > 0:
					exAudioBg = exAudioBgArr[0]
					needAudioUpload = not exAudioBg.getActive()
					if not exAudioBg.getActive():
						template_values['NeedAudioUpload'] =  True
				else:
					exAudioBg = ExtendedAudioBackground()
					exAudioBg.put()
					template_values['NeedAudioUpload'] =  True

				template = JINJA_ENVIRONMENT.get_template('admin.html')

		self.response.set_status(200)
		self.response.out.write(template.render(template_values))
		return

class UploadAudioHandler(blobstore_handlers.BlobstoreUploadHandler):
	def post(self):
		try:
			upload = self.get_uploads()[0]
			exAudioBgArr = ExtendedAudioBackground.query().fetch(1)
			exAudioBg = None
			if len(exAudioBgArr) > 0:
				exAudioBg = exAudioBgArr[0]
			else:
				exAudioBg = ExtendedAudioBackground()

			exAudioBg.setUploadKey(upload.key())
			exAudioBg.setActive(True)

			exAudioBg.put()

			self.redirect('/admin')

		except:
			logging.error(sys.exc_info()[0])
			self.error(500)		

class StopAudioShare(webapp2.RequestHandler):
	
	def get(self):

		accessCookie = self.request.cookies.get("AccessCode")

		code = memcache.get('AccessCookie')
		if not (accessCookie is not None and code is not None and code == accessCookie):
			self.redirect("/admin")
			return


		exAudioBgArr = ExtendedAudioBackground.query().fetch(1)
		exAudioBg = None
		if len(exAudioBgArr) > 0:
			exAudioBg = exAudioBgArr[0]

		blobKey = exAudioBg.getUploadKey()
		if blobKey  is not None:
			blobstore.delete(blobKey)
		exAudioBg.setActive(False)
		exAudioBg.setUploadKey(None)
		exAudioBg.put()

		self.redirect('/admin')
		return


class GetBlob(blobstore_handlers.BlobstoreDownloadHandler):
    def get(self, blobKey):
        if not blobstore.get(blobKey):
            self.error(404)
        else:
            self.send_blob(blobKey)

class GetAudioBgPath(webapp2.RequestHandler):
	
	def get(self):
		ret = {'path': ''}

		exAudioBgArr = ExtendedAudioBackground.query().fetch(1)
		exAudioBg = None
		if len(exAudioBgArr) > 0:
			exAudioBg = exAudioBgArr[0]
			if exAudioBg.getActive():
				ret['path'] = str(exAudioBg.getUploadKey())

		self.response.set_status(200)
		self.response.out.write(json.dumps(ret, ensure_ascii=False))


class Login(webapp2.RequestHandler):
	
	def post(self):

		password = str(self.request.get('password'))

		admins = AdminRecord.query().fetch(1)		

		admin = None
		if len(admins) == 0:
			admin = AdminRecord()
			admin.put()
		else:
			admin = admins[0]


		accessCookie = ''
		if admin.login(password) == True:
			accessCookie = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(16))

			logging.info("DomainName: " + self.request.host_url)
			memcache.set("AccessCookie", accessCookie, 3600)
			self.response.set_cookie('AccessCode', accessCookie, 
				expires=datetime.now() + timedelta(minutes=60), 
				path='/', domain='' if 'localhost' in self.request.host \
				else self.request.host)



		self.response.set_status(200)
		self.redirect('/admin')



class ChangeAdminPassword(webapp2.RequestHandler):
	def get(self):

		accessCookie = self.request.cookies.get("AccessCode")
		password = str(self.request.get('newPassword'))


		code = memcache.get('AccessCookie')
		if not (accessCookie is not None and code is not None and code == accessCookie):
			self.redirect("/admin")
			return

		admins = AdminRecord.query().fetch(1)
		admin = admins[0]

		admin.setPassword(password)
		admin.put()

		return

from google.appengine.api import mail
from google.appengine.api.app_identity import get_application_id

class SendAdminPasswordToEmail(webapp2.RequestHandler):
	def get(self):

		accessCookie = self.request.cookies.get("AccessCode")

		code = memcache.get('AccessCookie')
		if not (accessCookie is not None and code is not None and code == accessCookie):
			self.redirect("/admin")
			return

		admins = AdminRecord.query().fetch(1)
		admin = admins[0]

		sender = "alexander.katasonov@gmail.com"
		mail.send_mail(sender=sender,
					  to="bsprogame@gmail.com",
					  subject="Your Password to Admin panel",
					  body="""
		Password: """ + admin.password)

		return		

class StartIntervalStat(webapp2.RequestHandler):
	
	def get(self):

		accessCookie = self.request.cookies.get("AccessCode")
		title = urllib.unquote(self.request.get('title').encode('utf-8')).decode("utf-8")

		if title is None:
			title = ''

		code = memcache.get('AccessCookie')
		if not (accessCookie is not None and code is not None and code == accessCookie):
			self.redirect("/admin")
			return


		settingsArr = SettingsRecord.query().fetch(1)
		settings = None
		if len(settingsArr) > 0:
			settings = settingsArr[0]
		settings.setTempStatTitle(title)
		settings.startTempStat()
		settings.put()

		self.redirect('/player/clearTempStat')

		return

class StopIntervalStat(webapp2.RequestHandler):
	
	def get(self):

		accessCookie = self.request.cookies.get("AccessCode")

		code = memcache.get('AccessCookie')
		if not (accessCookie is not None and code is not None and code == accessCookie):
			self.redirect("/admin")
			return


		settingsArr = SettingsRecord.query().fetch(1)
		settings = None
		if len(settingsArr) > 0:
			settings = settingsArr[0]
		settings.stopTempStat()
		settings.put()

		return

class GetIntervalStatInfo(webapp2.RequestHandler):
	def get(self):

		ret = {}
		ret['error'] = gErrors[0]



		settingsArr = SettingsRecord.query().fetch(1)
		settings = None
		if len(settingsArr) > 0:
			settings = settingsArr[0]
			ret['intervalStatTitle'] = 	settings.getTempStatTitle()
			ret['intervalStatStartDate'] = 	str(settings.getTempStatStartDate())
			if not settings.tempStatIsActive():
				ret['intervalStatEndDate'] = str(settings.getTempStatEndDate())
		self.response.set_status(200)
		self.response.out.write(json.dumps(ret, ensure_ascii=False))



class AdjustShotsNumber(webapp2.RequestHandler):
	
	def get(self):
		deferred.defer(cron_jobs.AdjustShotsNumberFunc)
		self.response.out.write('Adjusting number of shots for players successfully initiated.')


class MainPage(webapp2.RequestHandler):
	
	def get(self):
		self.response.set_status(200)
		self.response.out.write("OK")
		return


application = webapp2.WSGIApplication(
									   [('/', MainPage),
									   ('/time', GetTime),
									   ('/player/add', PlayerAdd),
									   ('/player/get', PlayerGet),
									   ('/player/set', PlayerSet),
									   ('/player/addShots', PlayerAddShots),
									   ('/player/list.csv', PlayerGetCSV),
									   ('/player/top', PlayerGetTop),
									   ('/player/clearTempStat', PlayerClearTempStatData),
									   ('/message/add', MessageAdd),
									   ('/message/get', MessageGet),
									   ('/message/delete', MessageDelete),
									   ('/message/list.csv', MessageGetCSV),
									   ('/admin', GetAdminPanel),
									   ('/upload_audio', UploadAudioHandler),
									   ('/login', Login),
									   ('/changepassword', ChangeAdminPassword),
									   ('/startintervalstat', StartIntervalStat),
									   ('/stopintervalstat', StopIntervalStat),
									   ('/stopaudioshare', StopAudioShare),
									   ('/getblob/([^/]+)?', GetBlob),
									   ('/getaudiobgpath', GetAudioBgPath),
									   ('/getintervalstatinfo', GetIntervalStatInfo),
									   ('/sendpassword', SendAdminPasswordToEmail),
									   ('/cron/AdjustShotsNumber', AdjustShotsNumber),
									   ],
									   debug=False)                                       
