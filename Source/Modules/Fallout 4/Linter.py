import re, os, sys
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

INITIALIZED = False
LEX = None
SYN = None
SEM = None

def ClearCache():
	pass

def Initialize():
	global LEX
	global SYN
	global SEM
	LEX = Lexical()
	SYN = Syntactic()
	SEM = Semantic()

def Process(aSource, aPaths):
	global INITIALIZED
	if not INITIALIZED:
		Initialize()
	global LEX
	global SYN
	global SEM
	LEX.Reset(True)
	SYN.Reset(True)
	SEM.Reset(True)
	tokens = []
	for token in LEX.Process(aSource):
		if token.type == TokenEnum.NEWLINE:
			if tokens:
				#stat = SYN.Process(tokens)
				#if stat:
				#	self.AssembleScript(stat)
				tokens = []
		elif token.type != TokenEnum.COMMENTLINE and token.type != TokenEnum.COMMENTBLOCK:
			tokens.append(token)
	return True