# Developed on Python 3.2.5
import os, io, zipfile, time

packagename = "SublimePapyrus"
packageextension = ".sublime-package"
releasefiles = [] # Contains all the files in the final .zip file.
corefiles = [] # Contains all the files in SublimePapyrus.sublime-package.
corelibraries = ["skyrim"] # The libraries to include in the core package.
libraries = {} # Contains lists of files for each library. Produces SublimePapyrus - Key.sublime-package files.

currentdirectory = os.getcwd()
for entry in os.listdir(currentdirectory):
	if not os.path.isfile(entry):
		if entry.lower().startswith(".") or entry.endswith(".stackdump"):
			continue
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
	else:
		if entry.lower() == "readme.md":
			releasefiles.append(os.path.join(currentdirectory, entry))

#print("\nCore files:")
corepackage = packagename + packageextension
with zipfile.ZipFile(os.path.join(currentdirectory, corepackage), "w") as corezip: 
	for corefile in corefiles:
		#print(corefile)
		corezip.write(corefile, os.path.relpath(corefile, os.path.split(corefile)[0]))
	releasefiles.append(os.path.join(currentdirectory, corepackage))

for library in libraries.keys():
	#print("\n" + library + " files:")
	librarypackage = packagename + " - " + library + packageextension
	with zipfile.ZipFile(os.path.join(currentdirectory, librarypackage), "w") as libraryzip:
		for libraryfile in libraries[library]:
			#print(libraryfile)
			libraryzip.write(libraryfile, os.path.relpath(libraryfile, os.path.split(libraryfile)[0]))
		releasefiles.append(os.path.join(currentdirectory, librarypackage))

#print("\nRelease files:")
releasepackage = packagename + " - " + time.strftime("%Y-%m-%d %H-%M-%S", time.gmtime()) + ".zip"
with zipfile.ZipFile(os.path.join(currentdirectory, releasepackage), "w") as releasezip:
	for releasefile in releasefiles:
		#print(releasefile)
		releasezip.write(releasefile, os.path.relpath(releasefile, os.path.split(releasefile)[0]))
		if releasefile.endswith(packageextension):
			os.remove(releasefile)

print("Done!")
time.sleep(2.0)