"""
Comments on documentation found in linter files

# ImplementationKeyword: <word>
	This kind of comment can be found on the line that starts a scope that
	pertains to the implementation of some object in or aspect of the Papyrus
	language.

# Implements: <description>
	This kind of comment can be found near a line that starts a scope that
	implements the rule or function described by the comment (e.g. no duplicate
	definitions are allowed).

"""

import re, os, sys
PLATFORM_WINDOWS = os.name == "nt"
PYTHON_VERSION = sys.version_info
if PYTHON_VERSION[0] == 2:
	import imp
	root, module = os.path.split(os.getcwd())

	lexicalModule = os.path.join(root, module, "LexicalAnalysis.py")
	imp.load_source("LexicalAnalysis", lexicalModule)

	syntacticModule = os.path.join(root, module, "SyntacticAnalysis.py")
	imp.load_source("SyntacticAnalysis", syntacticModule)
	
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

PAPYRUS_EXTENSION = ".PSC" # Used when generating or discovering paths to script files.
INITIALIZED = False
IMPORT_PATHS = None # List of str
LINTER_CACHE = {} # This dict is used to cache ScriptObject instances and the key is a str that represents the scriptname identifier in the upper case (i.e. str(script.identifier).upper())
COMPLETION_CACHE = {} # This dict is used to cache completions TODO: Implement completion generation and caching
LEX = None # Instance of LexicalAnalysis.Lexical
SYN = None # Instance of SyntacticAnalysis.Syntactic
SEMP1 = None # Instance of SemanticAnalysis.SemanticFirstPhase
SEMP2 = None # Instance of SemanticAnalysis.SemanticSecondPhase

def ClearCache(a_key = None):
# a_key: str
	global LINTER_CACHE
	global COMPLETION_CACHE
	if a_key:
		if LINTER_CACHE.get(a_key, None):
			del LINTER_CACHE[a_key]
		if COMPLETION_CACHE.get(a_key, None):
			del COMPLETION_CACHE[a_key]
	else:
		LINTER_CACHE = {}
		COMPLETION_CACHE = {}

def Initialize():
	global LEX
	global SYN
	global SEMP1
	global SEMP2
	LEX = Lexical()
	SYN = Syntactic()
	SEMP1 = SemanticFirstPhase()
	SEMP2 = SemanticSecondPhase()

def GetPath(a_identifier):
	global IMPORT_PATHS
	file_path = None
	dir_path = None
	if PLATFORM_WINDOWS:
		dir_list = a_identifier.namespace[:]
		dir_list.append(a_identifier.name)
		file_list = a_identifier.namespace[:]
		file_list.append("%s.psc" % a_identifier.name)
		for import_path in IMPORT_PATHS:
			if file_path and dir_path:
				break
			if not dir_path:
				temp_dir_path = os.path.join(import_path, *dir_list)
				if os.path.isdir(temp_dir_path):
					dir_path = temp_dir_path
			if not file_path:
				temp_file_path = os.path.join(import_path, *file_list)
				if os.path.isfile(temp_file_path):
					file_path = temp_file_path
		pass #TODO: Implement the same as below, but in a manner that is faster on case-insensitive filesystems
	else:
		namespace_original = [e.upper() for e in a_identifier.namespace]
		name = a_identifier.name.upper()
		file_name = name + PAPYRUS_EXTENSION
		for import_path in IMPORT_PATHS:
			if file_path and dir_path:
				break
			namespace = namespace_original[:]
			path = import_path
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
				entry_upper = entry.upper()
				if not file_path and file_name == entry_upper:
					temp = os.path.join(path, entry)
					if os.path.isfile(temp):
						file_path = temp
				if not dir_path and name == entry_upper:
					temp = os.path.join(path, entry)
					if os.path.isdir(temp):
						dir_path = temp
	return file_path, dir_path

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

def GetScriptName(aSource):
	global LEX
	global SYN
	global SEMP1
	global INITIALIZED
	if not INITIALIZED:
		Initialize()
	tokens = []
	for token in LEX.Process(aSource):
		tokenType = token.type
		if tokenType == TokenEnum.NEWLINE:
			if tokens:
				statement = SYN.Process(tokens)
				if statement:
					if isinstance(statement, SyntacticAnalysis.ScriptSignatureStatement):
						scriptName = statement.identifier.namespace
						scriptName.append(statement.identifier.name)
						return scriptName
				tokens = []
		elif tokenType != TokenEnum.COMMENTLINE and tokenType != TokenEnum.COMMENTBLOCK:
			tokens.append(token)
	return None

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