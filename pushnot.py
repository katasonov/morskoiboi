import sys
import models
from utils import *
import logging
import urllib
import json
import urllib2

SERVER_API_KEY = 'AIzaSyAx7mw84u8Vpp6lfvM4dIoKe20QdpnlLyA'

class PushNotificationBatchSender(models.IPlayersProcessor):

	def __init__(self, title, message, language):
		self.title = title
		self.message = message
		self.language = language

	def do(self, players):
		if len(players) < 1:
				return
		logging.info("PushNotificationBatchSender:do:")
		logging.info("for " + str(len(players)) + " players")
		regIds=[]
		for p in players:
			if p.pushNotificationUid is None or len(p.pushNotificationUid) < 1:
				continue
			if p.language != self.language:
				continue
			regIds = regIds + [p.pushNotificationUid]
		if len(regIds) < 1:
			return
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

	