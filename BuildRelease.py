"""
Builds .sublime-package files from the contents of the "Source" folder.

Developed for Python 3.x
"""

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
	print("Input version number: ")
	release_version = input()
	print("Building a release archive...")
	global ROOT
	license_file = os.path.join(ROOT, "LICENSE.md")
	if not os.path.isfile(license_file):
		print("Could not find 'LICENSE.md' in '%s'." % ROOT)
		return
	license_relative_path = os.path.relpath(license_file, os.path.split(license_file)[0])
	readme_file = os.path.join(ROOT, "README.md")
	if not os.path.isfile(readme_file):
		print("Could not find 'README.md' in '%s'." % ROOT)
		return
	readme_relative_path = os.path.relpath(readme_file, os.path.split(readme_file)[0])
	rls = os.path.join(ROOT, "Releases")
	if not os.path.isdir(rls):
		os.makedirs(rls)
	pkg = os.path.join(ROOT, "Packages")
	if not os.path.isdir(pkg):
		print("Could not find 'Packages' folder in '%s'." % ROOT)
		return
	packages = [os.path.join(pkg, p) for p in os.listdir(pkg) if PACKAGE_EXTENSION in p]
	with zipfile.ZipFile(os.path.join(rls, "%s - %s%s" % (RELEASE_PREFIX, release_version, RELEASE_EXTENSION)), "w") as release_zip:
		release_zip.write(license_file, license_relative_path)
		release_zip.write(readme_file, readme_relative_path)
		for package in packages:
			release_zip.write(package, os.path.relpath(package, os.path.split(package)[0]))
	print("Finished...")
main()