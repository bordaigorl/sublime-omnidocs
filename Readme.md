# Omni Docs plugin for Sublime Text

A simple plugin for Sublime Text for jumping to documentation for:

 1. selected symbols
 2. imported modules / API
 3. language reference

Some languages are supported out-of-the-box (see [Supported Languages](#languages-supported-out-of-the-box)) but other can be added by [customising the settings](#configuration).

The basic usage is pressing <kbd>F1</kbd> when needing help; a panel will be shown with the possible options:

![Imgur](http://i.imgur.com/rQPqvou.png)

## Changelog

 - **Version 1.1.0**:
     + added support for Sublime Text 2
     + added docs patterns for Erlang

## Installation

 1. Install [Sublime Text 3](http://www.sublimetext.com/3)
 2. Install the plugin either:
 
     - with **Package Control**: <kbd>ctrl+shift+P</kbd>, type "Install Package" and select "OmniDocs"; see <https://sublime.wbond.net/docs/usage>, or
     - **manually**: by cloning this repository in your Sublime Text Package directory `git clone git@github.com:bordaigorl/sublime-omnidocs.git` in your packages directory

## Usage

The plugin offers two commands: `omni_docs_panel` and `omni_docs_lookup`.

The command `omni_docs_panel` looks for imported modules in the current view or the currently open views, depending on settings, and displays a quick panel with the available documentation for them.

The `omni_docs_lookup` command looks up the current selection in the documentation.

The settings control, on a per-language basis, how the documentation should be accessed and shown; most of the presets open official online references but this can be fully customised in the settings, see [Configuration](#configuration).

### Key bindings and commands

The default keymap binds <kbd>F1</kbd> so that when it is pressed:

 * if something is selected then OmniDocs will search for the selected symbol in the docs for the current programming language;
 * if nothing is selected a quick panel will display a list of the currently imported modules, allowing you to open the corresponding documentation with one click.

To see the available commands you can bring up the commands panel with <kbd>ctrl+shift+P</kbd> and typing "OmniDocs".

### Languages supported out-of-the-box

 + Python
 + Markdown (only syntax reference)
 + Haskell
 + LaTeX
 + Java
 + Scala

Support for other languages can be easily added through the settings.

## Configuration

OmniDocs is designed to support any language, custom documentation sources and even other plugins. All you have to do to support a new language, change docs sources or call a custom command from OmniDocs, is changing few lines in the settings.

The settings can be customised in the file `OmniDocs.sublime-settings`. The settings can also be accessed from `Preferences > Package Preferences > Omni Docs`.

> **Note**: we refer to *import* any language construct that loads some documented external component; we call *modules* such components. Examples of imports are python's `import` statements or LaTeX' `\usepackage`. Examples of modules are python's `os.path` and LaTeX' `tikz`.

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
            <matching-method>,
            "across_open_files": <true/false>,
            "command": <command>,
            "args": <args>           
        }
    },
    ...
}
```

The `<selector>` controls when the rules apply. It can be for example `text.html`; OmniDocs will look for the most specific selector for which there are rules. For example an entry `text.html.markdown` will be triggered in a markdown document even if an entry for `text.html` exists.

If the settings for a particular selector is left empty (i.e. `<selector>: {}`), then that scope will be disabled; similarly, you can disable a specific section by setting it to the empty object.

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
The `args` field of the `lookup_docs` setting should contain the `$selection` variable to show relevant information. For example a generic `lookup_docs` setting could be `{"command": "open_url", "args": {"url": "http://www.google.com/#q=$selection"}}`.

## Module docs

The `module_docs` section is more complex as it needs to specify how OmniDocs should find the imported modules.
There are two methods to specify this: based on *scopes* and based on *patterns*.

### Scope based method

The first and simplest method uses selectors to find the module names.
For example, in java (with the standard ST3 Java syntax definition) the imported module name in `import` statements are marked with the scope `meta.import storage.modifier.import`:

```json
"source.java": {
    "module_docs": {
        "selector": "meta.import storage.modifier.import",
        "across_open_files": true,
        "command": "open_url",
        "args": {"url": "http://javadocs.org/$module"}
    }
}
```

If instead you prefer the names of the classes used in the code to be detected as possible topics of the documentation you could use

```json
    "selector": "storage.type - storage.type.primitive"
```

### Pattern based method

Instead of the `selector` setting a `patterns` array can specify how to extract the imports using regular expressions (*regex*).

```
"module_docs": {
    "patterns": [
        {
            "import_regex":   <regex>
            "import_capture": <capture> // optional
            "module_regex":   <regex>   // optional
        },
        ...
    ]
}
```

The pattern based method works in two phases.
First, the `import_regex` regex is used to extract the lines containing imports. With `import_capture` you can use capture groups of the `import_regex`  to extract from it the name(s) of the imported module(s); if left unspecified the full match is used.
Second, if `module_regex` is specified, it is used to extract from a match possibly multiple names of modules. This step is optional but necessary to parse imports that include more than a module.

For example, to parse `import string, os.path` in python you need to match the import with `"import_regex": "^\\s*import\\s+([a-zA-Z0-9.\\-\\_, ]+)$"`, capture the list of modules with `"import_capture": "$1"` and finally specify `"module_regex": "[a-zA-Z0-9.\\-\\_]+"` so that the module names can be matched in the extracted list.


## Example configuration

```json
"text.tex": {
    "module_docs": {
        "patterns": [{
            "import_regex": "\\\\usepackage(\\[\\w*\\])?\\{([^\\}]*)\\}",
            "import_capture": "$2",
            "module_regex": "[^ \n\t,]+"
        }],
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

 + Built-in support for more languages
 + Add a command to request parse and display json for docs
 + Consider switching to settings driven by syntax specific setting files
