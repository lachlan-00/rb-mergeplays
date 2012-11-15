#!/usr/bin/python
# coding: utf-8
#
# Copyright (C)2011 Lachlan de Waard
#
# --------------------------------------
# Rhythmbox Merge Plays from Last.fm
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


LASTFM_FILE = 'dump'
LAST_FM_FILE = codecs.open(LASTFM_FILE, "r", "utf8")
LAST_FM_LIST = []
COUNT_LIST = []
ERROR_LIST = []

print 'scanning dump file...'
# Read the last.fm list file
count = 0
for lines in LAST_FM_FILE:
    lines = lines.replace('\n', '')
    lines = lines.split('\t')
    lines[0] = 1
    lines.pop()
    lines.pop()
    lines.pop()
    LAST_FM_LIST.insert(count, lines)
    count = count + 1
LAST_FM_FILE.close()

print 'opening rhythmdb...'
root = (etree.parse(os.getenv('HOME') +
            '/.local/share/rhythmbox/rhythmdb.xml')).getroot()
items = root.getiterator("entry")

print 'merging dump file plays together...'
# should be converting to rhythmbox unicode... (will pull from rb-fileorganizer)
count = 0
for plays in LAST_FM_LIST:
    plays[0] = 1
    exist = False
    for songs in COUNT_LIST:
        if plays[2] == songs[2] and plays[1] == songs[1]:
            songs[0] = songs[0] + plays[0]
            exist = True
    if exist == False:
        COUNT_LIST.insert(count, plays)
    count = count + 1

# Search the database for the song and update play-count
print str(len(COUNT_LIST)) + ' items found.'
print 'starting search for play discrepancies'
count = 0

for songs in COUNT_LIST:
    for entries in items:
        foundtitle = False
        foundartist = False
        mergeplays = False
        if entries.attrib == {'type': 'song'}:
            for info in entries:
                if info.tag == 'title':
                    if (info.text).lower() == songs[1].lower():
                        foundtitle = True
                if info.tag == 'artist':
                    if (info.text).lower() == songs[2].lower():
                        foundartist = True
                if info.tag == 'play-count' and foundartist == True and (
                         foundtitle == True):
                    mergeplays = True
                    if not int(info.text) >= int(songs[0]):
                        changefile = '/home/user/mergeplays-changes.txt'
                        filechanges = codecs.open(changefile,
                                                    "a", "utf8")
                        filechanges.write('merging: ' + songs[2] + ' - ' +
                                            songs[1] + ' - ' + str(songs[0]) +
                                            '\n')
                        info.text = str(songs[0])
                        filechanges.close()
            # If play-count wasn't found insert it.
            # Rhythmbox seems to fix indentation and location on restart
            if foundartist == True and foundtitle == True and (
                    mergeplays == False):
                mergeplays = True
                insertplaycount = etree.SubElement(entries, 'play-count')
                insertplaycount.text = str(songs[0])
                filechanges = codecs.open('/home/user/mergeplays-changes.txt',
                                            "a", "utf8")
                filechanges.write('creating: ' + songs[2] + ' - ' + songs[1] +
                                     ' - ' + str(songs[0]) + '\n')
                filechanges.close()
    count = count + 1
    if str(count)[-2:] == '00':
        print str(count) + '/' + str(len(COUNT_LIST)) + ' files processed'

    #print ERROR_LIST
    if mergeplays == False:
        files = codecs.open('/home/user/mergeplays-error.txt', "a", "utf8")
        files.write(str(songs) + '\n')
        files.close()

# Save changes
output = etree.ElementTree(root)
output.write((os.getenv('HOME') + '/.local/share/rhythmbox/rhythmdb.xml'),
                    encoding="utf-8")

#print ERROR_LIST
#files = codecs.open('/home/user/mergeplays-error.txt', "w", "utf8")
#for items in ERROR_LIST:
#    files.write(str(items) + '\n')
#files.close()
print 'done'
