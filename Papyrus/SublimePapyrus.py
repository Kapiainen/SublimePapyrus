import sublime, sublime_plugin
import os
import sys
PYTHON_VERSION = sys.version_info
SUBLIME_TEXT_VERSION = 2
if (PYTHON_VERSION[0] == 3) and (PYTHON_VERSION[1] == 3):
    # 3.3
    SUBLIME_TEXT_VERSION = 3
if SUBLIME_TEXT_VERSION == 2:
    import ConfigParser
    from StringIO import StringIO
elif SUBLIME_TEXT_VERSION == 3:
    import configparser
    from io import StringIO

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
# The path to the folder containing the vanilla Skyrim .psc files.
scripts=%s

# The path to PapyrusCompiler.exe
compiler=%s

# The folder you wish to output the .pex files to. If commented out (# at the start of a line), then .pex files are placed in the folder one level above the .psc file.
output=%s

# The name of the file containing Papyrus' flags. The file has to be among the folders that are imported, which includes the scripts folder defined above and the folder containing the .psc file(s) to be compiled.
flags=%s

[Import]
# Additional folders that contain .psc you wish to import when compiling.
# Template:
# pathN=Drive:\\Folder1\\Folder2\\Folder_with_PSC_files
# The order in which .psc files are processed is:
# - the path containing the .psc file to compile provided that this path is not the same as the path containing the vanilla Skyrim .psc files
# - path1
# - path2
# .
# .
# .
# - pathN
# - the path containing the vanilla Skyrim .psc files ("scripts=" key above)
#
# For example if you want to separate the vanilla scripts (defined in the "scripts=" key) and SKSE scripts into their own folders (defined as an additional import), then you would define the path to SKSE's .psc files as the value for a "pathN" key.
# path1=Drive:\\Folder\\Subfolder_containing_SKSE_PSC_files
#
""" % (END_USER_SCRIPTS, END_USER_COMPILER, END_USER_OUTPUT, END_USER_FLAGS)

def getPrefs(filePath):
    fileDir, fileName = os.path.split(filePath)
    ret = {}
    ret["compiler"] = END_USER_COMPILER
    ret["output"] = END_USER_OUTPUT
    ret["flags"] = END_USER_FLAGS
    ret["import"] = END_USER_SCRIPTS
    if (os.path.exists(INI_LOCATION)):
        if SUBLIME_TEXT_VERSION == 2:
            parser = ConfigParser.ConfigParser()
        elif SUBLIME_TEXT_VERSION == 3:
            parser = configparser.ConfigParser()
        parser.read([INI_LOCATION])

        if (parser.has_section("Skyrim")):
            if(parser.has_option("Skyrim", "compiler")):
                ret["compiler"] = parser.get("Skyrim", "compiler")

            if(parser.has_option("Skyrim", "output")):
                ret["output"] = parser.get("Skyrim", "output")
            else:
                ret["output"] = os.path.dirname(fileDir)

            if(parser.has_option("Skyrim", "flags")):
                ret["flags"] = parser.get("Skyrim", "flags")

        ret["import"] = []
        if (fileDir != parser.get("Skyrim", "scripts")):
            ret["import"].append(fileDir)
        if (parser.has_section("Import")):
            for configKey, configValue in parser.items("Import"):
                if (configKey.startswith("path")):
                    if (os.path.exists(configValue)):
                            ret["import"].append(configValue)
        
        if (parser.get("Skyrim", "scripts") not in ret["import"]):
            ret["import"].append(parser.get("Skyrim", "scripts"))
        if SUBLIME_TEXT_VERSION == 2:
            ret["import"] = ";".join(filter(None, ret["import"]))
        elif SUBLIME_TEXT_VERSION == 3:
            ret["import"] = ";".join([_f for _f in ret["import"] if _f])

    ret["filename"] = fileName
    return ret

class CompilePapyrusCommand(sublime_plugin.WindowCommand):
    def run(self, **args):
        config = getPrefs(args["cmd"])
        if (len(config) > 0):
            args["cmd"] = [config["compiler"], config["filename"]]
            args["cmd"].append("-f=%s" % config["flags"])
            args["cmd"].append("-i=%s" % config["import"])
            args["cmd"].append("-o=%s" % config["output"])
            args["working_dir"] = os.path.dirname(config["compiler"])
            self.window.run_command("exec", args)
        else:
            sublime.status_message("No configuration for %s" % os.path.dirname(args["cmd"]))

class CreateDefaultSettingsFileCommand(sublime_plugin.WindowCommand):
    def run(self, **args):
        if os.path.exists(INI_LOCATION):
            sublime.status_message("ERROR: INI file already exists at %s" % (INI_LOCATION))
        else:
            outHandle = open(INI_LOCATION, "w")
            outHandle.write(DEFAULT_INI_TEXT)
            outHandle.close()
            self.window.open_file(INI_LOCATION)

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
