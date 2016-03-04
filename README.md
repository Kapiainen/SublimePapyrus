**SublimePapyrus**
==
A Sublime Text 2 and 3 package for the Papyrus scripting language.

# **Contents**
- [Description](#description)
- [How to install](#how-to-install)
- [Core features](#core-features)
- [Modules](#modules)
- [Changelog](#changelog)
- [License](#license)

## **Description**
SublimePapyrus is a package that aims to provide a development environment for a scripting language called [Papyrus](http://www.creationkit.com/Category:Papyrus) within [Sublime Text](https://www.sublimetext.com/). The package is split into a core package and additional packages for specific games and/or resources. The core package is always required, but the other packages usually depend upon the core package or one of the other packages.

## **How to install**
- Download a [release](https://github.com/Kapiainen/SublimePapyrus/releases).
- Start Sublime Text.
- Click on the *Browse Packages...* option in the *Preferences* section of Sublime Text's toolbar.
- The *\Data\Packages* folder should now be open. Browse to *\Data\Installed Packages*.
- Open the release archive that was downloaded and extract the *.sublime-package* files to *\Data\Installed Packages*.
- Restart Sublime Text.

## **Core features**
- Build system framework
 - Single file build
 - Batch build
 - Hide successful build results
 - Highlight build errors
- Valid key insertion framework
- Commands
 - Open script
 - Clear error highlights
- Settings

#### Build system framework
The core of this package contains a flexible build system framework that should be able to handle most situations. The build system supports both single file and batch building, multiple import folders, and additional arguments. Lines in the source code that cause build errors can also be highlighted and brought to the center of the screen. Attempts to batch build one of the folders defined in the import folders setting will show a warning prompt.

#### Valid key insertion framework
Certain functions have a limited pool of valid values that can be used as the argument and some functions return specific values based on e.g. the object that the function was called on. ***Insert **** commands open a panel that lists either the description and the value, or just the value that will be inserted when chosen.

#### Commands
- Open script
  - This command brings up an input panel and uses the input string to find matching files in the import folders that have been defined in the settings. The syntax highlighting that is active is used to figure out which module's import folders setting to use.

- Clear error highlights
  - This command just clears all error highlights (build errors, linter errors, etc.) that have been applied by this package.

#### Settings
Settings are located in *Preferences* > *Package Settings* > *SublimePapyrus*.

- All modules
  - ***linter_on_save***: Run the linter whenever a script is saved. Default: True

  - ***linter_on_modified***: Run the linter whenever a script is modified. Default: True

  - ***linter_delay***: The delay in milliseconds between the last modification of a script and the linter being triggered. Default: 500

  - ***linter_panel_error_messages***: Another method of showing error messages in addition to the messages that are shown in the status bar that is located at the bottom of Sublime Text's windows. If one wishes to see error messages in Sublime Text 2, then it is recommended that one enables this setting as messages regarding a script being saved override the linter's error messages. Default: False

  - ***intelligent_code_completion***: Enables the code completion system that uses cached results from the linter to provide context-aware completions. Default: True

  - ***center_highlighted_line***: Automatically scrolls the view so that a highlighted line is in the center of the view. Default: True

  - ***highlight_build_errors***: Highlights lines that cause attempts to compile scripts to fail. Default: True

  - ***hide_successful_build_results***: Hides the panel that shows build results, if there were no issues during compilation. Default: False

  - ***batch_compilation_warning***: Shows a warning in the scenario where batch building would involve compiling scripts in one of the folders that have been defined in the relevant module's import folders setting. Default: True

- Build settings specific to each module
  - ***compiler***: The path to the compiler executable.

  - ***flags***: The name of the file containing information about flags (e.g. *"TESV_Papyrus_Flags.flg"* for Skyrim). A file by this name is expected to exist in at least one of the import folders.

  - ***output***: The path where compiled scripts should end up.

  - ***import***: A list of paths to folders containing script sources. Earlier entries override later entries. If one wanted to override Skyrim's script sources with script sources from Skyrim Script Extender (SKSE), then the path to SKSE's script sources should have a lower index than the path to Skyrim's script sources.

  - ***arguments***: A list of strings that are added at the end when invoking the compiler. Can be used to include additional options when invoking the compiler.

## **Modules**
- [The Elder Scrolls V: Skyrim](#the-elder-scrolls-v-skyrim)
 - [Skyrim Script Extender](#skyrim-script-extender-skse)
 - [Immersive First Person View](#immersive-first-person-view-ifpv)

### **The Elder Scrolls V: Skyrim**
- Syntax highlighting
- Linter
- Intelligent code completion
- Build system
- Commands
 - Generate completions
 - Valid key insertion
    - Actor value
    - Form type
    - Tracked statistic
    - Animation variables
    - Game settings

#### Syntax highlighting
Syntax highlighting for the version of Papyrus that is used in ***The Elder Scrolls V: Skyrim***.

#### Linter
The linter performs lexical, syntactic, and semantic analysis on the source code of scripts as they are being edited. Lines that cause errors are highlighted and the error messages are shown as status messages (bottom left corner of Sublime Text).

Caching is used by the linter in order to improve performance and cache invalidation only exists for a few scenarios. Modifications to the import folders setting (e.g. changing the order of paths) requires a restart of Sublime Text in order to clear the cache and ensure that the right scripts are being used.

The linter does work in Sublime Text 2, but error messages and highlighting is not possible due to technical limitations, which do not apply to Sublime Text 3, regarding the API in Sublime Text 2 when the linter is triggered by editing a script. Error messages and highlighting is possible in Sublime Text 2 when the linter is triggered by saving a script.

Information about settings relevant to the linter can be found **[here](#settings)**.

#### Intelligent code completion
The intelligent code completion system utilizes the linter to produce suggestions in a context-aware manner. This system can:
- Return completions for all functions, events, properties, and variables (including function/event parameters) that exist within the scope of the line that is being edited. This includes functions, events, and properties that have been inherited from a parent script, if a parent script has been defined.

- Determine if a completion for a function/event should be in the form of a function/event definition or a function/event call.

- Return completions for all scripts that exist within the import folders that have been defined in the package settings.

- Return keyword completions are also returned on the basis of the context of the line that is being edited.

- Provide information about the object behind the completion (e.g. a function's return type, a variable's type, whether a variable is a function/event parameter).

Caching is used by the intelligent code completion system in order to improve performance. Saving a script invalidates the portions of the cache that would be affected by modifications to that script.

There is a [setting](#settings) to turn this feature off. If this feature is disabled, then one can generate completions with the ***Generate completions*** command, but these completions will show up as suggested completions regardless of the context.

#### Build system
Single file build system and a batch build variant.

#### Commands
- Generate completions
  - This command uses the linter to generate completions for functions, events, and script names. A panel with all the import folders is shown so that one can choose which set of script sources to process. If there are a lot of script sources in a particular folder, then it can take a while to finish processing.

- Valid key insertion
  - Information about this command can be found **[here](#valid-key-insertion-framework)**.
    - Actor values names
    - Form type IDs
    - Tracked statistic names
    - Animation variable names (boolean, float, and integer)
    - Game setting names (float, integer, and string)

#### **3rd party resources for Skyrim**
##### Skyrim Script Extender (SKSE)
- Commands
 - Valid key insertion

###### Commands
- Valid key insertion
  - Information about this command can be found **[here](#valid-key-insertion-framework)**.
    - Menu names
    - Input keycodes
    - Control names
    - DefaultObject names
    - ActorValueInfo names and IDs
    - Actor action IDs
    - Player camera state IDs

##### Immersive First Person View (IFPV)
- Commands
 - Valid key insertion

###### Commands
- Valid key insertion
  - Information about this command can be found **[here](#valid-key-insertion-framework)**.
    - Config value names (boolean, float, integer, and string)
    - SKSE mod event names

## **Changelog**
Version 1.0.0 - 2016/03/04:
  - Major rewrite
  - Introduction of version numbers

## **License**

See [**LICENSE.md**](LICENSE.md) for more information.
