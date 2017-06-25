# -*- coding: utf-8 -*-
#
#       Copyright (C) 2014
#       Sean Poyser (seanpoyser@gmail.com)
#
#  This Program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2, or (at your option)
#  any later version.
#
#  This Program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with XBMC; see the file COPYING.  If not, write to
#  the Free Software Foundation, 675 Mass Ave, Cambridge, MA 02139, USA.
#  http://www.gnu.org/copyleft/gpl.html
#


import xbmc
import xbmcaddon
import xbmcplugin
import xbmcgui

import urllib
import os
import re
import requests

import utilsTOOLS as utils
import lineuptools as tools

import sfile

import sys
path    = utils.OTT_HOME
sys.path.insert(0, path)

from channel import Channel
import dixie

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


GETTEXT  = utils.GETTEXT
TITLE    = utils.TITLE
FRODO    = utils.FRODO
GOTHAM   = utils.GOTHAM
BASEURL  = utils.GetBaseUrl()

KODISOURCE =  ADDON.getSetting('KODISOURCE') == 'true'
USERLOGOS  =  OTT_ADDON.getSetting('logo.type') == '1'
EXTRAS     =  os.path.join(OTT_PROFILE, 'extras')

# -----Addon Modes ----- #

_OTT            = 0
_MAIN           = 100
_EDIT           = 200
_RENAME         = 300
_TOGGLESORT     = 400
_SETTINGS       = 500
_LOGO           = 600
_SELECT         = 700
_CANCELSELECT   = 800
_INSERTABOVE    = 900
_INSERTBELOW    = 1000
_TOGGLEHIDE     = 1100
_HIDE           = 1200
_SHOW           = 1300
_PLAY           = 1400
_EDIT           = 1500
_NEWCHANNEL     = 1600
_REMOVE         = 1700
_CLONE          = 1800
_EDITCHANNELS   = 1900

_EDITCATEGORIES   = 1910
_EDITCATEGORY     = 1920
_BULKEDITCATEGORY = 1930
_RENAMEFAVOURITE  = 1940

_BACKUPRESTORE   = 1950
_BACKUPCHANNELS  = 1960
_RESTORECHANNELS = 1970
_FULLBACKUP      = 1980
_FULLRESTORE     = 1990

_ADDSKINSLIST  = 2000
_INILINEUP     = 2040
_IPTVLINEUP    = 2050
_ADDLOGOSLIST  = 2100
_ADDLINEUPLIST = 2200
_GETSKINS      = 2300
_GETLOGOS      = 2400
_GETLINEUPS    = 2500

_MAKEALPHA     = 2600
_INI           = 2700

# --------------------- Addon Settings --------------------- #

ALPHASORT  = ADDON.getSetting('SORT').lower()       == 'alphabetical'
SHOWHIDDEN = ADDON.getSetting('SHOWHIDDEN').lower() == 'true'
SHOWSTREAM = ADDON.getSetting('SHOWSTREAM').lower() == 'true'

# ---------------------------------------------------------- #


# --------------------- 'Global' Variables --------------------- #

START_WEIGHT = -1
END_WEIGHT   = -1

try:    
    START_WEIGHT = int(xbmcgui.Window(10000).getProperty('OTT_TOOLS_START'))

    try:   
        END_WEIGHT = int(xbmcgui.Window(10000).getProperty('OTT_TOOLS_END'))
    except: 
        pass
except: 
    pass

if ALPHASORT:
    START_WEIGHT = -1
    END_WEIGHT   = -1

# -------------------------------------------------------------- #

def main():
    utils.CheckVersion()

    addDir('Add Channel Line-up',               _ADDLINEUPLIST,   thumbnail=ICON, fanart=FANART, isFolder=True)
    addDir('Edit Channels',                     _EDITCHANNELS,    thumbnail=ICON, fanart=FANART, isFolder=True)
    addDir('Edit Categories',                   _EDITCATEGORIES,  thumbnail=ICON, fanart=FANART, isFolder=True)
    addDir('Back-up + Restore',                 _BACKUPRESTORE,   thumbnail=ICON, fanart=FANART, isFolder=True)
    addDir('Add Skins',                         _ADDSKINSLIST,    thumbnail=ICON, fanart=FANART, isFolder=True)
    addDir('Add Logo Packs',                    _ADDLOGOSLIST,    thumbnail=ICON, fanart=FANART, isFolder=True)
    addDir('Rename Favourites Category',        _RENAMEFAVOURITE, thumbnail=ICON, fanart=FANART, isFolder=True)
    addDir('Set Alphabetical Channel Order',    _MAKEALPHA,       thumbnail=ICON, fanart=FANART, isFolder=True)
    addDir('Update Add-on Links',               _INI,             thumbnail=ICON, fanart=FANART, isFolder=True)
    addDir('Create Line-up from INI File',      _INILINEUP,       thumbnail=ICON, fanart=FANART, isFolder=True)
    addDir('Create Line-up from IPTV Settings', _IPTVLINEUP,      thumbnail=ICON, fanart=FANART, isFolder=True)


