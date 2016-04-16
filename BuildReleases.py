# Developed for Python 3.x
import os, zipfile, sys, time

ROOT = ""
if len(sys.argv) > 1:
	ROOT = sys.argv[1]
else:
	ROOT = os.getcwd()

RELEASE_PREFIX = "SublimePapyrus"
RELEASE_EXTENSION = ".zip"
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
	rls = os.path.join(ROOT, "Releases")
	if not os.path.isdir(rls):
		os.makedirs(rls)
	pkg = os.path.join(ROOT, "Packages")
	if not os.path.isdir(pkg):
		print("Could not find 'Packages' folder in '%s'." % ROOT)
		return
	packages = [os.path.join(pkg, p) for p in os.listdir(pkg) if PACKAGE_EXTENSION in p]
	with zipfile.ZipFile(os.path.join(rls, "%s - %s%s" % (RELEASE_PREFIX, time.strftime("%Y-%m-%d %H-%M-%S", time.gmtime()), RELEASE_EXTENSION)), "w") as releaseZip:
		releaseZip.write(licenseFile, licenseRelPath)
		releaseZip.write(readmeFile, readmeRelPath)
		for package in packages:
			releaseZip.write(package, os.path.relpath(package, os.path.split(package)[0]))
	print("Finished...")
main()