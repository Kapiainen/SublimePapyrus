import re, os, sys
PLATFORM_WINDOWS = os.name == "nt"
PYTHON_VERSION = sys.version_info
if PYTHON_VERSION[0] == 2:
	import imp
	root, module = os.path.split(os.getcwd())

	lexicalModule = os.path.join(root, module, "LexicalAnalysis.py")
	imp.load_source("LexicalAnalysis", lexicalModule)

	syntacticModule = os.path.join(root, module, "SyntacticAnalysis.py")
	imp.load_source("SyntacticAnalysis", Module)
	
	semanticModule = os.path.join(root, module, "SemanticAnalysis.py")
	imp.load_source("SemanticAnalysis", semanticModule)

	from LexicalAnalysis import *
	from SyntacticAnalysis import *
	from SemanticAnalysis import *

	# Cleaning up
	del root
	del module
	del coreModule
	del lexicalModule
	del syntacticModule
	del semanticModule
elif PYTHON_VERSION[0] >= 3:
	from .LexicalAnalysis import *
	from .SyntacticAnalysis import *
	from .SemanticAnalysis import *

PAPYRUS_EXTENSION = ".PSC"
INITIALIZED = False
IMPORT_PATHS = None
LINTER_CACHE = {}
TYPE_MAPS = {}
LEX = None
SYN = None
SEMP1 = None
SEMP2 = None

#class TypeMap(object):
#	__slots__ = [
#		"identifier", # LexicalAnalysis.Identifier
#		"path" # string
#	]
#
#	def __init__(self, aIdentifier, aPath):
#		assert isinstance(aIdentifier, Identifier) #Prune
#		assert isinstance(aPath, str) #Prune
#		self.identifier = aIdentifier
#		self.path = aPath
#
#def ClearCache(aPath):
#	global LINTER_CACHE
#	LINTER_CACHE = {}
#	global TYPE_MAPS
#	TYPE_MAPS = {}
#
#def GetCachedScript(aIdentifier): # Pass this along to Semantic's constructor
#	"""Returns a Script object from the cache, and if necessary generates and caches the object."""
#	assert isinstance(aIdentifier, Identifier) #Prune
#	global LINTER_CACHE
#	key = None
#	if aIdentifier.namespace:
#		key = ":".join(aIdentifier.namespace[:].append(aIdentifier.name)).upper()
#	else:
#		key = aIdentifier.name.upper()
#	script = LINTER_CACHE.get(key, None)
#	if not script:
#		global TYPE_MAPS
#		typeMap = TYPE_MAPS.get(key, None)
#		if typeMap:
#			with open(typeMap.path, "r") as f:
#				source = f.read()
#				script = BuildScript(source)
#				if script:
#					LINTER_CACHE[] = script
#				else:
#					raise Exception("'%s' is not a valid script." % typeMap.path)
#		else:
#			raise Exception("Missing TypeMap for '%s'" % key)
#	return script
#
#def MapType(aType, aImportedScripts, aImportedNamespaces):
#	"""Returns a Type object.
#
#All types go through this function to get validated and cached as TypeMap instances for later use."""
#	assert isinstance(aType, Type) #Prune
#	assert isinstance(aImportedScripts, list) #Prune
#	assert isinstance(aImportedNamespaces, list) #Prune
#	global TYPE_MAPS
#	key = None
#	if aType.identifier.namespace:
#		key = ":".join(aType.identifier.namespace[:].append(aType.identifier.name)).upper()
#	else:
#		key = aType.identifier.name.upper()
#	typeMap = TYPE_MAPS.get(key, None)
#	if not typeMap:
#		# Figure out the actual type
#		#	Namespace
#		#	Name
#		#	Struct or not
#		ident = None
#		path = None
#		# Figure out the path to the script file
#		global IMPORT_PATHS
#		if PLATFORM_WINDOWS: # Case-insensitive filesystem
#			for importPath in IMPORT_PATHS:
#
#		else: # Unix -> Usually case-sensitive filesystems
#			pass
#		typeMap = TypeMap(ident, path)
#		TYPE_MAPS[key] = typeMap # key = type identifier used in the script, which may have imported scripts or namespaces
#		absoluteKey = None
#		if typeMap.identifier.namespace:
#			absoluteKey = ":".join(typeMap.identifier.namespace[:].append(typeMap.identifier.name)).upper()
#		else:
#			absoluteKey = typeMap.identifier.name.upper()
#		TYPE_MAPS[absoluteKey] = typeMap # absoluteKey = full type identifier, which is required when no scripts or namespaces have been imported
#	return