def createINILineup():
    tools.createINIFileLineup()


def createIPTVLineup():
    tools.createIPTVLineup()


def getSkinList(id):
    regex = 'skin name="(.+?)" url="(.+?)" icon="(.+?)" fanart="(.+?)" description="(.+?)"'
    url   =  BASEURL + 'skins/'

    skins = url + 'skinlist.xml'
    req   = requests.get(skins)
    html  = req.content
    items = re.compile(regex).findall(html)

    for item in items:
        label  = item[0]
        id     = url + item[1]
        icon   = url + item[2]
        fanart = url + item[3]
        desc   = item[4]
        
        addDir(label, _GETSKINS, id, desc=desc, thumbnail=icon, fanart=fanart, isFolder=False)


def getSkin(label, url):
    path    = os.path.join(EXTRAS, 'skins')
    zipfile = os.path.join(path,   'skins.zip')
    
    if utils.DialogYesNo('Would you like to install ' + label, 'and make it your active skin?', 'It will be downloaded and installed into your system.'):
        utils.download(url, path, zipfile)
        utils.DialogOK(label + ' skin has been installed successfully.', 'It is now set as your active EPG skin.', 'Please restart On-Tapp.TV. Thank you.')
        OTT_ADDON.setSetting('dixie.skin', label)


def getLogosList(id):
    regex = 'logopack name="(.+?)" url="(.+?)" icon="(.+?)" fanart="(.+?)" description="(.+?)"'
    url   =  BASEURL + 'logos/'

    logos = url + 'logopacklist.xml'
    req   = requests.get(logos)
    html  = req.content
    items = re.compile(regex).findall(html)

    for item in items:
        label  = item[0]
        id     = url + item[1]
        icon   = url + item[2]
        fanart = url + item[3]
        desc   = item[4]
           
        addDir(label, _GETLOGOS, id, desc=desc, thumbnail=icon, fanart=fanart, isFolder=False)


def getLogos(label, url):
    path    = os.path.join(EXTRAS, 'logos')
    zipfile = os.path.join(path,   'logos.zip')
    
    if utils.DialogYesNo('Would you like to install ' + label, 'and make it your active logo-pack?', 'It will be downloaded and installed into your system.'):
        utils.download(url, path, zipfile)
        utils.DialogOK(label + ' logo-pack has been installed successfully.', 'It is now set as your active logo-pack.', 'Please restart On-Tapp.TV. Thank you.')
        OTT_ADDON.setSetting('dixie.logo.folder', label)


def getLineupList(id):
    baseurl = BASEURL + 'lineups/'

    url = baseurl + 'lineups.json'
    req = requests.get(url)

    response = req.json()
    result   = response['lineups']

    lineups  = result['lineup']

    for lineup in lineups:
        label = lineup['-name']
        id     = baseurl + lineup['-url']
        icon   = baseurl + lineup['-icon']
        fanart = baseurl + lineup['-fanart']
        sfZip  = baseurl + lineup['-sfzip']
        isSF   = lineup['-sf']
        desc   = lineup['-description']

        addDir(label, _GETLINEUPS, id, desc=desc, thumbnail=icon, fanart=fanart, isSF=isSF, sfZip=sfZip, isFolder=False)


def getLineups(label, url, isSF, sfZip):
    path    = OTT_PROFILE
    zipfile = os.path.join(path, 'lineups.zip')
    chandir = os.path.join(path, 'channels')

    line1    = 'Would you like to [COLOR orange]INSTALL[/COLOR] ' + label + ' line-up'
    line2    = 'or [COLOR orange]MERGE[/COLOR] it with your existing line-up?'
    line3    = ''
    nolabel  = 'MERGE'
    yeslabel = 'INSTALL'

    if utils.DialogYesNo(line1, line2, line3, nolabel, yeslabel):
        if isSF == 'true':
            utils.DialogOK(label + ' requires some links added to your Super Favourites', 'We will install these first and then install your line-up', 'Thank you.')
            utils.installSF(sfZip)

        if os.path.isdir(chandir):
            sfile.rmtree(chandir)

        utils.deleteCFG()
        utils.download(url, path, zipfile)
        OTT_ADDON.setSetting('dixie.lineup', label)
        utils.DialogOK(label + ' line-up has been installed successfully.', 'It is now set as your active channel line-up.', 'Please restart On-Tapp.TV. Thank you.')

    else:
        tools.mergeLineups(label, isSF, sfZip, url)


