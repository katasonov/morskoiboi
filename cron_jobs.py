import logging
from models import PlayerRecord

from google.appengine.ext import deferred
from google.appengine.ext import ndb

BATCH_SIZE = 100  # ideal batch size may vary based on entity size.

def AdjustShotsNumberFunc(cursor=None, num_updated=0):
    players, next_curs, more = PlayerRecord.query().fetch_page(\
        BATCH_SIZE, start_cursor=cursor)

    to_put = []
    for p in players:
        # In this example, the default values of 0 for num_votes and avg_rating
        # are acceptable, so we don't need this loop.  If we wanted to manually
        # manipulate property values, it might go something like this:
        if p.shots < 120:
            p.shots = 120
            to_put.append(p)    

    if to_put:
        ndb.put_multi(to_put)
        num_updated += len(to_put)
        logging.debug(
            'Put %d entities to Datastore for a total of %d',
            len(to_put), num_updated)
        deferred.defer(
            AdjustShotsNumberFunc, cursor=next_curs, num_updated=num_updated)
    else:
        logging.debug(
            'Shots number adjusted for %d players!', num_updated)

def ClearPlayerTempStatValues(cursor=None, num_updated=0):
    players, next_curs, more = PlayerRecord.query().fetch_page(\
        BATCH_SIZE, start_cursor=cursor)

    to_put = []
    for p in players:
        # In this example, the default values of 0 for num_votes and avg_rating
        # are acceptable, so we don't need this loop.  If we wanted to manually
        # manipulate property values, it might go something like this:
        p.totalPlayTimeT = 0
        p.totalWinsT = 0
        p.totalLosesT = 0
        p.totalMadeShotsT = 0
        p.totalGamesT = 0
        p.winsToGamesT = 0
        to_put.append(p)
        
    if to_put:
        ndb.put_multi(to_put)
        num_updated += len(to_put)
        logging.debug(
            'Put %d entities to Datastore for a total of %d',
            len(to_put), num_updated)
        deferred.defer(
            ClearPlayerTempStatValues, cursor=next_curs, num_updated=num_updated)
    else:
        logging.debug(
            'Player temp stat data cleared for %d players!', num_updated)


