#!/usr/bin/env python
#-*- coding: utf-8 -*-

""" Rhythmbox Merge Plays from Last.fm
    ----------------Authors----------------
    Lachlan de Waard <lachlan.00@gmail.com>
    ----------------Licence----------------
    GNU General Public License version 3

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""

import sys
import os
import shutil
import codecs
import xml
import xml.etree.ElementTree as etree

from xml.etree.ElementTree import tostring

try:
    if sys.argv:
        LASTFM_FILE = sys.argv[1]
    else:
        LASTFM_FILE = 'dump.txt'
except:
    LASTFM_FILE = 'dump.txt'
LAST_FM_FILE = codecs.open(LASTFM_FILE, "r", "utf8")
LAST_FM_LIST = []
COUNT_LIST = []
ERROR_LIST = []
HOMEFOLDER = os.getenv('HOME')

urlascii = ('%', "#", ';', ' ', '"', '<', '>', '?', '[', '\\',
            "]", '^', '`', '{', '|', '}', '€', '‚', 'ƒ', '„',
            '…', '†', '‡', 'ˆ', '‰', 'Š', '‹', 'Œ', 'Ž', '‘',
            '’', '“', '”', '•', '–', '—', '˜', '™', 'š', '›',
            'œ', 'ž', 'Ÿ', '¡', '¢', '£', '¥', '|', '§', '¨',
            '©', 'ª', '«', '¬', '¯', '®', '¯', '°', '±', '²',
            '³', '´', 'µ', '¶', '·', '¸', '¹', 'º', '»', '¼',
            '½', '¾', '¿', 'À', 'Á', 'Â', 'Ã', 'Ä', 'Å', 'Æ',
            'Ç', 'È', 'É', 'Ê', 'Ë', 'Ì', 'Í', 'Î', 'Ï', 'Ð',
            'Ñ', 'Ò', 'Ó', 'Ô', 'Õ', 'Ö', 'Ø', 'Ù', 'Ú', 'Û',
            'Ü', 'Ý', 'Þ', 'ß', 'à', 'á', 'â', 'ã', 'ä', 'å',
            'æ', 'ç', 'è', 'é', 'ê', 'ë', 'ì', 'í', 'î', 'ï',
            'ð', 'ñ', 'ò', 'ó', 'ô', 'õ', 'ö', '÷', 'ø', 'ù',
            'ú', 'û', 'ü', 'ý', 'þ', 'ÿ', '¦')
urlcode = ('%25', '%23', '%3B', '%20', '%22', '%3C', '%3E', '%3F',
           '%5B', '%5C', '%5D', '%5E', '%60', '%7B', '%7C', '%7D',
           '%E2%82%AC', '%E2%80%9A', '%C6%92', '%E2%80%9E',
           '%E2%80%A6', '%E2%80%A0', '%E2%80%A1', '%CB%86',
           '%E2%80%B0', '%C5%A0', '%E2%80%B9', '%C5%92', '%C5%BD',
           '%E2%80%98', '%E2%80%99', '%E2%80%9C', '%E2%80%9D',
           '%E2%80%A2', '%E2%80%93', '%E2%80%94', '%CB%9C',
           '%E2%84%A2', '%C5%A1', '%E2%80%BA', '%C5%93', '%C5%BE',
           '%C5%B8', '%C2%A1', '%C2%A2', '%C2%A3', '%C2%A5',
           '%7C', '%C2%A7', '%C2%A8', '%C2%A9', '%C2%AA',
           '%C2%AB', '%C2%AC', '%C2%AF', '%C2%AE', '%C2%AF',
           '%C2%B0', '%C2%B1', '%C2%B2', '%C2%B3', '%C2%B4',
           '%C2%B5', '%C2%B6', '%C2%B7', '%C2%B8', '%C2%B9',
           '%C2%BA', '%C2%BB', '%C2%BC', '%C2%BD', '%C2%BE',
           '%C2%BF', '%C3%80', '%C3%81', '%C3%82', '%C3%83',
           '%C3%84', '%C3%85', '%C3%86', '%C3%87', '%C3%88',
           '%C3%89', '%C3%8A', '%C3%8B', '%C3%8C', '%C3%8D',
           '%C3%8E', '%C3%8F', '%C3%90', '%C3%91', '%C3%92',
           '%C3%93', '%C3%94', '%C3%95', '%C3%96', '%C3%98',
           '%C3%99', '%C3%9A', '%C3%9B', '%C3%9C', '%C3%9D',
           '%C3%9E', '%C3%9F', '%C3%A0', '%C3%A1', '%C3%A2',
           '%C3%A3', '%C3%A4', '%C3%A5', '%C3%A6', '%C3%A7',
           '%C3%A8', '%C3%A9', '%C3%AA', '%C3%AB', '%C3%AC',
           '%C3%AD', '%C3%AE', '%C3%AF', '%C3%B0', '%C3%B1',
           '%C3%B2', '%C3%B3', '%C3%B4', '%C3%B5', '%C3%B6',
           '%C3%B7', '%C3%B8', '%C3%B9', '%C3%BA', '%C3%BB',
           '%C3%BC', '%C3%BD', '%C3%BE', '%C3%BF', '%C2%A6')

rbdb_rep = ('%28', '%29', '%2B', '%27', '%2C', '%3A', '%21',
            '%24', '%26', '%2A', '%2C', '%2D', '%2E', '%3D',
            '%40', '%5F', '%7E')
rbdb_itm = ('(', ')', '+', "'", ',', ':', '!', '$', '&', '*',
            ',', '-', '.', '=', '@', '_', '~')

# Replace Characters with UTF code value
def set_url(string):
    """ Set RhythmDB style string """
    count = 0
    while count < len(urlascii):
        string = string.replace(urlascii[count], urlcode[count])
        count = count + 1
    return string

def set_ascii(string):
    """ Change unicode codes back to asscii for RhythmDB """
    count = 0
    while count < len(rbdb_rep):
        string = string.replace(rbdb_rep[count],
                                rbdb_itm[count])
        count = count + 1
    return string


print 'scanning dump file...'
# Read the last.fm list file
count = 0
for lines in LAST_FM_FILE:
    #lines = set_url(lines)
    lines = set_ascii(lines)
    lines = lines.replace('\n', '')
    lines = lines.split('\t')
    lines[0] = 1
    lines.pop()
    lines.pop()
    lines.pop()
    LAST_FM_LIST.insert(count, lines)
    count = count + 1
LAST_FM_FILE.close()

print 'creating db backup'
PATH = '/.local/share/rhythmbox/'
DB = (os.getenv('HOME') + PATH + 'rhythmdb.xml')
shutil.copy(DB, os.getenv('HOME') + PATH + 'rhythmdb-backup-merge.xml')

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
                        changefile = HOMEFOLDER + '/mergeplays-changes.txt'
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
                filechanges = codecs.open(HOMEFOLDER + '/mergeplays-changes.txt',
                                            "a", "utf8")
                filechanges.write('creating: ' + songs[2] + ' - ' + songs[1] +
                                     ' - ' + str(songs[0]) + '\n')
                filechanges.close()
    count = count + 1
    if str(count)[-2:] == '00':
        print str(count) + '/' + str(len(COUNT_LIST)) + ' files processed'

    #print ERROR_LIST
    if mergeplays == False:
        files = codecs.open(HOMEFOLDER + '/mergeplays-error.txt', "a", "utf8")
        files.write(str(songs) + '\n')
        files.close()

# Save changes
output = etree.ElementTree(root)
output.write((HOMEFOLDER + '/.local/share/rhythmbox/rhythmdb.xml'),
             encoding="utf-8")

#print ERROR_LIST
#files = codecs.open(HOMEFOLDER + '/mergeplays-error.txt', "w", "utf8")
#for items in ERROR_LIST:
#    files.write(str(items) + '\n')
#files.close()
print 'done'