def editChannels():
    channels   = getAllChannels(ALPHASORT)
    totalItems = len(channels)

    for ch in channels:
        channel    = ch[2]
        id         = ch[1]
        title      = channel.title
        logo       = channel.logo
        weight     = channel.weight
        hidden     = channel.visible == 0
        stream     = channel.streamUrl
        userDef    = channel.userDef == 1
        desc       = channel.desc
        categories = channel.categories
        isClone    = channel.isClone == 1

        if hidden and not SHOWHIDDEN:
            continue

        menu  = []
        #menu.append(('Rename channel', 'XBMC.RunPlugin(%s?mode=%d&id=%s)' % (sys.argv[0], _RENAME, urllib.quote_plus(id))))
        #menu.append(('Change logo',    'XBMC.RunPlugin(%s?mode=%d&id=%s)' % (sys.argv[0], _LOGO,   urllib.quote_plus(id))))
        menu.append(('Edit channel',   'XBMC.RunPlugin(%s?mode=%d&id=%s)' % (sys.argv[0], _EDIT,   urllib.quote_plus(id))))


        if inSelection(weight):
            menu.append(('Hide selection', 'XBMC.RunPlugin(%s?mode=%d)' % (sys.argv[0], _HIDE)))
            menu.append(('Bulk Edit categories', 'XBMC.RunPlugin(%s?mode=%d)' % (sys.argv[0], _BULKEDITCATEGORY)))
            if SHOWHIDDEN:
                menu.append(('Show selection', 'XBMC.RunPlugin(%s?mode=%d)' % (sys.argv[0], _HIDE)))
        else:
            hideLabel = 'Show channel' if hidden else 'Hide channel'
            menu.append((hideLabel, 'XBMC.RunPlugin(%s?mode=%d&id=%s)' % (sys.argv[0], _TOGGLEHIDE, urllib.quote_plus(id))))

        if (not ALPHASORT) and (weight != START_WEIGHT) and (weight != END_WEIGHT):
            menu.append(('Select channel', 'XBMC.RunPlugin(%s?mode=%d&id=%s&weight=%d)' % (sys.argv[0], _SELECT, urllib.quote_plus(id), weight)))

        if inSelection(weight):
            pass

        elif isSelection() and (not ALPHASORT):
            menu.append(('Insert selection above',   'XBMC.RunPlugin(%s?mode=%d&weight=%d)' % (sys.argv[0], _INSERTABOVE, weight)))
            menu.append(('Insert selection below',   'XBMC.RunPlugin(%s?mode=%d&weight=%d)' % (sys.argv[0], _INSERTBELOW, weight)))

        if START_WEIGHT > -1:
            menu.append(('Clear selection', 'XBMC.RunPlugin(%s?mode=%d)' % (sys.argv[0], _CANCELSELECT)))

        if not userDef:
            menu.append(('Clone channel', 'XBMC.RunPlugin(%s?mode=%d&id=%s)' % (sys.argv[0], _CLONE, urllib.quote_plus(id))))

        menu.append(('Create new channel', 'XBMC.RunPlugin(%s?mode=%d)' % (sys.argv[0], _NEWCHANNEL)))

        if userDef or isClone:
            menu.append(('Remove channel', 'XBMC.RunPlugin(%s?mode=%d&id=%s)' % (sys.argv[0], _REMOVE, urllib.quote_plus(id))))

        #if len(stream):
        #    menu.append(('Activate stream', 'XBMC.RunPlugin(%s?mode=%d&stream=%s)' % (sys.argv[0], _PLAY, urllib.quote_plus(stream))))

        addStdMenu(menu)


        title = title + ' [COLOR orange] [%s] [/COLOR]' % categories

        if userDef:
            title += ' (user-defined)'

        if SHOWSTREAM:
            if len(stream) > 0:
                title += ' (stream set)'

        if len(desc):
            title += ' - %s' % desc

        if hidden:
            title = '[COLOR red]' + title  + '[/COLOR]'

        if inSelection(weight):
            title = '[I]' + title  + '[/I]'

        addDir(title, _EDIT, id, weight=weight, thumbnail=logo, fanart=FANART, isFolder=False, menu=menu, infolabels={}, totalItems=totalItems)


def editCategories():
    categories = getCategoriesList()

    for category in categories:
        if category != 'uncategorised':
            addDir(category, _EDITCATEGORY, id=category, isFolder=False)


