# -*- coding: utf-8 -*-
#
#       Copyright (C) 2016
#       On-Tapp-Networks Limited

import xbmc
import xbmcaddon
import xbmcgui

import json
import os

import utilsTOOLS as utils
import sfile

import sys
path = utils.OTT_HOME
sys.path.insert(0, path)

import playlists
import dixie
import channel as dixieChannel


OTT_TITLE    = utils.OTT_TITLE
OTT_ADDON    = utils.OTT_ADDON
OTT_PROFILE  = utils.OTT_PROFILE
OTT_CHANNELS = utils.OTT_CHANNELS


ADDONID  = utils.ADDONID
ADDON    = utils.ADDON
HOME     = utils.HOME
PROFILE  = utils.PROFILE
VERSION  = utils.VERSION
ICON     = utils.ICON
FANART   = utils.FANART
DATAPATH = utils.DATAPATH


def mergeLineups(label, isSF, sfZip, url):
    if not utils.DialogYesNo('Are you sure you want to continue and merge channels?', 'We highly recommend you back-up your channel line-up first', 'THERE IS NO UNDO!'):
        return

    path    = os.path.join(OTT_PROFILE, 'chanstomerge')
    zipfile = os.path.join(OTT_PROFILE, 'tomerge.zip')

    if isSF == 'true':
        utils.installSF(sfZip)

    utils.download(url, path, zipfile)

    toMerge  = os.path.join(OTT_PROFILE, 'chanstomerge', 'channels')
    channels = getAllChannels(toMerge)

    merge = []
    for channel in channels:
        chTag    = ''
        chTitle  = channel[2].title
        chStream = channel[2].streamUrl

        merge.append([chTag, chTitle, chStream])

    OTT_ADDON.setSetting('dixie.lineup', label)

    return _mergeLineups(merge)


def createINIFileLineup():
    utils.DialogOK('Please choose an INI file to create a channel line-up from.', 'This may take a while, please be patient')

    lineup = readINIFile()
    return _createLineup(lineup)


def createIPTVLineup():
    utils.DialogOK('We will now create a channel line-up from your IPTV settings', 'This may take a while, please be patient')

    plfile = os.path.join(OTT_PROFILE, 'plists')

    if os.path.exists(plfile):
        sfile.remove(plfile)

    lineup = playlists.loadPlaylists()

    return _createLineup(lineup)


def _createLineup(lineup):
    utils.deleteCFG()

    dp = xbmcgui.DialogProgress()
    dp.create('On-Tapp.TV', 'Creating channels...')

    OPEN_OTT  = '_OTT['
    CLOSE_OTT = ']OTT_'

    channels = dixie.getAllChannels()

    update = 0

    dp.update(update, 'Adding links to channels...', 'This may take a few minutes.')
    toEdit   = {}
    found    = []

    nItem = len(lineup)

    if nItem == 0:
        utils.DialogOK('We cannot detect any links.', 'Please check your settings.')
        return

    for idx, item in enumerate(lineup):
        lineupTag   = item[0]
        cleanTitle  = dixie.cleanPrefix(item[1])
        lineupTitle = dixie.mapChannelName(cleanTitle)
        lineupLabel = lineupTag + lineupTitle

        lineupStream = item[2]

        update = 100 * idx / nItem
        dp.update(update, 'Adding links to channels...', 'Processing %s' % lineupLabel)
        if dp.iscanceled():
            dp.close()
            return

        for channel in channels:
            chTitle  = channel[2].title

            FUZZY = False
            EXACT = dixie.exactMatch(chTitle, lineupTitle)

            if not EXACT:
                FUZZY = dixie.fuzzyMatch(chTitle, lineupTitle)

            EXACT = dixie.exactMatch(chTitle, lineupTitle) == True
            FUZZY = dixie.fuzzyMatch(chTitle, lineupTitle) == True

            if EXACT or FUZZY:
                if item[1] not in found:
                    found.append(item[1])

                urlStream = OPEN_OTT + lineupLabel.upper() + CLOSE_OTT + lineupStream

                if chTitle in toEdit:
                    toEdit[chTitle].append(urlStream)
                else:
                    toEdit[chTitle] = [urlStream]

            if EXACT:
                break

    update = 100

    dp.update(update, 'Adding links to channels...', 'Saving Channel Line-up...')

    toWrite = []

    for channel in channels:
        chan = channel[2]

        if chan.title in toEdit:
            chan.streamUrl = '|'.join(toEdit[chan.title])
            toWrite.append(channel)
        else:
            chan.visible = 0
            toWrite.append(channel)

    dp.update(update, 'Adding links to channels...', 'Saving Channel Line-up...')
    dp.close()

    from channel import Channel
    for idx, item in enumerate(lineup):
        if item[1] not in found:
            tag   = item[0]
            title = item[1]
            label = tag + title
            chID  = dixie.CleanFilename(title)

            streamUrl = OPEN_OTT + label + CLOSE_OTT + item[2]

            channelToAdd   = Channel(chID, title, streamUrl=streamUrl, desc=title, categories='00. Unmatched', userDef=1)
            newChannelItem = [idx, chID, channelToAdd]
            toWrite.append(newChannelItem)

    writeChannelsToFile(toWrite, updateWeight=True)

    utils.DialogOK('Your Channel Line-up has now been created.', 'If there are any mis-matches due to similar names,', 'You can edit the channels in the EPG.')
    return


