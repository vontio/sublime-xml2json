Sublime xml to json and json to xml
===============================

convert xml file to json file or json file to xml file.

## Installation:

 - you should use [sublime package manager][0]
 - use `cmd+shift+P` then `Package Control: Install Package`
 - look for `xml2json` and install it.
 - OR, Clone or unpack to "xml2json" folder inside "Packages" of your Sublime installation.

## Usage :

 - use `cmd+shift+P` then `xml2json` or `json2xml`
 - or goto menubar `Tools` then `xml2json` or `json2xml`
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

 [0]: http://wbond.net/sublime_packages/package_control