def editCategory(category):
    RENAME = 101
    REMOVE = 201
    
    menu = []
    menu.append(['Rename category', RENAME])
    menu.append(['Remove category', REMOVE])

    option = selectMenu(category, menu)

    if option == RENAME:
        return renameCategory(category)

    if option == REMOVE:
        return removeCategory(category)

    return False


def renameCategory(category):
    newcat = getText('Rename %s' % category)
    if not newcat:
        return False

    newcat   = '|' + newcat + '|'
    category = '|' + category + '|'

    doRename(category, newcat)

    return True


def renameFavourite():
    current  =  OTT_ADDON.getSetting('FAVOURITE')
    curfave  = '|' + current + '|'

    new      =  getText('Enter new name for the favourites category', text=current)
    newfave  = '|' + new + '|'

    doRename(curfave, newfave)

    OTT_ADDON.setSetting('FAVOURITE', new)
    utils.DialogOK('Your Favourites category has been renamed.', 'It will show in the EPG Category menu as:', new)


def doRename(old, new):
    channels = getAllChannels()

    for channel in channels:
        categories = '|' + channel[2].categories + '|'
        categories = categories.replace('||', '|')

        newcategories = categories.replace(old, new)

        if newcategories == categories:
            continue

        while newcategories.startswith('|'):
            newcategories = newcategories[1:]

        while newcategories.endswith('|'):
            newcategories = newcategories[:-1]

        channel[2].categories = newcategories

        updateChannel(channel[2], channel[1])


def removeCategory(category):
    newcat   = ''
    newcat   = '|' + newcat + '|'
    category = '|' + category + '|'

    channels = getAllChannels()

    for channel in channels:
        categories = '|' + channel[2].categories + '|'
        categories = categories.replace('||', '|')

        newcategories = categories.replace(category, newcat)
        newcategories = newcategories.replace('||', '|')

        if newcategories == categories:
            continue

        while newcategories.startswith('|'):
            newcategories = newcategories[1:]

        while newcategories.endswith('|'):
            newcategories = newcategories[:-1]

        channel[2].categories = newcategories

        if len(newcategories) < 1:
            channel[2].categories = 'uncategorised'
            channel[2].visible = 0

        updateChannel(channel[2], channel[1])

    return True


def insertSelection(above, theWeight):
    channels   = getAllChannels() #these will be sorted by weight

    toMove   = []
    original = []

    while len(channels) > 0:
        channel = channels.pop(0)
        weight  = channel[2].weight
        if inSelection(weight):
            toMove.append(channel)
        else:
            original.append(channel)

    channelList = []

    if above:
        channelList = insertAbove(theWeight, original, toMove)
    else:
        channelList = insertBelow(theWeight, original, toMove)

    writeChannelsToFile(channelList)

    cancelSelection()
    
    return True


def insertBelow(theWeight, original, toMove):
    channelList = []

    inserted = False

    for channel in original:
        weight = channel[2].weight

        if weight > theWeight and not inserted:
            inserted = True
            for ch in toMove:
                channelList.append(ch)
                   
        channelList.append(channel)

    #special case if inserting below bottom
    if not inserted:
        for ch in toMove:
            channelList.append(ch)

    return channelList


def insertAbove(theWeight, original, toMove):
    channelList = []

    inserted = False

    for channel in original:
        weight = channel[2].weight

        if weight >= theWeight and not inserted:
            inserted = True
            for ch in toMove:
                channelList.append(ch)

        channelList.append(channel)

    return channelList
  

def inSelection(weight):
    return weight >= START_WEIGHT and weight <= END_WEIGHT


def isSelection():
    return START_WEIGHT > -1

    
def cancelSelection():
    xbmcgui.Window(10000).clearProperty('OTT_TOOLS_START')
    xbmcgui.Window(10000).clearProperty('OTT_TOOLS_END')
    return True


def selectChannel(weight):
    value = str(weight)

    if START_WEIGHT < 0: # nothing set
        xbmcgui.Window(10000).setProperty('OTT_TOOLS_START', value)
        xbmcgui.Window(10000).setProperty('OTT_TOOLS_END',   value)
        return True

    if weight > END_WEIGHT: #after current end
        xbmcgui.Window(10000).setProperty('OTT_TOOLS_END', value)
        return True

    if weight > START_WEIGHT and END_WEIGHT < 0: #only start set
        xbmcgui.Window(10000).setProperty('OTT_TOOLS_END', value)
        return True

    if weight > START_WEIGHT and weight < END_WEIGHT: #between current start and end
        startDelta = weight     - START_WEIGHT
        endDelta   = END_WEIGHT - weight
        if startDelta < endDelta:
            xbmcgui.Window(10000).setProperty('OTT_TOOLS_START', value)
        else:
            xbmcgui.Window(10000).setProperty('OTT_TOOLS_END', value)
        return True

    if weight < START_WEIGHT and END_WEIGHT < 0: #before start, end not set
        xbmcgui.Window(10000).setProperty('OTT_TOOLS_START', value)
        xbmcgui.Window(10000).setProperty('OTT_TOOLS_END',   str(START_WEIGHT))
        return True

    if weight < START_WEIGHT:
        xbmcgui.Window(10000).setProperty('OTT_TOOLS_START', value)
        return True

    return False


