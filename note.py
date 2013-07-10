#!/usr/bin/env python

from datetime import datetime
""" 
Read opera notes file notes.adr
Structure of the file:
    #FOLDER     start of folder
    #NOTE       start of note
    -           end of folder (note: folder can be nested!)
"""


def parse(fp):
    """Parse notes.adr line by line.
    Return a list of notes, each note a dictionary
    """
    keys = ['ID', 'URL', 'UNIQUEID']
    notes = []
    tags = []
    for line in fp:
        line = line.strip()
        if line == '#FOLDER':
            note = {}
            isFolder = True
            notes.append(note)
        if line == '#NOTE':
            note = {}
            isFolder = False
            notes.append(note)
        lineSp = line.split('=', 1)
        if lineSp[0] in keys:
            note[lineSp[0]] = lineSp[1]
        if lineSp[0] == 'CREATED':
            note['CREATED'] = datetime.fromtimestamp(int(lineSp[1])).strftime('%Y/%m/%d')
        # Process NAME= lines
        # For folder, first line (before \x02\x02) to tag, rest goes to NOTE
        # For note, all to NOTE
        # Extract NOTE's first line as NAME (convert to ris as title)
        if lineSp[0] == 'NAME':
            if not isFolder:
                comment = lineSp[1]
            else:
                lineSp1 = lineSp[1].split('\x02\x02', 1) 
                tags.append(lineSp1[0])
                # If folder itself contains no information other than its name
                # Delete it
                if len(lineSp1) == 1:
                    notes.remove(note)
                    continue
                comment = lineSp1[1]
            name = comment.split('\x02\x02', 1)[0]
            note['NAME'] = name
            note['NOTE'] = comment.replace('\x02\x02', '\n')
            note['TAG'] = ','.join(tags)
        if line == '-':
            tags.pop()
    return notes 


def n2ris(note):
    '''Convert one note to ris format string
    OperaNote keys      ris keys
    NAME                TI
    URL                 UR
    NOTE                N1
    TAG                 KW
    ----
    TY - ELEC for note with url and TY - GEN for folder note, start a record
    ER - for end of a ris record
    '''
    n2risMap = {
            'NAME'    :   'TI',
            'URL'     :   'UR',
            'NOTE'    :   'N1',
            'TAG'     :   'KW',
            'CREATED' :   'PY',
            ## 'ID'        :   '??? - ',
            ## 'UNIQUEID'  :   '??? - '
            }
    res = ''
    if 'URL' in note:
        res += 'TY - ELEC\n'
    else:
        res += 'TY - GEN\n'
    for k in note:
        if k in n2risMap:
            res += n2risMap[k] + ' - {0}\n'.format(note[k])
    res += 'ER - \n'
    return res



def notes2ris(notes):
    """Write notes to ris string format.
    """
    res = ''
    for note in notes:
        res += n2ris(note)
    return res




fp = open('notes.adr','r')
notes = parse(fp)
fp.close()
fp = open('operaNote.ris', 'w')
fp.write(notes2ris(notes))
fp.close()

