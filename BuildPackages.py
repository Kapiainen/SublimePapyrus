# Developed on Python 3.2.5
# This program goes through the repository looking for files in specific places, adds the files to lists, and then generates .sublime-package files.
import os, io, zipfile, time

packagename = "SublimePapyrus"
packageextension = ".sublime-package"
packagedirectory = "Packages"
corefiles = [] # Contains all the files in SublimePapyrus.sublime-package.
corelibraries = ["skyrim"] # The libraries to include in the core package.
libraries = {} # Contains lists of files for each library. Produces SublimePapyrus - Key.sublime-package files.
currentdirectory = os.getcwd()
for entry in os.listdir(currentdirectory):
	if entry.lower().startswith("."):
			continue
	if not os.path.isfile(entry):
		if entry.lower() == "core":
			coredirectory = os.path.join(currentdirectory, entry)
			for corefile in os.listdir(coredirectory):
				corefiles.append(os.path.join(coredirectory, corefile))
		elif entry.lower() == "libraries":
			librariesdirectory = os.path.join(currentdirectory, entry)
			for library in os.listdir(librariesdirectory):
				librarydirectory = os.path.join(librariesdirectory, library)
				if library.lower() in corelibraries:
					for libraryfile in os.listdir(librarydirectory):
						corefiles.append(os.path.join(librarydirectory, libraryfile))
				else:
					libraryfiles = []
					for libraryfile in os.listdir(librarydirectory):
						libraryfiles.append(os.path.join(librarydirectory, libraryfile))
					libraries[library] = libraryfiles
outputdirectory = os.path.join(currentdirectory, packagedirectory)
if not os.path.exists(outputdirectory):
		os.mkdir(outputdirectory)
print("Core files:")
corepackage = packagename + packageextension
with zipfile.ZipFile(os.path.join(outputdirectory, corepackage), "w") as corezip:
	for corefile in corefiles:
		print(corefile)
		corezip.write(corefile, os.path.relpath(corefile, os.path.split(corefile)[0]))
for library in libraries.keys():
	print("\n" + library + " files:")
	librarypackage = packagename + " - " + library + packageextension
	with zipfile.ZipFile(os.path.join(outputdirectory, librarypackage), "w") as libraryzip:
		for libraryfile in libraries[library]:
			print(libraryfile)
			libraryzip.write(libraryfile, os.path.relpath(libraryfile, os.path.split(libraryfile)[0]))
print("\nDone!")
#time.sleep(2.0)