def GetPath(aIdentifier):
	global IMPORT_PATHS
	filePath = None
	dirPath = None
	if PLATFORM_WINDOWS:
		pass #TODO: Implement the same as below, but in a manner that is faster on case-insensitive filesystems
	else:
		namespaceOriginal = [e.upper() for e in aIdentifier.namespace]
		name = aIdentifier.name.upper()
		fileName = name + PAPYRUS_EXTENSION
		for importPath in IMPORT_PATHS:
			if filePath and dirPath:
				break
			namespace = namespaceOriginal[:]
			path = importPath
			while namespace:
				progressed = False
				for entry in os.listdir(path):
					if entry.upper() == namespace[0]:
						temp = os.path.join(path, entry)
						if os.path.isdir(temp):
							path = temp
							namespace.pop(0)
							progressed = True
							break
				if not progressed:
					break
			if namespace:
				continue
			for entry in os.listdir(path):
				entryUpper = entry.upper()
				if not filePath and fileName == entryUpper:
					temp = os.path.join(path, entry)
					if os.path.isfile(temp):
						filePath = temp
				if not dirPath and name == entryUpper:
					temp = os.path.join(path, entry)
					if os.path.isdir(temp):
						dirPath = temp
	return filePath, dirPath

def SourceReader(aPath):
	with open(aPath, "r") as f:
		return f.read()
	return None

def BuildScript(aSource):
	assert isinstance(aSource, str) #Prune
	global LEX
	global SYN
	global SEMP1
	tokens = []
	for token in LEX.Process(aSource):
		tokenType = token.type
		if tokenType == TokenEnum.NEWLINE:
			if tokens:
				statement = SYN.Process(tokens)
				if statement:
					SEMP1.Assemble(statement)
				tokens = []
		elif tokenType != TokenEnum.COMMENTLINE and tokenType != TokenEnum.COMMENTBLOCK:
			tokens.append(token)
	return SEMP1.Build(GetPath)

#def SortImport(aIdentifier, aScripts, aNamespaces):
#	global IMPORT_PATHS
#	isFile = False
#	isDir = False
#	if PLATFORM_WINDOWS:
#		pass #TODO: Implement the same as below, but in a manner that is faster on case-insensitive filesystems
#	else:
#		namespaceOriginal = [e.upper() for e in aIdentifier.namespace]
#		name = aIdentifier.name.upper()
#		fileName = name + PAPYRUS_EXTENSION
#		for importPath in IMPORT_PATHS:
#			if isFile and isDir:
#				break
#			namespace = namespaceOriginal[:]
#			path = importPath
#			while namespace:
#				progressed = False
#				for entry in os.listdir(path):
#					if entry.upper() == namespace[0]:
#						temp = os.path.join(path, entry)
#						if os.path.isdir(temp):
#							path = temp
#							namespace.pop(0)
#							progressed = True
#							break
#				if not progressed:
#					break
#			if namespace:
#				continue
#			for entry in os.listdir(path):
#				entryUpper = entry.upper()
#				if not isFile and fileName == entryUpper:
#					temp = os.path.join(path, entry)
#					if os.path.isfile(temp):
#						isFile = True
#				if not isDir and name == entryUpper:
#					temp = os.path.join(path, entry)
#					if os.path.isdir(temp):
#						isDir = True
#	key = str(aIdentifier).upper()
#	if isFile and isDir:
#		raise Exception("SublimePapyrus - Fallout 4 - Ambiguous import, could be both a script and a namespace.") #TODO: Handle this error
#	elif isFile:
#		if aScripts.get(key, None):
#			raise Exception("SublimePapyrus - Fallout 4 - Already imported this script.") #TODO: Handle this error
#		aScripts[key] = aIdentifier
#	elif isDir:
#		if aNamespaces.get(key, None):
#			raise Exception("SublimePapyrus - Fallout 4 - Already imported this namespace.") #TODO: Handle this error
#		aNamespaces[key] = aIdentifier
#	else:
#		raise Exception("SublimePapyrus - Fallout 4 - Unresolved import.") #TODO: Handle this error

def Initialize():
	global LEX
	global SYN
	global SEMP1
	global SEMP2
	LEX = Lexical()
	SYN = Syntactic()
	SEMP1 = SemanticFirstPhase()
	SEMP2 = SemanticSecondPhase()

def Process(aSource, aPaths, aCaprica):
	assert isinstance(aSource, str) #Prune
	assert isinstance(aPaths, list) #Prune
	assert isinstance(aCaprica, bool) #Prune
	global INITIALIZED
	if not INITIALIZED:
		Initialize()
	global IMPORT_PATHS
	IMPORT_PATHS = aPaths
	global LEX
	global SYN
	global SEMP1
	global SEMP2
	LEX.Reset(aCaprica)
	SYN.Reset(aCaprica)
	SEMP1.Reset(aCaprica)
	SEMP2.Reset(aCaprica)
	print("Linting with Caprica extensions:", aCaprica)
	script = BuildScript(aSource)
	global LINTER_CACHE
	LINTER_CACHE[str(script.identifier).upper()] = script
	SEMP1.Validate(script, LINTER_CACHE, GetPath, SourceReader, BuildScript)
	#SEMP2.Validate(script)
	return True