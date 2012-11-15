#!/usr/bin/python
# coding: utf-8
#
# Copyright (C)2011 Lachlan de Waard
#
# --------------------------------------
# Rhythmbox make 'Loved' tracks from Last.fm 5 stars
# --------------------------------------
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.	
#	
# This program is distributed in the hope that it will be useful,	
# but WITHOUT ANY WARRANTY; without even the implied warranty of	
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the	
# GNU General Public License for more details.	
#
# You should have received a copy of the GNU General Public License	
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import codecs
import xml
import xml.etree.ElementTree as etree

from xml.etree.ElementTree import tostring

LASTFM_FILE = 'lovedtracks'
LAST_FM_FILE = codecsopen(LASTFM_FILE,"r", , "utf8")
LAST_FM_LIST = []

count = 0

# Read the last.fm lovedtracks file
for lines in LAST_FM_FILE:
    lines = lines.replace('\n','')
    lines = lines.split('\t')
    LAST_FM_LIST.insert(count,lines)
    count = count + 1
LAST_FM_FILE.close()

root = (etree.parse(os.getenv('HOME')+'/.local/share/rhythmbox/rhythmdb.xml')).getroot()
items = root.getiterator("entry")

# Search the database for the song and update rating
for songs in LAST_FM_LIST:
    for entries in items:
        foundtitle = False
        foundartist = False
        mergelove = False
        if entries.attrib == {'type': 'song'}:
            for info in entries:
                if info.tag == 'title':
                    if info.text == songs[1]:
                        foundtitle = True
                if info.tag == 'artist':
                    if info.text == songs[2]:
                        foundartist = True
                if info.tag == 'rating' and foundartist == True and foundtitle == True:
                    if not info.text == '5':
                        print ('Loved: ' + songs[2] + ' - ' + songs[1])
                        mergelove = True
                        info.text = '5'
            # If rating wasn't found insert it. 
            # Rhythmbox seems to fix indentation and location on restart
            if foundartist == True and foundtitle == True and mergelove == False:
                mergelove = True
                insertloved = etree.SubElement(entries, 'rating')
                insertloved.text = '5'
                print ('creating: ' + songs[2] + ' - ' + songs[1])

# Save changes
output = etree.ElementTree(root)
output.write((os.getenv('HOME')+'/.local/share/rhythmbox/rhythmdb.xml'), encoding="utf-8")
