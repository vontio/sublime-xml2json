import sublime, sublime_plugin
import os

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

def get_xml_candidates():
	return [
		'Packages/XML/XML.sublime-syntax',   # ST3.1+/ST4 
		'Packages/XML/XML.tmLanguage',       # ST2/ST3
	]

def get_json_candidates():
	return [
		'Packages/JSON/JSON.sublime-syntax',     # ST3+/ST4
		'Packages/JSON/JSON.tmLanguage',         # ST3
		'Packages/JavaScript/JSON.sublime-syntax',
		'Packages/JavaScript/JSON.tmLanguage',   # ST2 / ST3
	]

def get_settings():
	return sublime.load_settings('xml2json.sublime-settings')

def get_empty_tag_style():
	style = get_settings().get('empty_tag_style', 'compact')
	if isinstance(style, str):
		style = style.strip().lower()
	else:
		style = 'compact'
	if style not in ('compact', 'spaced', 'expanded'):
		style = 'compact'
	return style

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
		setSyntaxSafely(newView, get_xml_candidates())

	elif syntax == 'json':
		setSyntaxSafely(newView, get_json_candidates())

def save_with_prompt(source_view, text, syntax, extension, source_label):
	target_path = None
	source_path = source_view.file_name()
	if source_path:
		target_path = os.path.splitext(source_path)[0] + extension
	if not target_path:
		newViewWithText(text, syntax)
		sublime.status_message(source_label + ': source not saved, opened new buffer')
		return

	if os.path.exists(target_path):
		choice = sublime.yes_no_cancel_dialog('File exists:\n{}\nOverwrite?'.format(target_path), 'Overwrite', 'Don\'t Overwrite')
		if choice != sublime.DIALOG_YES:
			newViewWithText(text, syntax)
			sublime.status_message(source_label + ': did not overwrite existing file')
			return

	try:
		with open(target_path, 'w', encoding='utf-8') as handle:
			handle.write(text)
		new_view = sublime.active_window().open_file(target_path)
		if syntax == 'json':
			setSyntaxSafely(new_view, get_json_candidates())
		elif syntax == 'xml':
			setSyntaxSafely(new_view, get_xml_candidates())
		sublime.status_message(source_label + ': saved to ' + target_path)
	except Exception as e:
		sublime.error_message(source_label + ' error saving file: ' + str(e))
		newViewWithText(text, syntax)

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

def json2xml(fulltext, pretty=True):
	try:
		jsonObj = json.JSONDecoder(object_pairs_hook=OrderedDict).decode(fulltext)
		xmlStr = xmltodict.unparse(
			jsonObj, pretty=pretty, empty_tag_style=get_empty_tag_style())
	except ValueError:
		try:
			newText = '{"root":' + fulltext + '}' #try to add a wrapper
			jsonObj = json.JSONDecoder(object_pairs_hook=OrderedDict).decode(newText)
			xmlStr = xmltodict.unparse(
				jsonObj, pretty=pretty, empty_tag_style=get_empty_tag_style())
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

class Xml2jsonSaveCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		fulltext = self.view.substr(sublime.Region(0, self.view.size()))
		jsonStr = xml2json(fulltext, True)
		if jsonStr:
			save_with_prompt(self.view, jsonStr, 'json', '.json', 'xml2json_save')

class Json2xmlSaveCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		fulltext = self.view.substr(sublime.Region(0, self.view.size()))
		xmlStr = json2xml(fulltext, True)
		if xmlStr:
			save_with_prompt(self.view, xmlStr, 'xml', '.xml', 'json2xml_save')

class PrettyJsonOrderedCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		region = sublime.Region(0, self.view.size())
		fulltext = self.view.substr(region)
		try:
			jsonObj = json.JSONDecoder(object_pairs_hook=OrderedDict).decode(fulltext)
		except Exception as e:
			sublime.error_message('pretty json error: ' + str(e))
			return

		formatted = json.dumps(jsonObj, indent=2, ensure_ascii=False)
		self.view.replace(edit, region, formatted)
		setSyntaxSafely(self.view, get_json_candidates())

class CompactJsonCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		region = sublime.Region(0, self.view.size())
		fulltext = self.view.substr(region)
		try:
			jsonObj = json.JSONDecoder(object_pairs_hook=OrderedDict).decode(fulltext)
		except Exception as e:
			sublime.error_message('compact json error: ' + str(e))
			return

		compact = json.dumps(jsonObj, ensure_ascii=False)
		self.view.replace(edit, region, compact)
		setSyntaxSafely(self.view, get_json_candidates())

class PrettyXmlCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		region = sublime.Region(0, self.view.size())
		fulltext = self.view.substr(region)
		try:
			xmlObj = xmltodict.parse(fulltext)
			pretty_xml = xmltodict.unparse(
				xmlObj, pretty=True, empty_tag_style=get_empty_tag_style())
		except Exception as e:
			sublime.error_message('pretty xml error: ' + str(e))
			return

		self.view.replace(edit, region, pretty_xml)
		setSyntaxSafely(self.view, get_xml_candidates())

class CompactXmlCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		region = sublime.Region(0, self.view.size())
		fulltext = self.view.substr(region)
		try:
			xmlObj = xmltodict.parse(fulltext)
			compact_xml = xmltodict.unparse(
				xmlObj, pretty=False, empty_tag_style=get_empty_tag_style())
		except Exception as e:
			sublime.error_message('compact xml error: ' + str(e))
			return

		self.view.replace(edit, region, compact_xml)
		setSyntaxSafely(self.view, get_xml_candidates())
