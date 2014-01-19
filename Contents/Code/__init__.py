from datetime import datetime

TITLE 		= 'USTVnow'
PREFIX 		= '/video/ustvnow'
ART 		= 'art-default.jpeg'
ICON 		= 'icon-default.png'
ICON_PREFS 	= 'icon-prefs.png'

BASE_URL		 = 'http://m.ustvnow.com'
GUIDE			 = 'http://www.ustvnow.com?a=do_login&force_redirect=1&manage_proper=1&input_username=%s&input_password=%s'
RECORD_PROGRAM	 = 'http://www.ustvnow.com/recordprogram.php?id=%s&token=%s'
DELETE_RECORDING = 'http://www.ustvnow.com/recordprogram.php?delete=%s&token=%s'
LOGIN_URL		 = BASE_URL + '/iphone/1/live/login?username=%s&password=%s'
LIVETV			 = BASE_URL + '/iphone/1/live/playingnow?pgonly=true&token=%s'
RECORDINGS		 = BASE_URL + '/iphone/1/dvr/viewdvrlist?pgonly=true&token=%s'
FAVORITES		 = BASE_URL + '/iphone/1/live/showfavs?pgonly=true&token=%s'
ADD_FAVORITE	 = BASE_URL + '/iphone/1/live/updatefavs?prgsvcid=%s&token=%s&action=add'

####################################################################################################
def FormatDate(date):
	times = date.split('-')
	start = datetime.strptime(times[0], "%H:%M%p").strftime("%I:%M%p")
	end = datetime.strptime(times[1], "%H:%M%p").strftime("%I:%M%p")
	return start + '-' + end
	
def GetURL(network):
	page = HTML.ElementFromURL(LIVETV % (Dict['token']))
	node = page.xpath("//h1[contains(., '" + network + "')]/../..")
	href = node[0].xpath(".//a[contains(@class, 'viewlink')]")
	
	if len(href) > 0:
		return href[0].get('href')
	else:
		return None
		
def URLEncode(title, summary, network):
	return '#' + String.Encode(summary.strip() + '::' + title + '::' + network)
	
####################################################################################################
def Start():
	ObjectContainer.title1 = TITLE
	ObjectContainer.art = R(ART)
	DirectoryObject.thumb = R(ICON)
	DirectoryObject.art = R(ART)

####################################################################################################
@handler(PREFIX, TITLE, art=ART, thumb=ICON)
def MainMenu(view_group='InfoList'):
	Login()
	oc = ObjectContainer()	
	oc.add(DirectoryObject(key = Callback(GetChannels), title = 'All Channels'))
	oc.add(DirectoryObject(key = Callback(GetFavorites), title = 'My Favorites'))
	oc.add(DirectoryObject(key = Callback(GetRecordings), title = 'My Recordings'))
	oc.add(DirectoryObject(key = Callback(GetGuide), title = 'Channel Guide'))
	oc.add(PrefsObject(title = 'Preferences', thumb = R(ICON_PREFS)))
	return oc

####################################################################################################
@route(PREFIX + '/getchannels')
def GetChannels():	
	oc = ObjectContainer(title2='Live TV')
	page = HTML.ElementFromURL(LIVETV % (Dict['token']))
	feeds = page.xpath("//div[contains(@class, 'livetv-content-pages')]")
	for feed in feeds:
		url = feed.xpath('.//a[@class="viewlink"]')
		if len(url) > 0:
			name = feed.xpath('.//h1')[0].text
			url = BASE_URL + url[0].get("href")		
			title = feed.xpath('.//td[@class="nowplaying_item"]')[0].text
			summary = feed.xpath('.//td[@class="nowplaying_itemdesc"]')[0].text_content()
			thumb = R(name.lower() + '.jpg')
			encoded_data = URLEncode(title, summary, name)
			oc.add(VideoClipObject(
				url = url + encoded_data,
				title = name + ' - ' + String.DecodeHTMLEntities(title),
				summary = String.DecodeHTMLEntities(summary.strip()),
				thumb = thumb,
				art = thumb
			))
			
	return oc

####################################################################################################
@route(PREFIX + '/getfavorites')
def GetFavorites():
	oc = ObjectContainer(title2='My Favorites')
	page = HTML.ElementFromURL(FAVORITES % (Dict['token']))
	favorites = page.xpath("//div[contains(@class, 'livetv-content-pages')]")
	for fav in favorites:
		url = fav.xpath('.//a[@class="viewlink"]')
		if len(url) > 0:
			name = fav.xpath('.//h1')[0].text
			url = BASE_URL + url[0].get("href")		
			title = fav.xpath('.//td[@class="nowplaying_item"]')[0].text
			summary = fav.xpath('.//td[@class="nowplaying_itemdesc"]')[0].text_content()
			thumb = R(name.lower() + '.jpg')
			encoded_data = URLEncode(title, summary, name)
			oc.add(VideoClipObject(
				url = url + encoded_data,
				title = name + " - " + String.DecodeHTMLEntities(title),
				summary = String.DecodeHTMLEntities(summary.strip()),
				thumb = thumb,
				art = thumb
			))
			
	if len(oc) == 0:
		return ObjectContainer(title2='Favorites', header='Favorites', message='No Favorites found')
	else:
		return oc

