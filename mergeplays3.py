#!/usr/bin/env python3

""" parse dumpfile and push into rhythmbox

  merge last.fm data with rhythmbox
  ---------------------------------

  This script will examine a dump file from lastscrape
  then query your ampache database

  if it matches the artist, album and song
  it will update your databse to reflect each play

"""


import codecs
import csv
import os
import shutil
import sys
import xml.etree.ElementTree as etree

# Process/script checks
PROCESSPLAYS = None
PROCESSLOVED = None
WEHAVEMERGED = False
DBBACKUP = None

# File check
MERGEPLAYSFILE = False
MERGELOVEDFILE = False

# commandline arguments
FUZZYSEARCH = False
OVERWRITEDUMP = False

# Default file names
PLAYS = 'dump.txt'
LOVED = 'loved.txt'
PLAYLOG = 'mergeplays-playcount-PROCESSED.txt'
LOVELOG = 'mergeplays-loved-PROCESSED.txt'

# Default paths for rhythmbox & the user
HOMEFOLDER = os.getenv('HOME')
PATH = '/.local/share/rhythmbox/'
DB = (HOMEFOLDER + PATH + 'rhythmdb.xml')
DBBACKUP = (HOMEFOLDER + PATH + 'rhythmdb-backup-merge.xml')

# get dump file name from arguments
for arguments in sys.argv:
    if arguments[:3] == '/d:':
        print('\nUsing cmdline plays file ' + arguments[3:] + '\n')
        PLAYS = arguments[3:]
    if arguments[:3] == '/l:':
        print('\nUsing cmdline loved file ' + arguments[3:] + '\n')
        LOVED = arguments[3:]
    if arguments.lower() == '/fuzzy':
        print('\nIgnoring Album when searching for played tracks\n')
        FUZZYSEARCH = True
    if arguments.lower() == '/overwrite':
        print('\nReplacing dump with processed file\n')
        OVERWRITEDUMP = True

# decide whether to process
if os.path.isfile(PLAYS):
    PROCESSPLAYS = True
    # Don't overwrite yourself
    if PLAYS == PLAYLOG:
        PLAYLOG = PLAYLOG + '.tmp'
if os.path.isfile(LOVED):
    PROCESSLOVED = True
    if LOVED == LOVELOG:
        LOVELOG = LOVELOG + '.tmp'

# clear output files if they exist
if os.path.isfile(PLAYLOG):
    TMPFILE = codecs.open(PLAYLOG, "w", "utf8")
    TMPFILE.close()
if os.path.isfile(LOVELOG):
    TMPFILE = codecs.open(LOVELOG, "w", "utf8")
    TMPFILE.close()

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

# only start if the database has been backed up.
if PROCESSPLAYS or PROCESSLOVED:
    try:
        print('creating rhythmdb backup\n')
        shutil.copy(DB, DBBACKUP)
        DBBACKUP = True
    except FileNotFoundError:
        DBBACKUP = False
    except PermissionError:
        DBBACKUP = False

    # open the database
    print('Opening rhythmdb...\n')
    root = etree.parse(os.path.expanduser(DB)).getroot()
    items = [s for s in root.getiterator("entry")
             if s.attrib.get('type') == 'song']