def addStdMenu(menu):
    sort = 'Sort by ONTapp.TV order' if ALPHASORT else 'Sort alphabetically'
    menu.append((sort, 'XBMC.RunPlugin(%s?mode=%d)' % (sys.argv[0], _TOGGLESORT)))

    if xbmcgui.Window(10000).getProperty('OTT_RUNNING').lower() != 'true':
        menu.append(('Launch On-Tapp.TV', 'XBMC.RunPlugin(%s?mode=%d)' % (sys.argv[0], _OTT)))

    menu.append(('Add-on settings', 'XBMC.RunPlugin(%s?mode=%d)' % (sys.argv[0], _SETTINGS)))


def toggleSort():
    if ALPHASORT:
        ADDON.setSetting('SORT', 'ONTapp.TV Order')
    else:
        ADDON.setSetting('SORT', 'Alphabetical')

    return True


def rename(id):
    channel = getChannelFromFile(id)
    title   = channel.title
    
    name = getText('Rename Channel', text=title)

    if not name:
        return False

    if name == title:
        return False

    if len(name) == 0:
        return False

    channel.title = name

    return updateChannel(channel, id)


def toggleHide(id):
    channel = getChannelFromFile(id)
    channel.visible = not channel.visible
    return updateChannel(channel, id)


def showSelection(_show):
    channels   = getAllChannels() #these will be sorted by weight

    show = 1 if _show else 0

    updated = False

    for ch in channels:
        channel = ch[2]
        id      = ch[1]
        weight  = channel.weight

        if weight > END_WEIGHT:
            break

        if weight >= START_WEIGHT:
            updated = True
            channel.visible = show
            updateChannel(channel, id)

    if not SHOWHIDDEN and not _show:
        cancelSelection()

    #actually makes sense to always cancel selection
    cancelSelection()

    return updated


def editChannel(id):
    channel = getChannelFromFile(id)
    if not channel:
        return False

    RENAME       = 100
    LOGO         = 200
    TOGGLEHIDE   = 300
    SELECT       = 400
    REMOVE       = 500
    DESC         = 600
    CATEGORY     = 700
    CLONE        = 800

    title      = channel.title
    weight     = channel.weight
    categories = channel.categories
    hidden     = int(channel.visible) == 0
    userDef    = int(channel.userDef) == 1
    isClone    = int(channel.isClone) == 1

    hideLabel  = 'Show channel' if hidden else 'Hide channel'

    menu = []
    menu.append(['Rename channel', RENAME])
    menu.append(['Change logo',    LOGO])

    menu.append(['Edit description', DESC])
    menu.append(['Edit categories', CATEGORY])
    menu.append([hideLabel,          TOGGLEHIDE])

    if not inSelection(weight):            
        menu.append(['Select channel', SELECT])

    if userDef or isClone:
        menu.append(['Remove channel', REMOVE])

    if not userDef:
        menu.append(['Clone channel', CLONE])
    
    option = selectMenu(title, menu)

    if option == RENAME:
        return rename(id)

    if option == LOGO:
        return updateLogo(id)

    if option == TOGGLEHIDE:
        return toggleHide(id)

    if option == SELECT:
        return selectChannel(weight)

    if option == REMOVE:
        return removeChannel(id)

    if option == DESC:
        return editChannelDescription(id)

    if option == CATEGORY:
        return editChannelCategory(id)

    if option == CLONE:
        return cloneChannel(id)

    return False


def editChannelDescription(id):
    channel = getChannelFromFile(id) 

    if not channel:
        return False

    desc = getText('Enter channel description', text=channel.desc)

    if not desc:
        return False

    channel.desc = desc
    return updateChannel(channel, id)


def editChannelCategory(id):
    channel = getChannelFromFile(id) 

    if not channel:
        return False

    categories = getText('Enter categories', text=channel.categories)

    if not categories:
        return False

    channel.categories = categories
    return updateChannel(channel, id)


