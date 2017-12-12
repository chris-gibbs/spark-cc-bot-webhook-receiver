#!/usr/bin/env python2
#  -*- coding: utf-8 -*-
"""A simple bot script.
This sample script leverages web.py (see http://webpy.org/).  By default the
web server will be reachable at port 8080 - append a different port when
launching the script if desired.  ngrok can be used to tunnel traffic back to
your server if you don't wish to expose your machine publicly to the Internet.
You must create a Spark webhook that points to the URL where this script is
hosted.  You can do this via the CiscoSparkAPI.webhooks.create() method.
Additional Spark webhook details can be found here:
https://developer.ciscospark.com/webhooks-explained.html
A bot must be created and pointed to this server in the My Apps section of
https://developer.ciscospark.com.  The bot's Access Token should be added as a
'SPARK_ACCESS_TOKEN' environment variable on the web server hosting this
script.
NOTE:  While this script is written to support Python versions 2 and 3, as of
the time of this writing web.py (v0.38) only supports Python 2.
Therefore this script only supports Python 2.
"""


from __future__ import print_function
from builtins import object

import json
import time
import web
import requests

from ciscosparkapi import CiscoSparkAPI, Webhook


# BitFinexAPIs
BitFinexAPI = 'https://api.bitfinex.com/v1/'
BitFinexTickerAPI = BitFinexAPI + 'ticker/'

# Coindesk APIs
CoindeskAPI = 'https://api.coindesk.com/v1/'
CoindeskBTC = CoindeskAPI + 'bpi/currentprice.json'

# Currency Conversion API
CurrencyConversionAPI = "https://api.fixer.io/latest"
# ?base=AUD&symbols=USD

# Global variables
urls = ('/sparkwebhook', 'webhook')       # Your Spark webhook should point to http://<serverip>:8080/sparkwebhook
app = web.application(urls, globals())    # Create the web application instance
api = CiscoSparkAPI()                     # Create the Cisco Spark API connection object

def GetCurrencyConversion (base, symbol, value):
    requestURL = CurrencyConversionAPI + '?base=' + base + '&symbols' + symbol  
    response = requests.get(requestURL, verify=False)
    responseJSON = json.loads(response.text)
    print(responseJSON)
    return str(round((float(value) * responseJSON['rates'][symbol]),4))

def GetBitFinexPrice(CoinType):
    priceURL = BitFinexTickerAPI + CoinType
    response = requests.get(priceURL, verify=False)
    response_dict = json.loads(response.text)
    return response_dict


class webhook(object):
    def POST(self):
        """Respond to inbound webhook JSON HTTP POSTs from Cisco Spark."""
        json_data = web.data()                                  # Get the POST data sent from Spark
        print("\nWEBHOOK POST RECEIVED:")
        #print(json_data, "\n")

        json_notification = json.loads(json_data)
        print(json.dumps(json_notification), "\n")
    
        webhook_obj = Webhook(json_notification)                    # Create a Webhook object from the JSON data

        #msg_data = api.messages.get(json_notification['data']['id'])

        room = api.rooms.get(webhook_obj.data.roomId)           # Get the room details
        message = api.messages.get(webhook_obj.data.id)         # Get the message details
        person = api.people.get(message.personId)               # Get the sender's details

        print("NEW MESSAGE IN ROOM '{}'".format(room.title))
        print("FROM '{}'".format(person.displayName))
        print("MESSAGE '{}'\n".format(message.text))

        # This is a VERY IMPORTANT loop prevention control step.
        # If you respond to all messages...  You will respond to the messages
        # that the bot posts and thereby create a loop condition.
        me = api.people.me()
        if message.personId == me.id:
            # Message was sent by me (bot); do not respond.
            print("Message sent by me. Return OK")
            return 'OK'
        else:
            # Message was sent by someone else; parse message and respond.
            print("Not ME")
            if "IOTA" in message.text:
                print ("Requesting IOTA rate")
                currentPriceJSON = GetBitFinexPrice("iotusd")
                convertedPrice = GetCurrencyConversion("USD","AUD",currentPriceJSON['last_price'])
                timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(float(currentPriceJSON['timestamp'])))
                message_text = "IOTA: $" + currentPriceJSON['last_price'] + ' (USD). $' + convertedPrice + '(AU). Timestamp: ' + timestamp
                response_message = api.messages.create(room.id, text=message_text)
            if "BTC" in message.text:
                print ("Requesting BTC rate")
                currentPriceJSON = GetBitFinexPrice("btcusd")
                convertedPrice = GetCurrencyConversion("USD","AUD",currentBTCPriceJSON['last_price'])
                timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(float(currentPriceJSON['timestamp'])))
                message_text = "IOTA: $" + currentPriceJSON['last_price'] + ' (USD). $' + convertedPrice + '(AU). Timestamp: ' + timestamp
                response_message = api.messages.create(room.id, text=message_text)
            if "DASH" in message.text:
                print ("Requesting BTC rate")
                currentPriceJSON = GetBitFinexPrice("dshusd")
                convertedPrice = GetCurrencyConversion("USD","AUD",currentPriceJSON['last_price'])
                timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(float(currentPriceJSON['timestamp'])))
                message_text = "DASH: $" + currentPriceJSON['last_price'] + ' (USD). $' + convertedPrice + '(AU). Timestamp: ' + timestamp
                response_message = api.messages.create(room.id, text=message_text)
            if "LITE" in message.text:
                print ("Requesting BTC rate")
                currentPriceJSON = GetBitFinexPrice("ltcusd")
                convertedPrice = GetCurrencyConversion("USD","AUD",currentPriceJSON['last_price'])
                timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(float(currentPriceJSON['timestamp'])))
                message_text = "LITECOIN: $" + currentPriceJSON['last_price'] + ' (USD). $' + convertedPrice + '(AU). Timestamp: ' + timestamp
                response_message = api.messages.create(room.id, text=message_text)
            if "zork" in message.text:
                print ("Requesting Zork")
                currentBTCPriceJSON = GetBitFinexPrice("btcusd")
                message_text = "NO! Just No " + person.displayName
                response_message = api.messages.create(room.id, text=message_text)
        return 'OK'


if __name__ == '__main__':
    # Start the web.py web server
    webhooks = api.webhooks.list()
    found = False

    for webhook in webhooks:
        if webhook.targetUrl == "http://chribbsdesign.com.au:8080/sparkwebhook":
            print(webhook)
            found = True

    if not found:
        api.webhooks.create("webhook", "http://chribbsdesign.com.au:8080/sparkwebhook","messages","created")
    app.run()