# only process id db found and backup created.
if os.path.isfile(DB) and DBBACKUP:
    print('Connection Established\n')
    # search for plays by artist, track AND album
    if PROCESSPLAYS and os.path.isfile(PLAYS) and not FUZZYSEARCH:
        RBCACHE = []
        for entries in items:
            if entries.attrib.get('type') == 'song':
                data = {}
                for info in entries:
                    if info.tag in ('title', 'artist', 'album'):
                        data[info.tag] = info.text.lower()
            RBCACHE.append('%(title)s\t%(artist)s\t%(album)s' % data)
        WEHAVEMERGED = True
        print('Processing last.fm dump file\n')
        with open(PLAYS, 'r') as csvfile:
            # lastscrape is sorted recent -> oldest so reverse that
            # that way the database will have a lower ID for older tracks
            openfile = reversed(list(csv.reader(csvfile, delimiter='\t',)))
            for row in openfile:
                tmprow = []
                tmpsong = None
                tmpartist = None
                tmpalbum = None
                tmpentry = None
                tmpcount = None
                mergeplays = False
                foundartist = None
                foundalbum = None
                foundsong = None
                idx = None
                # using the last.fm data check for the same song in rhythmbox
                try:
                    test = row[0]
                except IndexError:
                    test = None
                if test:
                    # skip previously modified rows
                    if len(row) == 8:
                        if row[7] == '1':
                            idx = None
                            MERGEPLAYSFILE = True
                            mergeplays = True
                    if not mergeplays:
                        tmpcheck = (row[1].lower() + '\t' + row[2].lower() +
                                    '\t' + row[3].lower())
                        if tmpcheck in RBCACHE:
                            idx = RBCACHE.index(tmpcheck)
                # if the index is found, update the playcount
                if idx:
                    entry = items[idx]
                    for info in entry:
                        if info.tag == 'play-count':
                            tmpcount = int(info.text)
                            info.text = str(tmpcount + 1)
                            mergeplays = True
                    #print(row)
                    if not mergeplays:
                        insertplaycount = etree.SubElement(entry, 'play-count')
                        insertplaycount.text = '1'
                        mergeplays = True
                # write 0 to show nothing was written to the database
                if not mergeplays and test:
                    files = codecs.open(PLAYLOG, "a", "utf8")
                    files.write(str(row[0]) + '\t' + str(row[1]) + '\t' +
                                str(row[2]) + '\t' + str(row[3]) + '\t' +
                                str(row[4]) + '\t' + str(row[5]) + '\t' +
                                str(row[6]) + '\t' + '0')
                    files.write('\n')
                    files.close()
                # write 1 to show that the play was written to the database
                elif mergeplays and test:
                    files = codecs.open(PLAYLOG, "a", "utf8")
                    files.write(str(row[0]) + '\t' + str(row[1]) + '\t' +
                                str(row[2]) + '\t' + str(row[3]) + '\t' +
                                str(row[4]) + '\t' + str(row[5]) + '\t' +
                                str(row[6]) + '\t' + '1')
                    files.write('\n')
                    files.close()
        print('Plays from Last.fm have been inserted into the database.\n')
        if not OVERWRITEDUMP:
            print(PLAYLOG + ' contains all track that the script ' +
                  'has processed.\n')
        # Save changes
        print('saving changes')
        output = etree.ElementTree(root)
        output.write(os.path.expanduser(DB), encoding="utf-8")
    # For tracks that are missing album the fuzzy search is a good idea
    elif PROCESSPLAYS and os.path.isfile(PLAYS) and FUZZYSEARCH:
        choice = str(input('Warning: When using fuzzy search\n\nThis ' +
                           'will add a play for the first matching' +
                           ' Song + Artist in the Rhythmbox databa' +
                           'se\n(If you have multiple copies of th' +
                           'e same song this means it may match th' +
                           'e incorrect album)\n\nDo you accept?  ' +
                           '(Y/N): '))
        if choice:
            if not choice.lower()[0] == 'y':
                PROCESSPLAYS = False
        if PROCESSPLAYS:
            RBCACHE = []
            for entries in items:
                if entries.attrib.get('type') == 'song':
                    data = {}
                    for info in entries:
                        if info.tag in ('title', 'artist'):
                            data[info.tag] = info.text.lower()
                RBCACHE.append('%(title)s\t%(artist)s' % data)
            WEHAVEMERGED = True
            print('Processing last.fm dump file\n')
            with open(PLAYS, 'r') as csvfile:
                # lastscrape is sorted recent -> oldest so reverse that
                # that way the database will have a lower ID for older tracks
                openfile = reversed(list(csv.reader(csvfile, delimiter='\t',)))
                for row in openfile:
                    tmprow = []
                    tmpsong = None
                    tmpartist = None
                    tmpalbum = None
                    tmpentry = None
                    tmpcount = None
                    mergeplays = False
                    foundartist = None
                    foundalbum = None
                    foundsong = None
                    idx = None
                    # use last.fm data to check for the same song in rhythmbox
                    try:
                        test = row[0]
                    except IndexError:
                        test = None
                    if test:
                        # skip previously modified rows
                        if len(row) == 8:
                            if row[7] == '1':
                                idx = None
                                MERGEPLAYSFILE = True
                                mergeplays = True
                        if not mergeplays:
                            tmpcheck = row[1].lower() + '\t' + row[2].lower()
                            if tmpcheck in RBCACHE:
                                idx = RBCACHE.index(tmpcheck)
                    # if the index is found, update the playcount
                    if idx:
                        entry = items[idx]
                        for info in entry:
                            if info.tag == 'play-count':
                                tmpcount = int(info.text)
                                info.text = str(tmpcount + 1)
                                mergeplays = True
                        #print(row)
                        if not mergeplays:
                            insertplaycount = etree.SubElement(entry,
                                                               'play-count')
                            insertplaycount.text = '1'
                            mergeplays = True
                    # write 0 to show nothing was written to the database
                    if not mergeplays and test:
                        files = codecs.open(PLAYLOG, "a", "utf8")
                        files.write(str(row[0]) + '\t' + str(row[1]) + '\t' +
                                    str(row[2]) + '\t' + str(row[3]) + '\t' +
                                    str(row[4]) + '\t' + str(row[5]) + '\t' +
                                    str(row[6]) + '\t' + '0')
                        files.write('\n')
                        files.close()
                    # write 1 to show that the play was written to the database
                    elif mergeplays and test:
                        files = codecs.open(PLAYLOG, "a", "utf8")
                        files.write(str(row[0]) + '\t' + str(row[1]) + '\t' +
                                    str(row[2]) + '\t' + str(row[3]) + '\t' +
                                    str(row[4]) + '\t' + str(row[5]) + '\t' +
                                    str(row[6]) + '\t' + '1')
                        files.write('\n')
                        files.close()
            print('Fuzzy plays from Last.fm have been inserted into' +
                  ' the database.\n')
            if not OVERWRITEDUMP:
                print(PLAYLOG + ' contains all track that the script ' +
                      'has processed.\n')
            # Save changes
            print('saving changes')
            output = etree.ElementTree(root)
            output.write(os.path.expanduser(DB), encoding="utf-8")
    else:
        print('no play dump file found\n')
    if PROCESSLOVED and os.path.isfile(LOVED):
        RBCACHE = []
        for entries in items:
            if entries.attrib.get('type') == 'song':
                data = {}
                for info in entries:
                    if info.tag in ('title', 'artist'):
                        data[info.tag] = info.text.lower()
            RBCACHE.append('%(title)s\t%(artist)s' % data)
        WEHAVEMERGED = True
        print('Processing last.fm loved file\n')
        with open(LOVED, 'r') as csvfile:
            openfile = list(csv.reader(csvfile, delimiter='\t',))
            for row in openfile:
                tmprow = []
                tmpsong = None
                tmpartist = None
                tmpalbum = None
                tmpentry = None
                tmpcount = None
                mergeplays = False
                foundartist = None
                foundalbum = None
                foundsong = None
                idx = None
                # using the last.fm data check for the same song in rhythmbox
                try:
                    test = row[0]
                except IndexError:
                    test = None
                if test:
                    # skip previously modified rows
                    if len(row) == 7:
                        if row[6] == '1':
                            idx = None
                            MERGELOVEDFILE = True
                            mergeplays = True
                    if not mergeplays:
                        # match rows with cache
                        tmpcheck = row[1].lower() + '\t' + row[2].lower()
                        if tmpcheck in RBCACHE:
                            idx = RBCACHE.index(tmpcheck)
                # if the index is found, update the playcount
                if idx:
                    entry = items[idx]
                    for info in entry:
                        if info.tag == 'rating':
                            if not info.text == '5':
                                info.text = '5'
                                mergeplays = True
                    if not mergeplays:
                        insertplaycount = etree.SubElement(entry, 'rating')
                        insertplaycount.text = '5'
                        mergeplays = True
                # write 0 to show nothing was written to the database
                if not mergeplays and test:
                    files = codecs.open(LOVELOG, "a", "utf8")
                    files.write(str(row[0]) + '\t' + str(row[1]) + '\t' +
                                str(row[2]) + '\t' + str(row[3]) + '\t' +
                                str(row[4]) + '\t' + str(row[5]) + '\t' +
                                '0')
                    files.write('\n')
                    files.close()
                # write 1 to show that the play was written to the database
                elif mergeplays and test:
                    files = codecs.open(LOVELOG, "a", "utf8")
                    files.write(str(row[0]) + '\t' + str(row[1]) + '\t' +
                                str(row[2]) + '\t' + str(row[3]) + '\t' +
                                str(row[4]) + '\t' + str(row[5]) + '\t' +
                                '1')
                    files.write('\n')
                    files.close()

        print('Loved from Last.fm have been rated 5 stars in the database.\n')
        if not OVERWRITEDUMP:
            print(LOVELOG + ' contains the results of the script.\n')
    else:
        print('no loved tracks file found\n')
else:
    # there was a problem with the command
    print('FILE NOT FOUND.\nUnable to process\n')

if WEHAVEMERGED:
    # Save changes
    print('saving changes')
    output = etree.ElementTree(root)
    output.write(os.path.expanduser(DB), encoding="utf-8")

# move PLAYSs so you don't accidentally reprocess them
# loved tracks can only be loved once so there's no reason to move.
if PROCESSPLAYS and WEHAVEMERGED:
    # rename source if it hasn't got a mergeplays status column
    if not MERGEPLAYSFILE:
        print('renaming source dump file')
        shutil.move(PLAYS, (PLAYS + '.old'))
    # replace file with the latest processed copy
    if OVERWRITEDUMP:
        print('replacing original dumpfile with process markers')
        shutil.move(PLAYLOG, PLAYS)
if PROCESSLOVED and WEHAVEMERGED:
    # rename source if it hasn't got a mergeplays status column
    if not MERGELOVEDFILE:
        print('renaming source loved file')
        shutil.move(LOVED, (LOVED + '.old'))
    # replace file with the latest processed copy
    if OVERWRITEDUMP:
        print('and replacing original lovedfile with process markers')
        shutil.move(LOVELOG, LOVED)

print('Done')
