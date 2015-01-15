# Developed on Python 3.2.5
import os, io, zipfile, time

packagename = "SublimePapyrus"
packageextension = ".sublime-package"
releasefiles = [] # Contains all the files in the final .zip file.

currentdirectory = os.getcwd()
for entry in os.listdir(currentdirectory):
	if os.path.isfile(entry):
		if entry.lower().startswith(".") or entry.endswith(".stackdump"):
			continue
		if entry.lower() == "readme.md":
			releasefiles.append(os.path.join(currentdirectory, entry))
		elif packageextension in entry.lower():
			releasefiles.append(os.path.join(currentdirectory, entry))

print("Release files:")
releasepackage = packagename + " - " + time.strftime("%Y-%m-%d %H-%M-%S", time.gmtime()) + ".zip"
with zipfile.ZipFile(os.path.join(currentdirectory, releasepackage), "w") as releasezip:
	for releasefile in releasefiles:
		print(releasefile)
		releasezip.write(releasefile, os.path.relpath(releasefile, os.path.split(releasefile)[0]))

print("\nDone!")
time.sleep(2.0)