####################################################################################################
@route(PREFIX + '/getrecordings')
def GetRecordings():
	oc = ObjectContainer(title2='Recordings')
	page = HTML.ElementFromURL(RECORDINGS % (Dict['token']))
	recordings = page.xpath('//div[contains(@class, "reccontentpage")]')
	for rec in recordings:
		url = rec.xpath('.//a[@class="viewlink"]')
		if len(url) > 0:
			name = rec.xpath('.//h1')[0].text
			url = BASE_URL + url[0].get("href")
			title = rec.xpath('.//td[@class="nowplaying_item"]')[0].text
			summary = rec.xpath('.//td[@class="nowplaying_itemdesc"]')
			if len(summary) > 0:
				summary = summary[0].text_content()
			else:
				summary = 'No description available'
			
			thumb = R(name.lower() + '.jpg')
			encoded_data = URLEncode(title, summary, name)
			oc.add(VideoClipObject(
				url = url + encoded_data,
				title = title,
				summary = String.DecodeHTMLEntities(summary.strip()),
				thumb = thumb,
				art = thumb
			))
	if len(oc) == 0:
		return ObjectContainer(title2='Recordings', header='Recordings', message='No Recordings found')
	else:
		return oc

####################################################################################################		
@route(PREFIX + '/getguide')
def GetGuide():
	oc = ObjectContainer(title2='Guide')
	page = HTML.ElementFromURL(GUIDE % (Prefs["username"], Prefs["password"]))
	channels = page.xpath('//td[contains(@class, "chnl")]')
	for channel in channels:
		show_info = []
		name = channel.xpath('.//strong')[0].text
		shows = channel.xpath('following-sibling::td//td[@title]')
		for show in shows:
			content = show.xpath('.//div[contains(@class, "cntnt")]')[0]
			href = content.xpath('.//a')[0]
			desc = content.xpath('.//div')[0].text		
			if desc is None:
				desc = 'No description available'			
			
			rec_id = content.xpath('.//a[contains(@title, "Record Program")]')
			if len(rec_id) > 0:
				rec_id = rec_id[0].get('onclick').split("javascript:recordProgram('")[1].split('\'')[0]
			else:
				rec_id = ''
				
			del_id = content.xpath('.//a[contains(@title, "Delete Marked Recording")]')
			if len(del_id) > 0:
				del_id = del_id[0].get('onclick').split("javascript:deleteProgram('")[1].split('\'')[0]
			else:
				del_id = ''
			
			fav_id = content.xpath('.//a[contains(@class, "play")]')
			if len(fav_id) > 0:
				fav_id = fav_id[0].get('onclick').split('playVideo("')[1].split('_')[0]
			else:
				fav_id = ''

			show_info.append({
				'channel': href.get('title').split('Watch ')[1],
				'time': FormatDate(show.get('title')),
				'title': href.text,
				'desc': desc,
				'rec_id': rec_id,
				'del_id': del_id,
				'fav_id': fav_id
				}
			)
		show_info = JSON.StringFromObject(show_info)
		oc.add(DirectoryObject(key = Callback(GuideSubMenu, title=name, data=String.Encode(show_info)), title=name))		
	return oc
		
####################################################################################################
@route(PREFIX + '/guidesubmenu')
def GuideSubMenu(title, data):
	oc = ObjectContainer(title2=title)
	shows = JSON.ObjectFromString(String.Decode(data))
	for show in shows:
		title = show['time'] + ' - ' + show['title']
		ids = show['rec_id'] + '||' + show['del_id'] + '||' + show['fav_id']
		oc.add(DirectoryObject(key = Callback(ChannelOptions, title=show['title'], summary=show['desc'], network=show['channel'], ids=ids), title=title, summary=show['desc']))
	return oc
	
####################################################################################################
@route(PREFIX + '/channeloptions')
def ChannelOptions(title, summary, network, ids):
	oc = ObjectContainer(title2='Options for ' + title)
	url = GetURL(network)
	rec_id, del_id, fav_id = ids.split('||')
	encoded_data = URLEncode(title, summary, network)
	
	if url is not None:
		oc.add(VideoClipObject(
			url = BASE_URL + url + encoded_data,
			title = 'Watch ' + title,
			summary = summary,
			thumb = R(network + ".jpg")
		))
		if rec_id is not '':		
			oc.add(DirectoryObject(key = Callback(RecordMenu, type='Record', id=rec_id), title='Record'))
		if del_id is not '':
			oc.add(DirectoryObject(key = Callback(RecordMenu, type='Delete', id=del_id), title='Delete'))
		if fav_id is not '':
			oc.add(DirectoryObject(key = Callback(FavoriteMenu, id=fav_id), title='Add to Favorites'))
	else:
		return ObjectContainer(header=network, message='You must be a paid subscriber to view these options')
	return oc
	
####################################################################################################
@route(PREFIX + '/recordmenu')
def RecordMenu(type, id):
	if type == 'Record':
		data = HTTP.Request(RECORD_PROGRAM % (id, Dict['token']))
	else:
		data = HTTP.Request(DELETE_RECORDING % (id, Dict['token']))
	return ObjectContainer(title2=type, header=type, message=data.content)
	
####################################################################################################
@route(PREFIX + '/favoritemenu')
def FavoriteMenu(id):
	data = XML.ElementFromURL(ADD_FAVORITE % (id, Dict['token']))
	return ObjectContainer(title2='Add to Favorites', header='Favorites', message='Favorite added successfully')
	
####################################################################################################
def Login():
	Dict['token'] = ""
	username = Prefs["username"]
	password = Prefs["password"]
	if (username != None) and (password != None):
		x = HTTP.Request(LOGIN_URL % (username, password), cacheTime=0).content
		for cookie in HTTP.CookiesForURL(BASE_URL).split(';'):
			if 'token' in cookie:
				Dict['token'] = cookie.split("=")[1]
				return True
	return False