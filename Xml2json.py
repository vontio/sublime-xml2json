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

def get_bool_setting(key, default):
	value = get_settings().get(key, default)
	if isinstance(value, str):
		value = value.strip().lower()
		if value in ('true', '1', 'yes', 'on', 'pretty', 'enable', 'enabled'):
			return True
		if value in ('false', '0', 'no', 'off', 'compact', 'disable', 'disabled'):
			return False
	return bool(value)

def get_json_indent():
	indent = get_settings().get('pretty_json_indent', 2)
	try:
		indent = int(indent)
		if indent < 0:
			indent = 2
	except Exception:
		indent = 2
	return indent

def get_xml_indent():
	indent = get_settings().get('pretty_xml_indent', 2)
	try:
		indent = int(indent)
		if indent < 0:
			indent = 2
	except Exception:
		indent = 2
	return ' ' * indent

def get_json_ensure_ascii():
	return get_bool_setting('json_ensure_ascii', False)

def get_json_sort_keys():
	return get_bool_setting('json_sort_keys', False)

def get_default_root_name():
	root = get_settings().get('default_xml_root_name', 'root')
	if not isinstance(root, str):
		return 'root'
	root = root.strip()
	return root or 'root'

def get_empty_tag_style():
	style = get_settings().get('empty_tag_style', 'compact')
	if isinstance(style, str):
		style = style.strip().lower()
	else:
		style = 'compact'
	if style not in ('compact', 'spaced', 'expanded'):
		style = 'compact'
	return style

def get_default_pretty():
	default_value = get_settings().get('default_conversion_pretty', True)
	if isinstance(default_value, str):
		default_value = default_value.strip().lower()
		if default_value == 'compact':
			return False
		if default_value == 'pretty':
			return True
	return bool(default_value)

def get_include_xml_declaration():
	return get_bool_setting('include_xml_declaration', True)

def get_line_ending():
	value = get_settings().get('line_ending', 'auto')
	if isinstance(value, str):
		value = value.strip().lower()
		if value in ('lf', '\\n', 'unix'):
			return '\n'
		if value in ('crlf', '\\r\\n', 'windows'):
			return '\r\n'
		if value in ('cr', '\\r', 'mac'):
			return '\r'
	return None

def get_ensure_final_newline():
	return get_bool_setting('ensure_final_newline', True)

def get_trim_trailing_whitespace():
	return get_bool_setting('trim_trailing_whitespace', True)

def normalize_newlines(text, source_text=None):
	target_newline = get_line_ending()
	if target_newline is None and source_text:
		if '\r\n' in source_text:
			target_newline = '\r\n'
		elif '\r' in source_text:
			target_newline = '\r'
		else:
			target_newline = '\n'

	text = text.replace('\r\n', '\n').replace('\r', '\n')
	has_trailing_newline = text.endswith('\n')

	if get_trim_trailing_whitespace():
		lines = text.split('\n')
		lines = [line.rstrip(' \t') for line in lines]
		text = '\n'.join(lines)

	if target_newline:
		text = text.replace('\n', target_newline)

	newline = target_newline or '\n'

	if get_ensure_final_newline():
		if not text.endswith(('\n', '\r')):
			text += newline
	elif has_trailing_newline and not text.endswith(('\n', '\r')):
		text += newline
	return text

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

def newViewWithText(text, syntax=None, source_text=None):
	newView = sublime.active_window().new_file()

	try:
		st_ver = int(sublime.version())
	except Exception:
		st_ver = 4000

	text = normalize_newlines(text, source_text)

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

def save_with_prompt(source_view, text, syntax, extension, source_label, source_text=None):
	target_path = None
	source_path = source_view.file_name()
	if source_path:
		target_path = os.path.splitext(source_path)[0] + extension
	if not target_path:
		newViewWithText(text, syntax, source_text)
		sublime.status_message(source_label + ': source not saved, opened new buffer')
		return

	text = normalize_newlines(text, source_text)
	if os.path.exists(target_path):
		choice = sublime.yes_no_cancel_dialog('File exists:\n{}\nOverwrite?'.format(target_path), 'Overwrite', 'Don\'t Overwrite')
		if choice != sublime.DIALOG_YES:
			newViewWithText(text, syntax, source_text)
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

def xml2json(fulltext, pretty=None):
	if pretty is None:
		pretty = get_default_pretty()
	try:
		jsonObj = xmltodict.parse(fulltext)
		if pretty:
			jsonStr = json.dumps(
				jsonObj,
				indent=get_json_indent(),
				ensure_ascii=get_json_ensure_ascii(),
				sort_keys=get_json_sort_keys())
		else:
			jsonStr = json.dumps(
				jsonObj,
				ensure_ascii=get_json_ensure_ascii(),
				sort_keys=get_json_sort_keys())
	except Exception as e:
		sublime.error_message('xml2json error: ' + str(e))
		return None
	return jsonStr

