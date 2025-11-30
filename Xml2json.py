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

def get_attr_text_normalization_enabled():
	return get_bool_setting('normalize_attribute_text_pairs', True)

def get_attr_text_value_key():
	value_key = get_settings().get('attribute_text_value_key', 'value')
	if not isinstance(value_key, str):
		return 'value'
	value_key = value_key.strip()
	return value_key or 'value'

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
		if get_attr_text_normalization_enabled():
			jsonObj = apply_attr_text_normalization(jsonObj)
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

def apply_attr_text_normalization(node, value_key=None):
	"""
	Smartly flattens xmltodict structure.
	1. Flattens attributes ("@key" -> "key") and text ("#text" -> configurable value key).
	2. Handles conflicts: if <tag value="100">text</tag>, keeps original structure to save data.
	3. Smart Empty Tag Handling:
	   - If inside a list: checks siblings. If ANY sibling has text, forces text="" for consistency.
	     If NO siblings have text, leaves them as pure objects.
	   - If single node: checks attributes. If exactly 1 attribute (e.g. <item name="x"/>), forces text="".
	"""
	value_key = value_key or get_attr_text_value_key()

	def _convert(current, is_list_item=False):
		# Base case: primitive types (str, int, none, etc.) return as is
		if not isinstance(current, (dict, list)):
			return current

		# --- CASE 1: Processing a LIST of items (Siblings) ---
		if isinstance(current, list):
			# Check Condition 1: Do any siblings have text?
			siblings_have_text = False
			for item in current:
				if isinstance(item, dict) and '#text' in item:
					siblings_have_text = True
					break
			
			new_list = []
			for item in current:
				# Apply Condition 1 Logic:
				# If we are in a mixed list (some have text), force empty strings on the others for consistency.
				if isinstance(item, dict) and siblings_have_text:
					attr_keys = [k for k in item.keys() if k.startswith('@')]
					child_keys = [k for k in item.keys() if not k.startswith('@') and k != '#text']
					has_text = '#text' in item
					
					# Only force if it's an "empty leaf" (has attrs, no children, no text)
					if attr_keys and not child_keys and not has_text:
						item = item.copy()
						item['#text'] = ""
				
				# Recurse with flag indicating this came from a list
				new_list.append(_convert(item, is_list_item=True))
			return new_list

		# --- CASE 2: Processing a DICT (Single Item) ---
		if isinstance(current, dict):
			new_dict = OrderedDict()
			
			# Analyze the node structure
			attr_keys = [k for k in current.keys() if k.startswith('@')]
			child_keys = [k for k in current.keys() if not k.startswith('@') and k != '#text']
			has_text = '#text' in current

			# --- Fix: Handle Consistency for Empty Tags ---
			if attr_keys and not child_keys and not has_text:
				should_force_text = False
				
				# Condition 2: Single Node Logic (No Siblings)
				# If this is NOT a list item, we look for "Single Attribute" heuristic.
				# e.g., <item key="val"/> -> likely a key-value pair.
				# e.g., <item id="1" type="bool"/> -> likely just an object.
				if not is_list_item:
					if len(attr_keys) == 1:
						should_force_text = True
				
				# Note: If is_list_item is True, we rely entirely on the LIST block above.
				# If the LIST block didn't add #text, it means no siblings had text, so we don't add it here.

				if should_force_text:
					has_text = True
					current = current.copy()
					current['#text'] = ""

			# --- Conflict Detection ---
			conflict = False
			if has_text:
				for k in attr_keys:
					if k[1:] == value_key:
						conflict = True
						break

			for key, val in current.items():
				if conflict:
					# Keep structure on conflict
					new_dict[key] = _convert(val) # Reset is_list_item for children
				else:
					# Flatten
					if key == '#text':
						new_dict[value_key] = val
					elif key.startswith('@'):
						new_dict[key[1:]] = val
					else:
						# Recurse (children are new contexts, not list items of THIS node)
						new_dict[key] = _convert(val) 
			
			return new_dict

		return current

	return _convert(node)

def json2xml(fulltext, pretty=None):
	if pretty is None:
		pretty = get_default_pretty()
	try:
		data = json.JSONDecoder(object_pairs_hook=OrderedDict).decode(fulltext)
		root_name = get_default_root_name() or "root"
		
		# decide if we need to wrap the data
		if isinstance(data, list):
			# Case 1: List at root level (e.g. [{}, {}]) -> Wrap in item tags under root
			wrapped = OrderedDict([(
				root_name, 
				OrderedDict([("item", data)])
			)])
		elif not isinstance(data, dict):
			# Case 2: Primitive types (string, int, etc.) -> Wrap directly
			wrapped = OrderedDict([(root_name, data)])
		else:
			# Case 3: Dictionary
			# We must wrap if:
			# A) There are multiple keys (e.g. {"a":1, "b":2})
			# OR
			# B) There is exactly 1 key, BUT its value is a LIST (e.g. {"string": [{}, {}]})
			#    Because xmltodict expands lists into sibling nodes, creating multiple roots.
			
			need_wrap = False
			if len(data) > 1:
				need_wrap = True
			elif len(data) == 1:
				first_key = list(data.keys())[0]
				first_value = list(data.values())[0]
				
				# 1. If value is a list, xmltodict creates multiple roots -> Must Wrap
				if isinstance(first_value, list):
					need_wrap = True
				# 2. If key looks like an attribute (@...) or text (#text), 
				#    it cannot be a root tag name -> Must Wrap
				elif first_key.startswith('@') or first_key == '#text':
					need_wrap = True

			if need_wrap:
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
