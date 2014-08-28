import sublime, sublime_plugin

if sublime.version() >= '3000':
	from collections import OrderedDict
	import json
	from . import xmltodict
else:
	import xmltodict
	import simplejson as json
	from ordereddict import OrderedDict

def newViewWithText(text):
	newView = sublime.active_window().new_file()
	if sublime.version() >= '3000':
		newView.run_command('append',{'characters':text})
	else:
		newEdit = newView.begin_edit()
		newView.insert(newEdit,0,text)
		newView.end_edit(newEdit)

def xml2json(fulltext,pretty=False):
	try:
		jsonObj = xmltodict.parse(fulltext)
		if pretty:
			jsonStr = json.dumps(jsonObj,indent=4)
		else:
			jsonStr = json.dumps(jsonObj)
	except Exception as e:
		sublime.error_message('xml2json error: ' + e.message)
		return None
	return jsonStr

class Xml2jsonCommand(sublime_plugin.TextCommand):
	def run(self,edit):
		fulltext = self.view.substr(sublime.Region(0, self.view.size()))
		jsonStr = xml2json(fulltext,False)
		if jsonStr:
			newViewWithText(jsonStr)

class Xml2jsonprettyCommand(sublime_plugin.TextCommand):
	def run(self,edit):
		fulltext = self.view.substr(sublime.Region(0, self.view.size()))
		jsonStr = xml2json(fulltext,True)
		if jsonStr:
			newViewWithText(jsonStr)

def json2xml(fulltext,pretty=False):
	try:
		jsonObj = json.JSONDecoder(object_pairs_hook=OrderedDict).decode(fulltext)
		xmlStr = xmltodict.unparse(jsonObj,pretty=pretty)
	except ValueError:
		try:
			newText = '{"root":' + fulltext + '}' #try to add a wrapper
			jsonObj = json.JSONDecoder(object_pairs_hook=OrderedDict).decode(fulltext)
			xmlStr = xmltodict.unparse(jsonObj,pretty=pretty)
		except Exception as e:
			newViewWithText(newText)
			sublime.error_message('json2xml error!!: ' + e.message)
			return None
	except Exception as e:
		sublime.error_message('json2xml error: ' + e.message)
		return None
	return xmlStr

class Json2xmlCommand(sublime_plugin.TextCommand):
	def run(self,edit):
		fulltext = self.view.substr(sublime.Region(0, self.view.size()))
		xmlStr = json2xml(fulltext,False)
		if xmlStr:
			newViewWithText(xmlStr)
class Json2xmlprettyCommand(sublime_plugin.TextCommand):
	def run(self,edit):
		fulltext = self.view.substr(sublime.Region(0, self.view.size()))
		xmlStr = json2xml(fulltext,True)
		if xmlStr:
			newViewWithText(xmlStr)
