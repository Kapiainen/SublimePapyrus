SublimePapyrus
==============

Sublime Text 2 package for the Papyrus scripting language.

Includes function/event snippets and syntax definitions for Skyrim (1.9.32.0.8), SKSE (1.7.1), SkyUI SDK (4.1), FISS (1.21), and NetImmerse Override (2.7.1).

How do I use the package?
- Install Sublime Text 2, if you do not have it yet. Launch it once in order to make sure all necessary folders are created. Check the Creation Kit wiki for instructions on how to set up the Papyrus compiler for use with external editors.
- Get a copy of SublimePapyrus from the repository (recommended) or the CK wiki, if the repository is inaccessible.
- Copy the folder labeled "Papyrus" to "%AppData%\Sublime Text 2\Packages" or "\Sublime Text 2\Data\Packages", if you are using the portable version of Sublime Text 2.
- Copy the contents of the other folders, if you intend to use those resources, and paste them into the folder labeled "Papyrus".
- If you have Skyrim installed outside of "C:\Program Files (x86)\Steam\steamapps\common\skyrim\" or "C:\Program Files\Steam\steamapps\common\skyrim\", then you need to open the Command Palette (CTRL+SHIFT+P), type in "Papyrus INI". An option called "Papyrus INI: Create default INI file" should show up. Select it and a file called "SublimePapyrus.ini" will be created in My Documents. This file contains paths to compiled scripts, script sources, and the Papyrus compiler. Edit the paths according to where you have installed Skyrim.
 

How do I use the program PapyrusToSublimeSnippets?

The program can be launched from anywhere and allows you to type in the path to the folder containing the Papyrus source files you wish to process. If you do not type in a path, then the program will process the folder the program is in. You can also type in the path to the folder you wish to output the resulting logs and snippets to. If you do not type in a path, then the resulting files will be output to a folder called "snippets" in the folder that the program is in. The snippets can then be copied over into the Papyrus package.
 
The program creates two logs: FunctionLog.txt and ClassLog.txt. These contain keywords, which are formatted for use in the Papyrus syntax definition (Papyrus.tmLanguage), based on the processed source files. The syntax definition can be found in the Papyrus package.



Based on the work done by Bethesda Game Studios and Mark Hanna. Used according to the license included in the original package and said license is included in this package.

Program, for automated creation of snippets, created by Quad2Core.

Team: Quad2Core, MrJack