class Xml2jsonCommand(sublime_plugin.TextCommand):
	def run(self,edit):
		fulltext = self.view.substr(sublime.Region(0, self.view.size()))
		jsonStr = xml2json(fulltext)
		if jsonStr:
			newViewWithText(jsonStr, 'json', fulltext)

def json2xml(fulltext, pretty=None):
	if pretty is None:
		pretty = get_default_pretty()
	try:
		data = json.JSONDecoder(object_pairs_hook=OrderedDict).decode(fulltext)
		root_name = get_default_root_name() or "root"
		# decide if we need to wrap the data
		if isinstance(data, list):
			# list at root level, need to wrap
			wrapped = OrderedDict([(
				root_name, 
				OrderedDict([("item", data)]) # wrap list items in "item" tags
			)])
		elif not isinstance(data, dict):
			# string, number, bool, null etc. Wrap it
			wrapped = OrderedDict([(root_name, data)])
		elif len(data) > 1:
			# multiple root-level keys, need to wrap
			wrapped = OrderedDict([(root_name, data)])
		else:
			wrapped = data
		xmlStr = xmltodict.unparse(
			wrapped,
			pretty=pretty,
			full_document=get_include_xml_declaration(),
			indent=get_xml_indent(),
			empty_tag_style=get_empty_tag_style())
	except Exception as e:
		sublime.error_message('json2xml error: ' + str(e))
		return None
	return xmlStr

class Json2xmlCommand(sublime_plugin.TextCommand):
	def run(self,edit):
		fulltext = self.view.substr(sublime.Region(0, self.view.size()))
		xmlStr = json2xml(fulltext)
		if xmlStr:
			newViewWithText(xmlStr, 'xml', fulltext)

class Xml2jsonSaveCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		fulltext = self.view.substr(sublime.Region(0, self.view.size()))
		jsonStr = xml2json(fulltext)
		if jsonStr:
			save_with_prompt(self.view, jsonStr, 'json', '.json', 'xml2json_save', fulltext)

class Json2xmlSaveCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		fulltext = self.view.substr(sublime.Region(0, self.view.size()))
		xmlStr = json2xml(fulltext)
		if xmlStr:
			save_with_prompt(self.view, xmlStr, 'xml', '.xml', 'json2xml_save', fulltext)

class PrettyJsonCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		region = sublime.Region(0, self.view.size())
		fulltext = self.view.substr(region)
		try:
			jsonObj = json.JSONDecoder(object_pairs_hook=OrderedDict).decode(fulltext)
		except Exception as e:
			sublime.error_message('pretty json error: ' + str(e))
			return

		formatted = json.dumps(
			jsonObj,
			indent=get_json_indent(),
			ensure_ascii=get_json_ensure_ascii(),
			sort_keys=get_json_sort_keys())
		formatted = normalize_newlines(formatted, fulltext)
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

		compact = json.dumps(
			jsonObj,
			ensure_ascii=get_json_ensure_ascii(),
			sort_keys=get_json_sort_keys())
		compact = normalize_newlines(compact, fulltext)
		self.view.replace(edit, region, compact)
		setSyntaxSafely(self.view, get_json_candidates())

class PrettyXmlCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		region = sublime.Region(0, self.view.size())
		fulltext = self.view.substr(region)
		try:
			xmlObj = xmltodict.parse(fulltext)
			pretty_xml = xmltodict.unparse(
				xmlObj,
				pretty=True,
				indent=get_xml_indent(),
				empty_tag_style=get_empty_tag_style())
		except Exception as e:
			sublime.error_message('pretty xml error: ' + str(e))
			return

		pretty_xml = normalize_newlines(pretty_xml, fulltext)
		self.view.replace(edit, region, pretty_xml)
		setSyntaxSafely(self.view, get_xml_candidates())

class CompactXmlCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		region = sublime.Region(0, self.view.size())
		fulltext = self.view.substr(region)
		try:
			xmlObj = xmltodict.parse(fulltext)
			compact_xml = xmltodict.unparse(
				xmlObj,
				pretty=False,
				indent=get_xml_indent(),
				empty_tag_style=get_empty_tag_style())
		except Exception as e:
			sublime.error_message('compact xml error: ' + str(e))
			return

		compact_xml = normalize_newlines(compact_xml, fulltext)
		self.view.replace(edit, region, compact_xml)
		setSyntaxSafely(self.view, get_xml_candidates())
