SublimePapyrus
==============

Sublime Text 2 package for the Papyrus scripting language.

Includes function/event snippets and syntax definitions for Skyrim (1.9.32.0.8), [SKSE](http://skse.silverlock.org) (1.7.1), [SkyUI SDK](https://github.com/schlangster/skyui/wiki) (4.1), [FISS](http://www.nexusmods.com/skyrim/mods/48265/) (1.21), [NetImmerse Override](http://www.nexusmods.com/skyrim/mods/37481/) (2.9.2), [DienesTools](http://www.nexusmods.com/skyrim/mods/54325/) (1.0), [JContainers](http://www.nexusmods.com/skyrim/mods/49743/) (3.1.0), [PapyrusUtil](http://www.nexusmods.com/skyrim/mods/49098/) (2.3), and [SkyUILib](https://github.com/schlangster/skyui-lib/wiki) (1).

How do I use the package?
- Install Sublime Text 2, if you do not have it yet. Launch it once in order to make sure all necessary folders are created.
- Get a copy of SublimePapyrus from the repository (recommended) or the CK wiki, if the repository is inaccessible.
- Copy the folder labeled "Papyrus" to "%AppData%\Sublime Text 2\Packages" or "\Sublime Text 2\Data\Packages", if you are using the portable version of Sublime Text 2.
- Copy the contents of the other folders, if you intend to use those resources, and paste them into the folder labeled "Papyrus".
- If you have Skyrim installed outside of "C:\Program Files (x86)\Steam\steamapps\common\skyrim\" or "C:\Program Files\Steam\steamapps\common\skyrim\", then you need to open the Command Palette (CTRL+SHIFT+P), type in "Papyrus INI". An option called "Papyrus INI: Create default INI file" should show up. Select it and a file called "SublimePapyrus.ini" will be created in My Documents. This file contains paths to compiled scripts, script sources, the Papyrus compiler, and paths to libraries you wish to import (optional). Edit the paths according to where you have the relevant files (usually where Skyrim has been installed).
 

How do I use the program SublimePapyrus?

The program can be launched from anywhere and allows you to type in the path to the folder containing the files you wish to process. All subfolders in the input folder will also be processed. If you do not type in a path, then the program will process the folder that the program is in. Generated snippets will be placed in subfolders called "Snippets" in the folders containing the Papyrus source files. The program can also update the syntax definition (Papyrus.tmLanguage) to match the snippets it can find. These two functions, snippet generation and syntax update, can be executed in series or individually.



Based on the work done by Bethesda Game Studios and Mark Hanna. Used according to the license included in the original package and said license is included in this package.

Team: Quad2Core, MrJack
