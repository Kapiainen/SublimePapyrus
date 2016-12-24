import os

# PLATFORM_WINDOWS is used to determine how to look for scripts in the filesystem. Unix-based OSes often have case-sensitive filesystems.
PLATFORM_WINDOWS = os.name == "nt"

class FunctionObject(object):
	__slots__ = [
		"identifier",
		"type",
		"parameters",
		"flags",
		"line"
	]

	def __init__(self):
		pass