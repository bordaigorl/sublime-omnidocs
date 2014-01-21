import sublime
import sublime_plugin
from string import Template
from os import path


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
        return "Run "+" ".join(args["cmd"])
    return " ".join([cmd] + list(map(str,args.values())))


class OmniDocsPanelCommand(sublime_plugin.TextCommand):

    def find_options_for(self, scope, local_settings):
        """ Select the most specific entry in the settings """
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
        if item >= 0:
            cmd = items[item][1]
            self.view.window().run_command(cmd["command"], cmd.get("args", {}))

    def run(self, edit):
        view = self.view
        scope = view.scope_name(view.sel()[0].begin()).split()[0].split('.')
        scope, options = self.find_options_for(
            scope, view.settings().get("omni_docs", {}))
        lang = scope.split('.')[-1].capitalize()
        env = {}
        file_fullpath = view.file_name() or ""

        env["file_path"], env["file_name"] = path.split(file_fullpath)
        env["file"] = file_fullpath
        env["file_extension"], env["file_base_name"] = path.splitext(env["file_name"])
        env["packages"] = sublime.packages_path()
        env["project"] = view.window().project_file_name()
        env["project_path"], env["project_name"] = path.split(env["project"])
        env["project_base_name"], env["project_extension"] = path.splitext(env["project_name"])
        env["language"] = lang
        env["selection"] = view.substr(view.sel()[0])
        items = []
        try:
            if "module_docs" in options:
                module_docs = options["module_docs"]
                method = module_docs["method"]
                views = [view]
                modules = set()
                if module_docs["options"].get("across_open_files", False):
                    views += view.window().views()
                if method == "regex":
                    for v in views:
                        mlist = []
                        v.find_all(
                            module_docs["options"]["pattern"],
                            0,
                            module_docs["options"].get("module_name","$0"),
                            mlist)
                        modules |= set(mlist)
                elif method == "selector":
                    for v in views:
                        regions = v.find_by_selector(module_docs["options"]["selector"])
                        modules |= set([v.substr(r) for r in regions])
                else:
                    view.set_status("omni_docs", "Omni Docs: unrecognized method "+method)
                for module in modules:
                    env["module"] = module
                    cmd = {
                        "command": module_docs["command"],
                        "args": jsonmap(apply_template(env), module_docs.get("args", {}))
                    }
                    items.append(
                        (["Show Docs for '"+module+"'", show_effect(cmd)], cmd))
            if "language_docs" in options:
                lang_docs = options["language_docs"]
                lang_docs["args"] = jsonmap(apply_template(env), lang_docs.get("args", {}))
                if lang !=  "default":
                    items += [(["Docs for " + lang, "Show generic help for this language"], lang_docs)]
                else:
                    items += [(["Generic help", show_effect(lang_docs)], lang_docs)]
            view.window().show_quick_panel(
                [item for (item, _) in items],
                lambda i: self.do_show_docs(items, i))
        except (KeyError):
            view.set_status("omni_docs", "Error in Omni Docs settings")
        # print(options)
