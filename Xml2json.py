import sublime, sublime_plugin
import json
if sublime.version() >= '3000':
	from . import xmltodict
else:
	import xmltodict

class Xml2jsonCommand(sublime_plugin.TextCommand):
	def run(self,edit):
		fulltext = self.view.substr(sublime.Region(0, self.view.size()))
		jsonObj = xmltodict.parse(fulltext)
		jsonStr = json.dumps(jsonObj)
		newView = sublime.active_window().new_file()
		if sublime.version() >= '3000':
			newView.run_command('append',{'characters':jsonStr})
		else:
			newEdit = newView.begin_edit()
			newView.insert(newEdit,0,jsonStr)
			newView.end_edit(newEdit)
		
class Json2xmlCommand(sublime_plugin.TextCommand):
	def run(self,edit):
		fulltext = self.view.substr(sublime.Region(0, self.view.size()))
		jsonObj = json.loads(fulltext)
		xmlStr = xmltodict.unparse(jsonObj)
		newView = sublime.active_window().new_file()
		if sublime.version() >= '3000':
			newView.run_command('append',{'characters':xmlStr})
		else:
			newEdit = newView.begin_edit()
			newView.insert(newEdit,0,xmlStr)
			newView.end_edit(newEdit)