def _mergeLineups(lineup):
    utils.deleteCFG()

    dp = xbmcgui.DialogProgress()
    dp.create('On-Tapp.TV', 'Creating channels...')

    channels = dixie.getAllChannels()

    update = 0

    dp.update(update, 'Adding links to channels...', 'This may take a few minutes.')

    toWrite = []

    nItem = len(lineup)

    if nItem == 0:
        utils.DialogOK('We cannot detect any links.', 'Please check your settings.')
        return

    for idx, item in enumerate(lineup):
        lineupTag    = item[0]
        lineupTitle  = item[1]
        lineupStream = item[2]

        update = 100 * idx / nItem
        dp.update(update, 'Adding links to channels...', 'Processing %s' % lineupTitle)
        if dp.iscanceled():
            dp.close()
            return

        for channel in channels:
            chTitle  = channel[2].title
            chStream = channel[2].streamUrl

            if lineupTitle == chTitle:
                if (len(chStream) > 0) and (len(lineupStream) > 0):
                    channel[2].streamUrl = chStream + '|' + lineupStream
                    toWrite.append(channel)

                elif (len(chStream) == 0) and (len(lineupStream) > 0):
                    channel[2].streamUrl = lineupStream
                    channel[2].visible   = '1'
                    toWrite.append(channel)

    update = 100

    dp.update(update, 'Adding links to channels...', 'Saving Channel Line-up...')

    writeChannelsToFile(toWrite, updateWeight=True)

    utils.DialogOK('Your Channel Line-ups have now been merged.', 'If there are any mis-matches due to similar names,', 'You can edit the channels in the EPG.')
    return


def updateChannel(dixieChannel, id):
    path = os.path.join(OTT_CHANNELS, id)

    return dixieChannel.writeToFile(path)


def writeChannelsToFile(channelList, updateWeight=True):
    weight = 1

    for item in channelList:
        id = item[1]
        ch = item[2]

        if updateWeight:
            ch.weight = weight
            weight   += 1

        updateChannel(ch, id)


def readINIFile():
    # import glob
    # ini   = os.path.join(OTT_PROFILE, 'ini', '*.*')
    # files = glob.glob(ini)
    #
    # for item in files:
    #     fullPath = os.path.split(item)
    #     iniPath  = fullPath[0]
    #     iniFile  = fullPath[1]
    #     dixie.log('===== PATH =====')
    #     dixie.log(iniPath)
    #     dixie.log('===== FILE =====')
    #     dixie.log(iniFile)

    # dialog = xbmcgui.Dialog().browse(1, 'Choose an INI File', os.path.join(OTT_PROFILE, 'ini'))
    # PATH = os.path.join(OTT_PROFILE, 'ini', )
    # inipath = os.path.join(OTT_PROFILE, 'ini')

    inipath = xbmc.translatePath(os.path.join(OTT_PROFILE, 'ini'))

    PATH = xbmcgui.Dialog().browse(1, 'Choose an INI File', 'files', mask='.ini')

    try:
        with open(xbmc.translatePath(PATH)) as content:
            items = content.readlines()

            tag = 'INI: '
            lineup = []
            for item in items:
                if '=' in item:
                    chans = item.split('=', 1)
                    chan  = chans[0]
                    strm  = chans[1].replace('\n', '')
                    if len(strm) != 0:
                        lineup.append([tag, chan, strm])

            return lineup
    except:
        return []


def getAllChannels(folder):
    channels = []

    try:
        current, dirs, files = sfile.walk(folder)
    except Exception, e:
        return channels

    for file in files:
        channels.append(file)

    sorted = []

    for id in channels:
        channel = getChannelFromFile(id, folder)

        sorter  = channel.weight

        sorted.append([sorter, id, channel])

    sorted.sort()

    return sorted


def getChannelFromFile(id, folder):
    from channel import Channel
    path = os.path.join(folder, id)

    if not sfile.exists(path):
        return None

    cfg = sfile.readlines(path)

    return Channel(cfg)


def main(cmd):
    if cmd == 'createIPTVLineup':
        createIPTVLineup()


if __name__ == '__main__':
    cmd = sys.argv[1]
    main(cmd)