def bulkEditCategory():
    channels = getAllChannels()
    utils.log('=== channels ===')
    utils.log(channels)
    toEdit   = []

    for channel in channels:
        weight  = channel[2].weight

        if inSelection(weight):
            toEdit.append(channel)

    newcat = getText('Enter custom category name', text='')

    if not newcat:
        return False

    toWrite = []

    for channel in toEdit:
        channel[2].categories = newcat
        toWrite.append(channel)

    writeChannelsToFile(toWrite, updateWeight=False)
    return True


def getCategoriesList():
    channels = getAllChannels()
    catList  = []

    for channel in channels:
        categories = channel[2].categories.split('|')

        for category in categories:
            if len(category) > 0 and category not in catList:
                catList.append(category)

    # catList.sort()
    return catList


def cloneChannel(id):
    channel = getChannelFromFile(id) 

    if not channel:
        return False 

    channel.isClone = True
    channel.id      = channel.id.split('_clone_')[0]

    clone = [[channel.weight, id.split('_clone_')[0], channel]]
    
    channels = getAllChannels() 

    channelList = insertBelow(channel.weight, channels, clone)

    writeChannelsToFile(channelList)

    return True


def removeChannel(id):
    channel = getChannelFromFile(id) 

    if not channel:
        return False

    if channel.userDef != 1 and channel.isClone != 1:
        return False

    if not utils.DialogYesNo('Remove %s' % channel.title, noLabel='Cancel', yesLabel='Confirm'):
        return False

    path = os.path.join(OTT_CHANNELS, id)
    utils.deleteFile(path)

    return True


def newChannel():
    title = ''

    while True:
        title = getText('Please enter channel name', title)
        if not title :
            return False

        id = createID(title)

        try:
            current, dirs, files = sfile.walk(OTT_CHANNELS)
        except Exception, e:
            return False

        duplicate = False
    
        for file in files:
            if id.lower() == file.lower():
                duplicate = True
                break

        if not duplicate:
            break

        utils.DialogOK('%s clashes with an existing channel.' % title, 'Please enter a different name.')

    weight  = 0
    channel = Channel(id, title, weight=weight, categories='', userDef=1, desc='')
    item    = [weight, id,  channel]

    channels = getAllChannels()
    channels.insert(0, item)

    writeChannelsToFile(channels)

    editChannelDescription(id)
    editChannelCategory(id)

    return True


def updateLogo(id):
    channel = getChannelFromFile(id)
    logo    = channel.logo

    logo = getImage(logo)

    if not logo:
        return False

    if not USERLOGOS:
        logo = convertToHome(logo)

    channel.logo = logo

    return updateChannel(channel, id)


def showBackupRestore():
    addDir('Back-up My Line-up', _BACKUPCHANNELS,  thumbnail=ICON, fanart=FANART, isFolder=True)
    addDir('Restore My Line-up', _RESTORECHANNELS, thumbnail=ICON, fanart=FANART, isFolder=True)
    addDir('Do Full Back-up',    _FULLBACKUP,      thumbnail=ICON, fanart=FANART, isFolder=True)
    addDir('Do Full Restore',    _FULLRESTORE,     thumbnail=ICON, fanart=FANART, isFolder=True)


def lineBackup():
    return


def lineRestore():
    return


def backupChannels():
    if not utils.DialogYesNo('Would you like to do a back-up of your channel line-up?', ''):
        return
    cmd = 'XBMC.RunScript(special://home/addons/script.tvguidedixie/backup.py, channel)'
    xbmc.executebuiltin(cmd)


def restoreChannels():
    cmd = 'XBMC.RunScript(special://home/addons/script.tvguidedixie/restore.py, channel)'
    xbmc.executebuiltin(cmd)


def fullBackup():
    if not utils.DialogYesNo('Would you like to do a full back-up of On-Tapp.TV?', ''):
        return
    cmd = 'XBMC.RunScript(special://home/addons/script.tvguidedixie/backup.py, full)'
    xbmc.executebuiltin(cmd)


def fullRestore():
    cmd = 'XBMC.RunScript(special://home/addons/script.tvguidedixie/restore.py, full)'
    xbmc.executebuiltin(cmd)


def getImage(logo):
    if len(logo) == 0:
        root = '/'
    else:
        logo = logo.replace('\\', '/')
        root = logo.rsplit('/', 1)[0] + '/'

    if KODISOURCE:
        image = xbmcgui.Dialog().browse(2, 'Choose logo', 'files', '')
    else:
        root   = xbmc.translatePath('special://userdata').split(os.sep, 1)[0] + os.sep
        image  = xbmcgui.Dialog().browse(2, 'Choose logo', 'files', '', False, False, root)

    if image and image != root:
        utils.log(image)
        utils.log('********** logo image: %s' % image)
        return image

    return None


