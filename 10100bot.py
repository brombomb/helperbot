#!/usr/bin/env python

import re
import sys
import socket
import string
import urllib
import urlparse
import urllib2
import json

HOST = "irc.gamesurge.net"
#HOST = "irc.freenode.net"
PORT = 6667
NAME = "helper10100"
IDENT = "10100helper"
REALNAME = "helper10100"
CHAN = "#10100"
#CHAN = "#10100-test"
JOINED = False
DEBUG = False

SPOT = "http://ws.spotify.com/lookup/1/.json?uri=%s" # Spotify
YTS = "http://gdata.youtube.com/feeds/api/videos?max-results=1&alt=json&q=%s" # Youtube Search
YTA = "https://gdata.youtube.com/feeds/api/videos/%s?v=2&alt=json" #Youtube API
IMGKEY = "8d8691c8d0d134c" # Imgur Secret
IMGAPI = "https://api.imgur.com/3/gallery/image%s" # Imgur API
WEATHER = "http://api.wunderground.com/api/05e5f1ea04bb9f30/conditions/q/%s.json" # Wunderground API

# Parse an IRC message line as defined by this format
#     :<prefix> <command> <params> :<trailing>
def parseLine(line):
    nick = ''
    command = ''
    message = line
    # Grab the User Nickname
    try:
        if line.find(':') == 0:
            userEnd = line.find(' ')
            user = line[1:userEnd - 1]
            user = user.split('!')
            nick = user[0]
    except:
        pass

    # Grab the message
    # Assume the first ' :' after the very first character (which should be a :
    try:
        messageStart = line.find(' :', 1)
        if messageStart != 1:
            message = line[messageStart + 2:]
        else:
            messageStart = line.length()
    except:
        pass

    # Grab the command now
    try:
        commandAndParams = line[userEnd + 1:messageStart - 1].split(' ')
        command = commandAndParams[0]
    except:
        pass

    return nick, command, message

# Send a message to the channel/user
def msg(txt, nick = ''):
    if nick != '':
        irc.send('PRIVMSG %s :%s \r\n' % (nick, txt))
    else:
        irc.send('PRIVMSG %s :%s \r\n' % (CHAN, txt))

# send a command to IRC
#def cmd(command):
#    irc.send('%s %s\r\n' % (command, CHAN))

def startup():
    irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    irc.connect((HOST,PORT))
    print 'Attempting to connect to %s %s' % (HOST, CHAN)
    #print irc.recv(4096)
    irc.send("NICK %s\r\n" % NAME)
    irc.send("USER %s %s bla :%s\r\n" % (IDENT, HOST, REALNAME))
    return irc

irc = startup()

while True:
    data = irc.recv(4096)
    nick, command, message = parseLine(data)
    if DEBUG:
        print "\n\n============="
        print data
        print "user: " + nick
        print "cmnd: " + command
        print "mesg: " + message

    # Wait for numeric 251 which is Number online
    if data.find('251') != -1 and JOINED == False:
        irc.send("JOIN :%s\r\n" % CHAN)
        JOINED = True

    # System Ping/Pong
    if data.find('PING :') != -1:
        irc.send('PONG ' + data.split()[1] + '\r\n')

    
#    # If someone kicks us try and rejoin.
#    if data.find('KICK') != -1:
#        cmd('JOIN :')

#    # Allow someone to make us quite
#    if data.find('!helper quit') != -1:
#        irc.send('PRIVMSG %s :Fine, if you dont want me\r\n' % CHAN)
#        irc.send('QUIT\r\n')
#        sys.exit(1)

    # Sanity check to see if alive
    if message.find('hi helper') != -1:
        msg("Hello %s" % nick)

    if (message.find('http') != -1 and JOINED):
        urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', message)
        file = open('urls.txt', 'a')
        file.write("\n".join(urls) + "\n");
        file.close()
        #msg("saving link")


    # Lookup Spotify Info, then try and find Youtube Video
    if message.find('spotify:') != -1:
        try:
            match = message[message.find('spotify:'):].strip()
            file = open('spotify.txt', 'a')
            file.write(match + "\n")
            file.close()
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
    if message.find('http://www.youtube.com/watch?v=') != -1:
        chat = message.split(':', 2)
        chat = chat[2] #Only keep the message
        qs = urlparse.parse_qs(chat[chat.find('?')+1:]);
        try:
            response = urllib2.urlopen(YTA % qs['v'][0].strip())
            vid = json.load(response)
            msg(vid['entry']['title']['$t'])
        except:
            print data

    # Look up Imgur Titles
    if message.find('imgur.com/') != -1:
        url = message[message.find('http'):] # Find the start of the URL
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

    if message.find('!weather') != -1:
        try:
            zip = message[message.find('!weather') + 9:] # grab the zip to end of line.
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

    if message.find('!spotify') != -1:
        msg("http://brombomb.com/10100bot/spotify.txt")

    if message.find('!src') != -1:
        msg("http://brombomb.com/10100bot/10100bot.py")

    if message.find('!help') != -1:
        msg("I will try to parse spotify, youtube, and imgur urls to the best I can.  If I can't I'll rage quit. pm brombomb with the link that made me rage quit and he'll fix it (maybe). Other commands !weather {zip}, !src")
