import sublime, sublime_plugin

try:
	st_ver = int(sublime.version())
except Exception:
	st_ver = 4000
if st_ver >= 3000:
	from collections import OrderedDict
	import json
	from . import xmltodict
else:
	import xmltodict
	import simplejson as json
	from ordereddict import OrderedDict

def setSyntaxSafely(view, candidates):
	"""
	candidates: list of possible syntax file paths (strings).
	Try them in order until one works.
	"""
	for path in candidates:
		try:
			view.set_syntax_file(path)
			return
		except Exception:
			pass

def newViewWithText(text, syntax=None):
	newView = sublime.active_window().new_file()

	try:
		st_ver = int(sublime.version())
	except Exception:
		st_ver = 4000

	if st_ver >= 3000:
		newView.run_command('append',{'characters':text})
	else:
		newEdit = newView.begin_edit()
		newView.insert(newEdit,0,text)
		newView.end_edit(newEdit)
	if syntax == 'xml':
		xml_candidates = [
			'Packages/XML/XML.sublime-syntax',   # ST3.1+/ST4 
			'Packages/XML/XML.tmLanguage',       # ST2/ST3
		]
		setSyntaxSafely(newView, xml_candidates)

	elif syntax == 'json':
		json_candidates = [
			'Packages/JSON/JSON.sublime-syntax',     # ST3+/ST4
			'Packages/JSON/JSON.tmLanguage',         # ST3
			'Packages/JavaScript/JSON.sublime-syntax',
			'Packages/JavaScript/JSON.tmLanguage',   # ST2 / ST3
		]
		setSyntaxSafely(newView, json_candidates)

def xml2json(fulltext, pretty=True):
	try:
		jsonObj = xmltodict.parse(fulltext)
		if pretty:
			jsonStr = json.dumps(jsonObj, indent=2, ensure_ascii=False)
		else:
			jsonStr = json.dumps(jsonObj, ensure_ascii=False)
	except Exception as e:
		sublime.error_message('xml2json error: ' + str(e))
		return None
	return jsonStr

class Xml2jsonCommand(sublime_plugin.TextCommand):
	def run(self,edit):
		fulltext = self.view.substr(sublime.Region(0, self.view.size()))
		jsonStr = xml2json(fulltext, True)
		if jsonStr:
			newViewWithText(jsonStr, 'json')

class Xml2jsonCompactCommand(sublime_plugin.TextCommand):
	def run(self,edit):
		fulltext = self.view.substr(sublime.Region(0, self.view.size()))
		jsonStr = xml2json(fulltext, False)
		if jsonStr:
			newViewWithText(jsonStr, 'json')

def json2xml(fulltext, pretty=True):
	try:
		jsonObj = json.JSONDecoder(object_pairs_hook=OrderedDict).decode(fulltext)
		xmlStr = xmltodict.unparse(jsonObj, pretty=pretty)
	except ValueError:
		try:
			newText = '{"root":' + fulltext + '}' #try to add a wrapper
			jsonObj = json.JSONDecoder(object_pairs_hook=OrderedDict).decode(newText)
			xmlStr = xmltodict.unparse(jsonObj, pretty=pretty)
		except Exception as e:
			newViewWithText(newText, 'xml')
			sublime.error_message('json2xml error!!: ' + str(e))
			return None
	except Exception as e:
		sublime.error_message('json2xml error: ' + str(e))
		return None
	return xmlStr

class Json2xmlCommand(sublime_plugin.TextCommand):
	def run(self,edit):
		fulltext = self.view.substr(sublime.Region(0, self.view.size()))
		xmlStr = json2xml(fulltext, True)
		if xmlStr:
			newViewWithText(xmlStr, 'xml')

class Json2xmlCompactCommand(sublime_plugin.TextCommand):
	def run(self,edit):
		fulltext = self.view.substr(sublime.Region(0, self.view.size()))
		xmlStr = json2xml(fulltext, False)
		if xmlStr:
			newViewWithText(xmlStr, 'xml')