def convertToHome(image):
    HOMESPECIAL = 'special://home/'
    HOMEFULL    = xbmc.translatePath(HOMESPECIAL)

    if image.startswith(HOMEFULL):
        image = image.replace(HOMEFULL, HOMESPECIAL)

    return image


def updateChannel(channel, id):
    path = os.path.join(OTT_CHANNELS, id)

    return channel.writeToFile(path)


def writeChannelsToFile(channelList, updateWeight=True):
    weight = 1

    for item in channelList:
        id        = item[1]
        ch        = item[2]

        if updateWeight:
            ch.weight = weight
            weight   += 1

        updateChannel(ch, id)


def getAllChannels(alphaSort = False):
    channels = []

    try:
        current, dirs, files = sfile.walk(OTT_CHANNELS)
    except Exception, e:
        return channels
    
    for file in files:
        channels.append(file)

    sorted = []

    for id in channels:
        channel = getChannelFromFile(id)

        sorter  = channel.title.lower() if ALPHASORT else channel.weight

        sorted.append([sorter, id, channel])

    sorted.sort()

    return sorted


def getChannelFromFile(id):
    path = os.path.join(OTT_CHANNELS, id)

    if not sfile.exists(path):
        return None

    cfg = sfile.readlines(path)

    return Channel(cfg)


def getText(title, text='', hidden=False):
    kb = xbmc.Keyboard(text, title)
    kb.setHiddenInput(hidden)
    kb.doModal()
    if not kb.isConfirmed():
        return None

    text = kb.getText().strip()

    if len(text) < 1:
        return None

    return text


def createID(title):
    title = title.replace('*', '_star')
    title = title.replace('+', '_plus')
    title = title.replace(' ', '_')

    title = re.sub('[:\\/?\<>|"]', '', title)
    title = title.strip()
    try:    title = title.encode('ascii', 'ignore')
    except: title = title.decode('utf-8').encode('ascii', 'ignore')

    return title.lower()


def selectMenu(title, menu):
    options = []
    for option in menu:
        options.append(option[0])

    option = xbmcgui.Dialog().select(title, options)

    if option < 0:
        return -1

    return menu[option][1]


def openSettings():
    ADDON.openSettings()
    return True


def refresh():
    xbmc.executebuiltin('Container.Refresh')


def makeAlphabetical():
    if utils.DialogYesNo('Changing to alphabetical channel order CANNOT be undone.', 'Do a back-up first to be safe.', 'Are you sure you want to do this?'):
        channels = []

        try:
            current, dirs, files = sfile.walk(OTT_CHANNELS)
        except Exception, e:
            return channels
    
        for file in files:
            channels.append(file)

        sorted = []

        for id in channels:
            channel = getChannelFromFile(id)

            sorter  = channel.title.lower()

            sorted.append([sorter, id, channel])

        sorted.sort()
        writeChannelsToFile(sorted)
        return
    return


def GetINI():
    line1 = 'We will now download the latest add-on integration files.'
    line2 = 'Please wait a minute or two. After that...'
    line3 = 'The updates will be active the next time you open the EPG.'

    utils.DialogOK(line1, line2, line3)

    cmd = 'XBMC.RunScript(special://home/addons/script.tvguidedixie/getIni.py, return)'
    xbmc.executebuiltin(cmd)
    return


def addDir(label, mode, id = '', weight = -1, desc='', thumbnail='', fanart=FANART, isFolder=True, menu=None, infolabels={}, totalItems=0, isSF='', sfZip=''):
    u  = sys.argv[0]

    u += '?label=' + urllib.quote_plus(label)
    u += '&mode='  + str(mode)

    if len(id) > 0:
        u += '&id=' + urllib.quote_plus(id)

    if weight > 0:
        u += '&weight=' + urllib.quote_plus(str(weight))

    if len(thumbnail) > 0:
        u += '&image=' + urllib.quote_plus(thumbnail)

    if len(fanart) > 0:
        u += '&fanart=' + urllib.quote_plus(fanart)

    liz = xbmcgui.ListItem(label, iconImage=thumbnail, thumbnailImage=thumbnail)

    if desc:
        infolabels['plot'] = desc

    if len(infolabels) > 0:
        liz.setInfo(type='Video', infoLabels=infolabels)
   
    liz.setProperty('Fanart_Image', fanart)

    if menu:
        liz.addContextMenuItems(menu, replaceItems=True)

    if len(isSF) > 0:
        u += '&isSF=' + urllib.quote_plus(isSF)

    if len(sfZip) > 0:
        u += '&sfZip=' + urllib.quote_plus(sfZip)

    xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=isFolder, totalItems=totalItems)


