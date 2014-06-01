import sublime, sublime_plugin
import p4lib
import sys
import os
import tempfile
import difflib
import ConfigParser

# This may only work on Windows 7 and up -- fine for our purposes
INI_LOCATION = os.path.expanduser("~/Documents/SublimePapyrus.ini")

# Default values for a standardized Steam installation (for end-users and modders)
if (os.path.exists("C:\\Program Files (x86)")):
    END_USER_ROOT = "C:\\Program Files (x86)\\Steam\\steamapps\\common\\skyrim"
else:
    END_USER_ROOT = "C:\\Program Files\\Steam\\steamapps\\common\\skyrim"
END_USER_OUTPUT   = os.path.join(END_USER_ROOT, "Data\\Scripts")
END_USER_SCRIPTS  = os.path.join(END_USER_OUTPUT, "Source")
END_USER_COMPILER = os.path.join(END_USER_ROOT, "Papyrus Compiler\\PapyrusCompiler.exe")
END_USER_FLAGS    = "TESV_Papyrus_Flags.flg"

DEFAULT_INI_TEXT = """[Skyrim]
scripts=%s
compiler=%s
output=%s
workspace=
flags=%s
""" % (END_USER_SCRIPTS, END_USER_COMPILER, END_USER_OUTPUT, END_USER_FLAGS)




def recursivePathCheck(path, target):
    path = os.path.normcase(path)
    target = os.path.normcase(target)
    if (path == target):
        return True

    while True:
        upPath = os.path.dirname(path)
        if (upPath == path):
            return False
        path = upPath
        if (path == target):
            return True




def getPrefs(currentDir):
    ret = {}

    if (not os.path.exists(INI_LOCATION)):
        ret["scripts"]   = END_USER_SCRIPTS
        ret["compiler"]  = END_USER_COMPILER
        ret["output"]    = END_USER_OUTPUT
        ret["workspace"] = "" # no P4 access for modders, but let's fill this in anyway
        ret["flags"]     = END_USER_FLAGS
    else:
        parser = ConfigParser.ConfigParser()
        parser.read(INI_LOCATION)
        for config in parser.sections():
            path = parser.get(config, "scripts")
            if (recursivePathCheck(currentDir, path)):
                for k in parser.items(config):
                    ret[k[0]] = k[1]
                break

    if ("import" not in ret):
        ret["import"] = ret["scripts"]
    return ret

def checkout(filename, prefs):
    user_client = prefs["workspace"]
    p4 = p4lib.P4(client=user_client)
    output = p4.edit(filename)
    sublime.status_message("%s: %s" % (output[0]["depotFile"], output[0]["comment"]))

def getTempFileName(truefilename, rev=None):
    basename = os.path.basename(truefilename)
    fname = os.path.join(tempfile.gettempdir(), "SublimePapyrus")
    if not os.path.exists(fname):
        os.makedirs(fname)
    fname = os.path.join(fname, os.path.splitext(basename)[0])
    if (rev is not None):
        fname += "#%i" % rev
    fname += os.path.splitext(truefilename)[1]
    return fname

def getRevisionListFor(filename, prefs):
    user_client = prefs["workspace"]
    p4 = p4lib.P4(client=user_client)
    revisions = p4.filelog(filename, longOutput=1)[0]["revs"]
    width = len(str(len(revisions)))
    revList = []
    for rev in revisions:
        revString = "[%s]: %s, %s" % (str(rev["rev"]).zfill(width), rev["user"], rev["date"])
        descString = rev["description"]
        revTuple = [revString, descString]
        revList.append(revTuple)
    return revList

def openDiffInTab(viewHandle, edit, name, oldText, newText):
    diffs = difflib.unified_diff(oldText.splitlines(), newText.splitlines())
    diffText = "\n".join(list(diffs))
    
    scratch = viewHandle.window().new_file()
    scratch.set_scratch(True)
    scratch.set_name(name)
    scratch.set_syntax_file("Packages/Diff/Diff.tmLanguage")
    scratch.insert(edit, 0, diffText)




class ViewOldRevisionCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        self.fileName = self.view.file_name()
        prefs = getPrefs(os.path.dirname(self.fileName))
        revs = getRevisionListFor(self.fileName, prefs)
        self.revLength = len(revs)
        self.view.window().show_quick_panel(revs, self.onSelect)

    def onSelect(self, index):
        if (index == -1):
            return
        rev = self.revLength - index
        prefs = getPrefs(os.path.dirname(self.fileName))
        user_client = prefs["workspace"]
        p4 = p4lib.P4(client=user_client)
        revText = p4.print_("%s#%i" % (self.fileName, rev))[0]["text"]
        
        tempFileName = getTempFileName(self.fileName, rev)
        tempFileHandle = open(tempFileName, "w")
        tempFileHandle.write(revText)
        tempFileHandle.close()

        self.view.window().open_file(tempFileName)

class DiffOldRevisionCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        self.edit = edit
        self.fileName = self.view.file_name()
        prefs = getPrefs(os.path.dirname(self.fileName))
        revs = getRevisionListFor(self.fileName, prefs)
        self.revLength = len(revs)
        self.view.window().show_quick_panel(revs, self.onSelect)

    def onSelect(self, index):
        if (index == -1):
            return
        rev = self.revLength - index
        prefs = getPrefs(os.path.dirname(self.fileName))
        user_client = prefs["workspace"]
        p4 = p4lib.P4(client=user_client)
        revText = p4.print_("%s#%i" % (self.fileName, rev))[0]["text"]
        currText = self.view.substr(sublime.Region(0, self.view.size()))

        openDiffInTab(self.view, self.edit, "Diff of %s and Perforce revision #%i" % (self.fileName, rev), revText, currText)

class DiffAgainstPerforce(sublime_plugin.TextCommand):
    def run(self, edit):
        self.fileName = self.view.file_name()
        prefs = getPrefs(os.path.dirname(self.fileName))
        user_client = prefs["workspace"]
        p4 = p4lib.P4(client=user_client)
        revText = p4.print_(self.fileName)[0]["text"]
        currText = self.view.substr(sublime.Region(0, self.view.size()))

        openDiffInTab(self.view, edit, "Diff of %s and Perforce head" % (self.fileName), revText, currText)

class CheckOutFromP4Command(sublime_plugin.TextCommand):
    def run(self, edit):
        checkout(self.view.file_name())

class PreEmptiveCheckOutPlugin(sublime_plugin.EventListener):
    def on_pre_save(self, view):
        prefs = getPrefs(os.path.dirname(view.file_name()))
        if (len(prefs) > 0):
            if (not os.access(view.file_name(), os.W_OK)):
                checkout(view.file_name(), prefs)

class CreateDefaultSettingsFileCommand(sublime_plugin.WindowCommand):
    def run(self, **args):
        if os.path.exists(INI_LOCATION):
            sublime.status_message("ERROR: INI file already exists at %s" % (INI_LOCATION))
        else:
            outHandle = open(INI_LOCATION, "w")
            outHandle.write(DEFAULT_INI_TEXT)
            outHandle.close()
            self.window.open_file(INI_LOCATION)

class CompilePapyrusCommand(sublime_plugin.WindowCommand):
    def run(self, **args):
        config = getPrefs(os.path.dirname(args["cmd"]))
        if (len(config) > 0):
            scriptPath = args["cmd"][len(config["scripts"])+1:]

            args["cmd"] = [config["compiler"], scriptPath]
            args["cmd"].append("-f=%s" % config["flags"])
            args["cmd"].append("-i=%s" % config["import"])
            args["cmd"].append("-o=%s" % config["output"])

            args["working_dir"] = os.path.dirname(config["compiler"])

            self.window.run_command("exec", args)
        else:
            sublime.status_message("No configuration for %s" % os.path.dirname(args["cmd"]))

class DisassemblePapyrusCommand(sublime_plugin.WindowCommand):
    def run(self, **args):
        scriptPath = args["cmd"]

        scriptDir = os.path.dirname(scriptPath)
        assembler = os.path.join(scriptDir, "PapyrusAssembler.exe")            
        scriptPath = os.path.splitext(os.path.basename(scriptPath))[0]
        args["cmd"] = [assembler, scriptPath]
        args["cmd"].append("-V")
        args["cmd"].append("-D")

        args["working_dir"] = scriptDir

        self.window.run_command("exec", args)

        disassembly = os.path.join(scriptDir, scriptPath + ".disassemble.pas")
        disassemblyFinal = os.path.join(scriptDir, scriptPath + ".pas")
        os.rename(disassembly, disassemblyFinal)
        if (os.path.exists(disassemblyFinal)):
            self.window.open_file(disassemblyFinal)

class AssemblePapyrusCommand(sublime_plugin.WindowCommand):
    def run(self, **args):
        scriptPath = args["cmd"]

        scriptDir = os.path.dirname(scriptPath)
        assembler = os.path.join(scriptDir, "PapyrusAssembler.exe")            
        scriptPath = os.path.splitext(os.path.basename(scriptPath))[0]
        args["cmd"] = [assembler, scriptPath]
        args["cmd"].append("-V")

        args["working_dir"] = scriptDir

        self.window.run_command("exec", args)

