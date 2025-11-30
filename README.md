Sublime xml to json and json to xml
===============================

convert xml file to json file or json file to xml file.

## Installation:

 - you should use [sublime package manager][0]
 - use `cmd+shift+P` then `Package Control: Install Package`
 - look for `xml2json` and install it.
 - OR, Clone or unpack to "xml2json" folder inside "Packages" of your Sublime installation.

## Usage :

 - use `cmd+shift+P` then `xml2json` or `json2xml` (opens result in a new unsaved buffer)
 - use `cmd+shift+P` then `xml2json (Save to file)` or `json2xml (Save to file)` to save next to the source file (e.g. `abc.xml` -> `abc.json`, `abc.json` -> `abc.xml`); if the target exists you will be asked whether to overwrite, and choosing not to overwrite leaves the result in an unsaved buffer
 - use `cmd+shift+P` then `Pretty JSON (Keep Order)` to format JSON while preserving key order (edits the current buffer without saving)
 - use `cmd+shift+P` then `Pretty XML`, `Compact JSON`, or `Compact XML` to format the current buffer without saving
 - or goto menubar `Tools` then `xml2json`
 - or bind some key in your user key binding:

  ```js
    {
	 "keys": ["ctrl+alt+shift+j"],
	 "command": "xml2json"
	},
	{
	 "keys": ["ctrl+alt+shift+l"],
	 "command": "json2xml"
	}
  ```

## Settings

- Configure `empty_tag_style` in `xml2json.sublime-settings` to control empty tag output when generating XML. Options: `compact` (`<tag/>`, default), `spaced` (`<tag />`), `expanded` (`<tag></tag>`).

 [0]: http://wbond.net/sublime_packages/package_control