def get_params(p):
    param=[]
    paramstring=p
    if len(paramstring)>=2:
        params=p
        cleanedparams=params.replace('?','')
        if (params[len(params)-1]=='/'):
           params=params[0:len(params)-2]
        pairsofparams=cleanedparams.split('&')
        param={}
        for i in range(len(pairsofparams)):
            splitparams={}
            splitparams=pairsofparams[i].split('=')
            if (len(splitparams))==2:
                param[splitparams[0]]=splitparams[1]
    return param


params = get_params(sys.argv[2])


doRefresh   = False
cacheToDisc = True


try:    mode = int(params['mode'])
except: mode = _MAIN

try:    id = urllib.unquote_plus(params['id'])
except: id = ''

    
utils.log(sys.argv[2])
utils.log(sys.argv)
utils.log('Mode = %d' % mode)
utils.log(params)


if mode == _MAIN:
    main()


if mode == _RENAME:
    doRefresh = rename(id)


if mode == _TOGGLEHIDE:
    doRefresh = toggleHide(id)

if mode == _HIDE or mode == _SHOW:
    doRefresh = showSelection(mode == _SHOW)

if mode == _LOGO:
    doRefresh = updateLogo(id)


if mode == _TOGGLESORT:
    doRefresh = toggleSort()


if mode == _OTT:
    xbmc.executebuiltin('RunScript(script.tvguidedixie)')


if mode == _SETTINGS:
    doRefresh = openSettings()


if mode == _SELECT:
    doRefresh = False
    try:    
        if not ALPHASORT:
            weight = int(params['weight'])
            doRefresh = selectChannel(weight)
    except:
        doRefresh = False

if mode == _PLAY:
    doRefresh = False
    try:
        stream   = urllib.unquote_plus(params['stream'])

        #ottAddon = xbmcaddon.Addon(id = 'script.tvguidedixie')
        #path     = ottAddon.getAddonInfo('path')

        #sys.path.insert(0, path)

        import player
        player.play(stream, False)
    except Exception, e:
        pass

if mode == _CANCELSELECT:
    doRefresh = cancelSelection()


if mode == _INSERTABOVE:
    try:
        weight = int(params['weight'])
        doRefresh = insertSelection(above=True, theWeight=weight)
    except:
        pass


if mode == _INSERTBELOW:
    try:
        weight = int(params['weight'])
        doRefresh = insertSelection(above=False, theWeight=weight)
    except:
        pass

if mode == _EDIT:
    doRefresh = editChannel(id)


if mode == _EDITCATEGORY:
    doRefresh = editCategory(id)


if mode == _NEWCHANNEL:
    doRefresh = newChannel()


if mode == _REMOVE:
    doRefresh = removeChannel(id)


if mode == _CLONE:
    doRefresh = cloneChannel(id)


if mode == _EDITCHANNELS:
    editChannels()


if mode == _EDITCATEGORIES:
    editCategories()


if mode == _RENAMEFAVOURITE:
    renameFavourite()


if mode == _BULKEDITCATEGORY:
    doRefresh = bulkEditCategory()


if mode == _ADDSKINSLIST:
    getSkinList(id)


if mode == _GETSKINS:
    label = urllib.unquote_plus(params['label'])
    url   = urllib.unquote_plus(params['id'])

    getSkin(label, url)


if mode == _ADDLOGOSLIST:
    getLogosList(id)


if mode == _GETLOGOS:
    label = urllib.unquote_plus(params['label'])
    url   = urllib.unquote_plus(params['id'])

    getLogos(label, url)


if mode == _ADDLINEUPLIST:
    getLineupList(id)


if mode == _GETLINEUPS:
    label = urllib.unquote_plus(params['label'])
    url   = urllib.unquote_plus(params['id'])
    isSF  = urllib.unquote_plus(params['isSF'])
    sfZip = urllib.unquote_plus(params['sfZip'])

    getLineups(label, url, isSF, sfZip)


if mode == _INILINEUP:
    createINILineup()


if mode == _IPTVLINEUP:
    createIPTVLineup()


if mode == _BACKUPRESTORE:
    showBackupRestore()


if mode == _BACKUPCHANNELS:
    backupChannels()


if mode == _RESTORECHANNELS:
    restoreChannels()


if mode == _FULLBACKUP:
    fullBackup()


if mode == _FULLRESTORE:
    fullRestore()


if mode == _MAKEALPHA:
    makeAlphabetical()

if mode == _INI:
    GetINI()

if doRefresh:
    refresh()

xbmcplugin.setContent(int(sys.argv[1]), 'movies')
# xbmc.executebuiltin('Container.SetViewMode(%d)' % 515)
xbmcplugin.endOfDirectory(int(sys.argv[1]), cacheToDisc=cacheToDisc)
