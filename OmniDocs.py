import sublime
import sublime_plugin
from string import Template
from os import path
import re

OMNI_DOCS_STATUS = "omni_docs"
OMNI_DOCS_KEY = "omni_docs"

PRETTY_CMD = {
    "open_url": "Browse",
    "open_file": "Open"
}


def jsonmap(f, obj):
    if isinstance(obj, dict):
        objres = {}
        for k in obj.keys():
            objres[k] = jsonmap(f, obj[k])
        return objres
    elif isinstance(obj, list):
        return list(map(lambda x: jsonmap(f, x), obj))
    elif isinstance(obj, str):
        return f(obj)
    else:
        return obj


def apply_template(env={}):
    def resfun(x):
        return Template(x).safe_substitute(env)
    return resfun


def show_effect(opt):
    cmd = opt.get("command", "")
    args = opt.get("args", {})
    if cmd == "exec":
        return "Run " + " ".join(args["cmd"])
    return " ".join([PRETTY_CMD.get(cmd, cmd)] + list(map(str, args.values())))


class OmniDocsCommand(sublime_plugin.TextCommand):

    def find_options(self):
        """ Select the most specific entry in the settings """
        local_settings = self.view.settings().get(OMNI_DOCS_KEY, {})
        scope = self.view.scope_name(self.view.sel()[0].begin()).split()[0].split('.')
        settings = sublime.load_settings("OmniDocs.sublime-settings")
        for sc in local_settings.keys():
            settings.set(sc, local_settings[sc])
        while len(scope) > 0:
            s = '.'.join(scope)
            if settings.has(s):
                return (s, settings.get(s))
            scope.pop()
        return ("default", settings.get("default", {}))

    def do_show_docs(self, items, item):
        self.view.erase_status(OMNI_DOCS_STATUS)
        if item >= 0:
            cmd = items[item][1]
            sublime.set_timeout(
                lambda: self.view.window().run_command(cmd["command"], cmd.get("args", {})),
                0)

    def make_env(self, scope):
        view = self.view
        env = {}
        file_fullpath = view.file_name() or ""
        env["file_path"], env["file_name"] = path.split(file_fullpath)
        env["file"] = file_fullpath
        env["file_extension"], env[
            "file_base_name"] = path.splitext(env["file_name"])
        env["packages"] = sublime.packages_path()
        env["project"] = view.window().project_file_name()
        env["project_path"], env["project_name"] = path.split(env["project"])
        env["project_base_name"], env[
            "project_extension"] = path.splitext(env["project_name"])
        env["language"] = scope.split('.')[-1].capitalize()
        env["selection"] = view.substr(view.sel()[0])
        return env


class OmniDocsPanelCommand(OmniDocsCommand):

    def run(self, edit, always_show_choices=True, only_current_view=False):
        view = self.view
        view.erase_status(OMNI_DOCS_STATUS)

        scope, options = self.find_options()
        view.set_status(OMNI_DOCS_STATUS, "OmniDocs "+scope)

        env = self.make_env(scope)

        items = []

        try:

            # FIND MODULES DOCUMENTATION
            if "module_docs" in options:
                module_docs = options["module_docs"]
                views = [view]
                modules = set()

                if module_docs.get("across_open_files", False) and not only_current_view:
                    views += view.window().views()

                if "patterns" in module_docs:
                    for pat in module_docs["patterns"]:
                        for v in views:
                            mlist = []
                            v.find_all(
                                pat["import_regex"], 0,
                                pat.get("import_capture", "$0"), mlist)
                            if "module_regex" in pat:
                                sublist = []
                                mpat = re.compile(pat["module_regex"], re.MULTILINE)
                                for m in mlist:
                                    for match in mpat.finditer(m):
                                        if "module_capture" in pat:
                                            sublist.append(match.expand(pat["module_capture"]))
                                        else:
                                            sublist.append(match.group(0))

                                mlist = sublist

                            modules |= set(mlist)

                if "selector" in module_docs:
                    for v in views:
                        regions = v.find_by_selector(module_docs["selector"])
                        modules |= set([v.substr(r) for r in regions])

                for module in modules:
                    env["module"] = module
                    cmd = {
                        "command": module_docs["command"],
                        "args": jsonmap(apply_template(env), module_docs.get("args", {}))
                    }
                    items.append(
                        (["Show Docs for '" + module + "'", show_effect(cmd)], cmd))

            # LANGUAGE DOCUMENTATION
            if "language_docs" in options:
                lang_docs = options["language_docs"]
                lang = env["module"] = env["language"]
                lang_docs["args"] = jsonmap(
                    apply_template(env), lang_docs.get("args", {}))
                if lang != "default":
                    items += [
                        ([lang + " reference", "Show generic help for this language"], lang_docs)]
                else:
                    items += [
                        (["Generic help", show_effect(lang_docs)], lang_docs)]

            # SHOW THE PANEL
            if len(items) > 1 or always_show_choices:
                view.window().show_quick_panel(
                    [item for (item, _) in items],
                    lambda i: self.do_show_docs(items, i))
            else:
                self.do_show_docs(items, 0)

        except (KeyError):
            view.set_status(OMNI_DOCS_STATUS, "Error in Omni Docs settings")


class OmniDocsLookupCommand(OmniDocsCommand):

    def run(self, edit):
        view = self.view
        view.erase_status(OMNI_DOCS_STATUS)

        scope, options = self.find_options()

        env = self.make_env(scope)

        try:

            if "lookup_docs" in options:
                    cmd = options["lookup_docs"]["command"]
                    args = jsonmap(apply_template(env), options["lookup_docs"].get("args", {}))
                    view.window().run_command(cmd, args)

        except (KeyError):
            view.set_status(OMNI_DOCS_STATUS, "Error in Omni Docs settings")