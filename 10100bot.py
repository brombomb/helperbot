#!/usr/bin/env python

import sys
import socket
import string
import urllib
import urlparse
import urllib2
import json

HOST="irc.gamesurge.net"
#HOST="irc.freenode.net"
PORT=6667
NICK="helper10100"
IDENT="10100helper"
REALNAME="helper10100"
CHAN="#10100"
#CHAN="#10100-test"

# Spotify Lookup URL
SPOT="http://ws.spotify.com/lookup/1/.json?uri=%s"
YTS="http://gdata.youtube.com/feeds/api/videos?max-results=1&alt=json&q=%s"
YTA="https://gdata.youtube.com/feeds/api/videos/%s?v=2&alt=json"
IMGKEY="8d8691c8d0d134c"
IMGAPI="https://api.imgur.com/3/gallery/image%s"
WEATHER="http://api.wunderground.com/api/05e5f1ea04bb9f30/conditions/q/%s.json"

def msg(txt): # Send a message to the channel
    irc.send('PRIVMSG %s :%s \r\n' % (CHAN, txt))

readbuffer=""

irc=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
irc.connect((HOST,PORT))
print 'Attempting to connect to ' + HOST + ' ' + CHAN
print irc.recv(4096)
irc.send("NICK %s\r\n" % NICK)
irc.send("USER %s %s bla :%s\r\n" % (IDENT, HOST, REALNAME))
irc.send("JOIN :%s\r\n" % CHAN)

while True:
    data = irc.recv(4096)
#    print data

    if data.find('PING') != -1:
        irc.send('PONG ' + data.split()[1] + '\r\n')

#    if data.find('!helper quit') != -1:
#        irc.send('PRIVMSG %s :Fine, if you dont want me\r\n' % CHAN)
#        irc.send('QUIT\r\n')
#        sys.exit(1)

    if data.find('hi helper') != -1:
        irc.send('PRIVMSG %s :Hello World...\r\n' % CHAN)

    if data.find('KICK') != -1:
        irc.send('JOIN %s\r\n' % CHAN)

    # Lookup Spotify Track Info, and Find Youtube Video
    if data.find('spotify:') != -1:
        try:
            match = data[data.find('spotify:'):].strip()
            response = urllib2.urlopen(SPOT % match)
            info = json.load(response)
            response.close()
            song = info['track']['artists'][0]['name'] + ' - ' + info['track']['name']
            response = urllib2.urlopen(YTS % urllib.quote(song))
            vid = json.load(response)
            response.close()
            try:
                ytvid = vid['feed']['entry'][0]['link'][0]['href']
                msg(song + ' ' +  ytvid[:ytvid.find('&')])
            except:
                msg(song)
        except:
            print data

    # Lookup Youtube Video Titles
    if data.find('http://www.youtube.com/watch?v=') != -1:
        chat = data.split(':', 2)
        chat = chat[2] #Only keep the message
        qs = urlparse.parse_qs(chat[chat.find('?')+1:]);
        try:
            response = urllib2.urlopen(YTA % qs['v'][0].strip())
            vid = json.load(response)
            msg(vid['entry']['title']['$t'])
        except:
            print data

    # Look up Imgur Titles
    if data.find('imgur.com/') != -1:
        url = data[data.find('http'):] # Find the start of the URL
        if url.find(' ') != -1: # We might have extra text after the link
            url = url[:url.find(' ')] # imgur links don't have spaces so find next space
        url = url[url.rfind('/'):] # grab the last part of the image
        if url.find('.') != -1: # We need to strip the image extension
            url = url[:url.rfind('.')]
        req = urllib2.Request(IMGAPI % url) 
        req.add_header('Authorization', 'Client-ID ' + IMGKEY)

        try:
            response = urllib2.urlopen(req)
            img = json.load(response)
            msg(img['data']['title'])
        except:
            print data

    if data.find('!weather') != -1:
        try:
            zip = data[data.find('!weather') + 9:] # grab the zip to end of line.
            response = urllib2.urlopen(WEATHER % zip.strip())
            weather = json.load(response)
            location = weather['current_observation']['observation_location']['full']
            text = weather['current_observation']['weather']
            temp = weather['current_observation']['temp_f']
            feels = weather['current_observation']['feelslike_f']
            wind = weather['current_observation']['wind_string']

            msg("Currently in %s: %s and %dF feels like %dF.  Winds %s" % (location, text, int(temp), int(feels), wind))
        except:
            print data

    if data.find('!src') != -1:
        msg("http://brombomb.com/10100bot/10100bot.py")

    if data.find('!help') != -1:
        msg("I will try to parse spotify, youtube, and imgur urls to the best I can.  If I can't I'll rage quit. pm brombomb with the link that made me rage quit and he'll fix it (maybe). Other commands !weather {zip}, !src")

