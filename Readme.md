# Omni Docs plugin for Sublime Text 3

A simple plugin for Sublime Text 3 for jumping to documentation for:

 1. selected symbols
 2. imported modules / API
 3. language reference

It supports some languages are supported out-of-the-box but other can be added by customising the settings.

The basic usage is pressing <kbd>F1</kbd> when needing help:

 * if something is selected then OmniDocs will search for the selected symbol in the docs for the current programming language;
 * if nothing is selected a quick panel will display a list of the currently imported modules, allowing you to open the corresponding documentation with one click.

<!-- Screenshot -->

## Installation

 1. Install [Sublime Text 3](http://www.sublimetext.com/3)
 2. Install the plugin either:
 
     a. with **Package Control**: see <https://sublime.wbond.net/installation>, or
     b. **manually**: by cloning this repository in your Sublime Text Package directory

## Usage

The plugin offers two commands: `omni_docs_panel` and `omni_docs_lookup`.

The command `omni_docs_panel` looks for imported modules in the current view or the currently open views, depending on settings, and displays a quick panel with the available documentation for them.

The `omni_docs_lookup` command looks up the current selection in the documentation.

The settings control, on a per-language basis, how the documentation should be accessed and shown; most of the presets open official online references but this can be fully customised in the settings, see [#configuration].

### Key bindings and commands

### Supported languages

 + Python
 + Markdown (only syntax reference)
 + Haskell
 + LaTeX

## Configuration

OmniDocs is designed to support any language, custom documentation sources and even other plugins. All you have to do to support a new language, change docs sources or call a custom command from OmniDocs, is changing few lines in the settings.

The settings can be customised in the file `OmniDocs.sublime-settings`. The settings can also be accessed from `Preferences > Package Preferences > Omni Docs`.

The basic structure of the settings is the following:

```
{
    <selector>: {
        "language_docs": {
            "command": <command>,
            "args": <args>
        },
        "lookup_docs": {
            "command": <command>,
            "args": <args>
        },
        "module_docs": {
            "method": <method>,
            "options": <method-options>,
            "across_open_files": <true/false>,
            "command": <command>,
            "args": <args>           
        }
    },
    ...
}
```

The `<selector>` controls when the rules apply. It can be for example `text.html`; OmniDocs will look for the most specific selector for which there are rules. For example an entry `text.html.markdown` will be triggered in a markdown document even if an entry for `text.html` exists.

If the settings for a particular selector is left empty (i.e. `<selector>: {}`), then that scope will be disabled.

The special selector `default` will trigger when no selector matched the scope of the current selection.

`<command>` can be any Sublime Text window-command, even provided by another plugin. For example `"command": "open_url", "args": {"url": <url>}` will open `<url>` in your browser.

The `<args>` field can contain any of the [Build System variables](http://docs.sublimetext.info/en/latest/reference/build_systems.html#build-system-variables) plus

<table>
  <tr> <td><code>$selection</code></td><td>Holds the currently selected text if any</td> </tr>
  <tr> <td><code>$language</code></td><td>Holds the name of the language</td> </tr>
</table>

There are three main sections in the settings for a selector: `language_docs`, `lookup_docs` and `module_docs`.

## Language and Lookup docs

The `language_docs` and `lookup_docs` specify which command has to be executed when the user requests the reference for the current language and help on a selected symbol respectively.
The `args` field of the `lookup_docs` setting should contain the `$selection` variable to show relevant information. For example a generic `lookup_docs` setting could be `{"command": "open_url", "args": {"url": "http://www.google.com?q=$selection"}}`.

## Module docs

The `module_docs` section is more complex as it needs to specify how OmniDocs should find the imported modules.

## Example

```json
    "text.tex": {
        "module_docs": {
            "method": "regex",
            "options": {
                "pattern": "\\\\usepackage(\\[\\w*\\])?\\{(\\w*)\\}",
                "module_name": "$2"
            },
            "across_open_files": true,
            "command": "exec",
            "args": {"cmd": ["texdoc", "${module}"]}
        },
        "language_docs":{
            "command": "open_url",
            "args": {"url": "http://svn.gna.org/viewcvs/*checkout*/latexrefman/trunk/latex2e.html"}
        },
        "lookup_docs": {
            "command": "open_url",
            "args": {"url": "http://tex.stackexchange.com/search?q=${selection}"}
        }
    }
```

## Todo

 + Extend matching scheme to support multiple imports on same statement
 + Built-in support for more languages

## Licence