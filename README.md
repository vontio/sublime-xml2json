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
 - use `cmd+shift+P` then `Pretty JSON`, `Pretty XML`, `Compact JSON` or `Compact XML` to format the current buffer without saving
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

- `empty_tag_style`: how empty tags are written when generating XML. `compact` (`<tag/>`, default), `spaced` (`<tag />`), `expanded` (`<tag></tag>`).
- `pretty_json_indent`: indentation size for pretty JSON (default `2`).
- `pretty_xml_indent`: indentation size for pretty XML (default `2`).
- `default_conversion_pretty`: whether conversion commands default to pretty (`true`/`"pretty"`) or compact (`false`/`"compact"`); default `true`.
- `json_ensure_ascii`: whether to escape non-ASCII when emitting JSON (default `false`).
- `json_sort_keys`: whether to sort keys when emitting JSON (default `false`).
- `normalize_attribute_text_pairs`: when converting XML to JSON, convert simple attribute/text pairs (e.g., `{"@name": "...", "#text": "..."}`) into `{name: "...", value: "..."}` (default `true`).
- `attribute_text_value_key`: key name to store text content when `normalize_attribute_text_pairs` is enabled (default `"value"`).
- `default_xml_root_name`: fallback root element name when wrapping JSON that lacks a single root (default `"root"`).
- `include_xml_declaration`: include `<?xml version="1.0" encoding="utf-8"?>` when converting JSON to XML (default `true`).
- `line_ending`: line endings for generated output: `auto` (preserve from source), `unix` (`\n`), `windows` (`\r\n`), `mac` (`\r`) (default `auto`).
- `ensure_final_newline`: ensure generated output ends with a newline (default `true`).
- `trim_trailing_whitespace`: trim trailing spaces/tabs on generated lines (default `true`; removes spaces after commas in pretty JSON).

You can adjust plugin settings and shortcuts via `Sublime Text` -> `Settings` -> `Package Settings` -> `xml2json` -> `Settings` and `Key Bindings`.

 [0]: http://wbond.net/sublime_packages/package_control
