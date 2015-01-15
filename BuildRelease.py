# Developed on Python 3.2.5
# This program goes looking for .sublime-package files and, if it can find any, will put those files, and other files (like documentation), into a .zip file that is ready for distribution.
import os, io, zipfile, time

packagename = "SublimePapyrus"
packageextension = ".sublime-package"
packagedirectory = "Packages"
releasedirectory = "Release"
releasefiles = [] # Contains all the files in the final .zip file.
currentdirectory = os.getcwd()
inputdirectory = os.path.join(currentdirectory, packagedirectory)
if os.path.exists(inputdirectory):
	for entry in os.listdir(inputdirectory):
		if packageextension in entry.lower():
			releasefiles.append(os.path.join(inputdirectory, entry))
	if len(releasefiles) > 0:
		for entry in os.listdir(currentdirectory):
			if os.path.isfile(entry):
				if entry.lower().startswith(".") or entry.endswith(".stackdump"):
					continue
				if entry.lower() == "readme.md":
					releasefiles.append(os.path.join(currentdirectory, entry))
		outputdirectory = os.path.join(currentdirectory, releasedirectory)
		if not os.path.exists(outputdirectory):
			os.mkdir(outputdirectory)
		print("Release files:")
		releasepackage = packagename + " - " + time.strftime("%Y-%m-%d %H-%M-%S", time.gmtime()) + ".zip"
		with zipfile.ZipFile(os.path.join(outputdirectory, releasepackage), "w") as releasezip:
			for releasefile in releasefiles:
				print(releasefile)
				releasezip.write(releasefile, os.path.relpath(releasefile, os.path.split(releasefile)[0]))
		print("\nDone!")
	else:
		print("No .sublime-package files in \"%s\"!" % inputdirectory)
else:
	print("\"%s\" does not exist!" % inputdirectory)
time.sleep(2.0)