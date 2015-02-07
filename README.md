SublimePapyrus
==============

Sublime Text 2 and 3 package for the Papyrus scripting language.

Includes function/event snippets and syntax definitions for:
- Skyrim (1.9.32.0.8)
 - [DienesTools](http://www.nexusmods.com/skyrim/mods/54325/) (1.0)
 - [FISS](http://www.nexusmods.com/skyrim/mods/48265/) (1.21)
 - [JContainers](http://www.nexusmods.com/skyrim/mods/49743/) (3.2)
 - [NetImmerse Override](http://www.nexusmods.com/skyrim/mods/37481/) (2.9.6)
 - [PapyrusUtil](http://www.nexusmods.com/skyrim/mods/58705/) (2.8)
 - [SKSE](http://skse.silverlock.org) (1.7.2)
 - [SkyUILib](https://github.com/schlangster/skyui-lib/wiki) (1)
 - [SkyUI SDK](https://github.com/schlangster/skyui/wiki) (4.1)
 - [UIExtensions](http://www.nexusmods.com/skyrim/mods/57046/) (1.1.0)


##How do I install the package?
- Install Sublime Text 2 or 3, if you do not have it yet. Launch it once in order to make sure all necessary folders have been created.

- Get a copy of SublimePapyrus from the repository (recommended), the Creation Kit wiki, if the repository is inaccessible.

- Loose files: Copy the repository. Copy the contents of the folder labeled "Core" to *"%AppData%\Sublime Text #\Packages\SublimePapyrus"*, or *"\Sublime Text #\Data\Packages\SublimePapyrus"* if you are using the portable version of Sublime Text, (replace # with the version of Sublime Text you are using). Copy the contents of the folders corresponding to the libraries you want to use from the subfolders found in the folder labeled "Libraries" to the same folder that was used mentioned in the previous step. You will most likely want to at least copy the contents of the Skyrim library.

- Packaged: Download a [release](https://github.com/Kapiainen/SublimePapyrus/releases). Copy SublimePapyrus.sublime-package (and any other .sublime-package files you want) to *"%AppData%\Sublime Text #\Data\Installed Packages"*, or *"\Sublime Text #\Data\Installed Packages"* if you are using the portable version of Sublime Text, (replace # with the version of Sublime Text you are using).

- If you have Skyrim installed outside of *"C:\Program Files (x86)\Steam\steamapps\common\skyrim\" or "C:\Program Files\Steam\steamapps\common\skyrim\"*, then you need to open the Command Palette (CTRL+SHIFT+P), type in *"SublimePapyrus INI"*. An option called *"SublimePapyrus: Create default INI file"* should show up. Select it and a file called *SublimePapyrus.ini* will be created in *My Documents*. This file contains paths to compiled scripts, script sources, the Papyrus compiler, and paths to libraries you wish to import (optional). Edit the paths according to where you have the relevant files (usually where Skyrim has been installed).

If you are using [Advanced Papyrus](https://github.com/Kapiainen/Advanced-Papyrus), then you should set the *compiler* option in *SublimePapyrus.ini* to point to the actual compiler, which would be called *PapyrusCompiler - Original.exe*, rather than the wrapper program.

##Features
- [Autocomplete](#autocomplete)
- [Syntax highlighting](#syntax-highlighting)
- [Build systems](#build-systems)
- [Commands](#commands)
	- [Create default INI file](#create-default-ini-file)
	- [Open script](#open-script)
	- [Open parent script](#open-parent-script)
	- [Clear compiler error highlights](#clear-compiler-error-highlights-sublime-text-3-only)
	- [Insert *enter noun here*](#insert-enter-noun-here-sublime-text-3-only)
- [Highlight compiler errors](#highlight-compiler-errors-sublime-text-3-only)
- [Hide successful build results](#hide-successful-build-results-sublime-text-3-only)

####Autocomplete
Functions and events that exist in supported libraries (see above) can be autocompleted via snippets. Type in only the name of the function or event. Function snippets will insert a function call. If you start typing the word *AddItem*, then the following will be inserted when you choose to autocomplete:
```papyrus
AddItem(Form akItemToAdd, int aiCount = 1, bool abSilent = false)
```

Event snippets will insert an entire event declaration. If you start typing the word *OnActivate*, then the following will be inserted when you choose to autocomplete:
```papyrus
Event OnActivate(ObjectReference akActionRef)

EndEvent
```

You can cycle through the arguments in both cases by pressing Tab (Shift+Tab to go backwards).

Snippets can be browsed in the Command Palette (Ctrl+Shift+P), which means that you can for example get a list of all functions and events in a particular script. You could have a look at all SKSE functions and events in the *Actor* script by typing in the following in the Command Palette while actively working on a file with the syntax set to *Papyrus*:
```
actor (skse)
```

There are also snippets for autocompleting statements like property declarations, while-loops, and scriptname.


####Syntax highlighting
Syntax highlighting for all keywords defined in Papyrus as well as names of all scripts, functions, and events in supported libraries (see above). Syntax highlighting is also available for Papyrus assembly files.


####Build systems
You can now compile Papyrus scripts from Sublime Text as long as you have defined the path to the Papyrus compiler and flags in *SublimePapyrus.ini*. The various INI settings are documented in detail in the INI file generated via the *SublimePapyrus: Create default INI file* command. 

The *Import* section of the INI file is of particular interest as it allows you to keep various scripts, and their source files, separate, which can be useful if you for example use [Mod Organizer](http://www.nexusmods.com/skyrim/mods/1334/).

There are also build systems for disassembling bytecode (.pex), and converting assembly (.pas) in to bytecode.

####Commands
######Create default INI file
If you type in the command *SublimePapyrus: Create default INI file* in the Command Palette, then the default *SublimePapyrus.ini* file is created in your *My Documents* folder. If you already have such a file, then a dialog asking whether or not you want to open it is opened. This INI file contains paths to your copy of the Papyrus compiler, folders containing scripts, etc. More details about the various options can be found in the INI file.


######Open script
If you type in the command *SublimePapyrus: Open script* in the Command Palette, then an input panel is shown at the bottom of the window. You can then type in a regular expression, which conforms to Python's regular expression standard, in order to open a matching script or get a list of multiple matches. The folders that are included in the search are: the folder of the currently active file open in Sublime Text, the folder defined in the INI file's *scripts* option in the *Skyrim* section, any folders defined in the INI file's *path\** options in the *Import* section. If you leave the input panel empty, but you have selected something in the currently active file, then the command will look for scripts matching the contents of the selection. You do not need to include the extension of the script nor special characters for the start (^) or end ($) of a string as those are added automatically. So if you input the following:
```
Actor
```
then that will make the command look for files matching the following pattern (case-insensitive):
```
^(actor\.psc)$
```

You could search for any script containing the substring "armor" by typing in the following in the input panel:
```
.*armor.*
```
as that would look for files matching the following pattern:
```
^(.*armor.*\.psc)$
```


######Open parent script
If you type in the command *SublimePapyrus: Open parent script* in the Command Palette, then the currently active file will be parsed for a line that looks something like this:
```papyrus
ScriptName X Extends Y
```
*X* is the name of the script and *Y* is the name of the parent script. If *extends Y* cannot be found in the file or a script named *Y* cannot be found, then the command will not open anything. If *extends Y* can be found in the file, then *Y* will be searched for just like in the command *SublimePapyrus: Open script*.

######Clear compiler error highlights (Sublime Text 3 only)
If you type in the command *SublimePapyrus: Clear compiler error highlights*, then any lines highlighted with the *Highlight compiler errors* feature will cease to be highlighted. In case it takes a long period of time before you attempt to compile your script again and you find the highlighting to be distracting.


######Insert *enter noun here* (Sublime Text 3 only)
This command can be used to insert valid arguments for functions like SKSE's *RegisterForMenu*. The commands follow the template *SublimePapyrus: Insert X (Library's name)*, where *X* is replaced with for example *menu name*. The purpose of these commands is to alleviate or even remove the need to either memorize valid options or look up the relevant documentation.

This feature has to be implemented on a per-library basis. This feature is currently supported by the following libraries:

- Skyrim
	- Actor value names
	- Form type IDs

- SKSE
	- Menu names
	- Input keycodes
	- Controls
	- DefaultObject keys
	- ActorValueInfo names and IDs


*SublimePapyrus: Insert menu name (SKSE)* starts the process of inserting a valid menu name used by SKSE's user interface functions. A menu will pop up showing you a list of valid arguments/menus that you can search through. The elements in the list are descriptive, but the actual menu name used by the functions will be inserted at the caret or replace the current selection. For example choosing the *Barter* option in the list will insert, or replace a selection, with *"BarterMenu"*.


####Highlight compiler errors (Sublime Text 3 only)
Lines, which cause the Papyrus compiler to report errors, can be automatically highlighted when compiling scripts in Sublime Text.

This feature is disabled by default and can be enabled in *Preferences -> Package Settings -> SublimePapyrus -> Settings - User*.


####Hide successful build results (Sublime Text 3 only)
Automatically hide the build results when the Papyrus compiler finishes without any errors when compiling scripts in Sublime Text. In case you want this feature to only apply to Papyrus scripts rather than using Sublime Text's *show_panel_on_build*, which applies to all build results.

This feature is disabled by default and can be enabled in *Preferences -> Package Settings -> SublimePapyrus -> Settings - User*.

 
##Credits
Based on the work done by Bethesda Game Studios and Mark Hanna. Used according to the license included in the original package and said license is included in this package.

Team: Quad2Core, MrJack
