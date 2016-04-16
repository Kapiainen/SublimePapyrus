# Developed for Python 3.x
import os, zipfile, sys

ROOT = ""
if len(sys.argv) > 1:
	ROOT = sys.argv[1]
else:
	ROOT = os.getcwd()

PACKGE_PREFIX = "SublimePapyrus"
PACKAGE_EXTENSION = ".sublime-package"

def main():
	global ROOT
	licenseFile = os.path.join(ROOT, "LICENSE.md")
	if not os.path.isfile(licenseFile):
		print("Could not find 'LICENSE.md' in '%s'." % ROOT)
		return
	licenseRelPath = os.path.relpath(licenseFile, os.path.split(licenseFile)[0])
	readmeFile = os.path.join(ROOT, "README.md")
	if not os.path.isfile(readmeFile):
		print("Could not find 'README.md' in '%s'." % ROOT)
		return
	readmeRelPath = os.path.relpath(readmeFile, os.path.split(readmeFile)[0])
	pkg = os.path.join(ROOT, "Packages")
	if not os.path.isdir(pkg):
		os.makedirs(pkg)
	src = os.path.join(ROOT, "Source")
	if not os.path.isdir(src):
		print("There is no 'Source' folder in '%s'." % ROOT)
		return
	core = os.path.join(src, "Core")
	if os.path.isdir(core):
		coreFiles = []
		for root, dirs, files in os.walk(core):
			for file in files:
				coreFiles.append(os.path.join(root, file))
		with zipfile.ZipFile(os.path.join(pkg, PACKGE_PREFIX+PACKAGE_EXTENSION), "w") as coreZip:
			coreZip.write(licenseFile, licenseRelPath)
			coreZip.write(readmeFile, readmeRelPath)
			for file in coreFiles:
				coreZip.write(file, os.path.relpath(file, os.path.split(file)[0]))
	else:
		print("There is no 'Core' folder in '%s'." % src)
		return
	modules = os.path.join(src, "Modules")
	if os.path.isdir(modules):
		for moduleName in os.listdir(modules):
			modulePath = os.path.join(modules, moduleName)
			if os.path.isdir(modulePath):
				moduleFiles = []
				for root, dirs, files in os.walk(modulePath):
					for file in files:
						moduleFiles.append(os.path.join(root, file))
				with zipfile.ZipFile(os.path.join(pkg, "%s - %s%s" % (PACKGE_PREFIX, moduleName, PACKAGE_EXTENSION)), "w") as moduleZip:
					moduleZip.write(licenseFile, licenseRelPath)
					moduleZip.write(readmeFile, readmeRelPath)
					for file in moduleFiles:
						moduleZip.write(file, os.path.relpath(file, os.path.split(file)[0]))
	print("Finished...")
main()