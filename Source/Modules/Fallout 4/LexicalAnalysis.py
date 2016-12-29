"""
This module handles the lexical analysis of source code written in the version of Papyrus that ships with Fallout 4.
"""
import re

# It is faster to store the type as an attribute in the Token object than it is to have multiple token classes and use the isinstance() function.
class TokenEnum(object):
	"""Types of tokens."""
	COLON = 0
	COMMA = 1
	COMMENTBLOCK = 2
	COMMENTLINE = 3
	DOCSTRING = 4
	FLOAT = 5
	IDENTIFIER = 6
	INT = 7
	KEYWORD = 8
	LEFTBRACKET = 9
	LEFTPARENTHESIS = 10
	MULTILINE = 11
	NEWLINE = 12
	RIGHTBRACKET = 13
	RIGHTPARENTHESIS = 14
	STRING = 15
	UNMATCHED = 16
	WHITESPACE = 17
	# Operators
	ADDITION = 18
	AND = 19
	ASSIGN = 20
	ASSIGNADDITION = 21
	ASSIGNDIVISION = 22
	ASSIGNMODULUS = 23
	ASSIGNMULTIPLICATION = 24
	ASSIGNSUBTRACTION = 25
	DIVISION = 26
	DOT = 27
	EQUAL = 28
	GREATERTHAN = 29
	GREATERTHANOREQUAL = 30
	LESSTHAN = 31
	LESSTHANOREQUAL = 32
	MODULUS = 33
	MULTIPLICATION = 34
	NOT = 35
	NOTEQUAL = 36
	OR = 37
	SUBTRACTION = 38
	# Keywords
	kAS = 39
	kAUTO = 40
	kAUTOREADONLY = 41
	kBETAONLY = 42
	kBOOL = 43
	kCOLLAPSED = 44
	kCOLLAPSEDONBASE = 45
	kCOLLAPSEDONREF = 46
	kCONDITIONAL = 47
	kCONST = 48
	kCUSTOMEVENT = 49
	kDEBUGONLY = 50
	kDEFAULT = 51
	kELSE = 52
	kELSEIF = 53
	kENDEVENT = 54
	kENDFUNCTION = 55
	kENDGROUP = 56
	kENDIF = 57
	kENDPROPERTY = 58
	kENDSTATE = 59
	kENDSTRUCT = 60
	kENDWHILE = 61
	kEVENT = 62
	kEXTENDS = 63
	kFALSE = 64
	kFLOAT = 65
	kFUNCTION = 66
	kGLOBAL = 67
	kGROUP = 68
	kHIDDEN = 69
	kIF = 70
	kIMPORT = 71
	kINT = 72
	kIS = 73
	kLENGTH = 74
	kMANDATORY = 75
	kNATIVE = 76
	kNEW = 77
	kNONE = 78
	kPARENT = 79
	kPROPERTY = 80
	kRETURN = 81
	kSCRIPTNAME = 82
	kSELF = 83
	kSTATE = 84
	kSTRING = 85
	kSTRUCT = 86
	kTRUE = 87
	kVAR = 88
	kWHILE = 89
	#Caprica extensions
	kBREAK = 90
	kCASE = 91
	kCONTINUE = 92
	kDO = 93
	kENDFOR = 94
	kENDFOREACH = 95
	kENDSWITCH = 96
	kFOR = 97
	kFOREACH = 98
	kLOOPWHILE = 99
	kSWITCH = 100
	kTO = 101
	kIN = 102
	kSTEP = 103

TokenDescription = [
	"COLON",
	"COMMA",
	"COMMENTBLOCK",
	"COMMENTLINE",
	"DOCSTRING",
	"FLOAT",
	"IDENTIFIER",
	"INT",
	"KEYWORD",
	"LEFTBRACKET",
	"LEFTPARENTHESIS",
	"MULTILINE",
	"NEWLINE",
	"RIGHTBRACKET",
	"RIGHTPARENTHESIS",
	"STRING",
	"UNMATCHED",
	"WHITESPACE",
	"ADDITION",
	"AND",
	"ASSIGN",
	"ASSIGNADDITION",
	"ASSIGNDIVISION",
	"ASSIGNMODULUS",
	"ASSIGNMULTIPLICATION",
	"ASSIGNSUBTRACTION",
	"DIVISION",
	"DOT",
	"EQUAL",
	"GREATERTHAN",
	"GREATERTHANOREQUAL",
	"LESSTHAN",
	"LESSTHANOREQUAL",
	"MODULUS",
	"MULTIPLICATION",
	"NOT",
	"NOTEQUAL",
	"OR",
	"SUBTRACTION",
	"kAS",
	"kAUTO",
	"kAUTOREADONLY",
	"kBETAONLY",
	"kBOOL",
	"kCOLLAPSED",
	"kCOLLAPSEDONBASE",
	"kCOLLAPSEDONREF",
	"kCONDITIONAL",
	"kCONST",
	"kCUSTOMEVENT",
	"kDEBUGONLY",
	"kDEFAULT",
	"kELSE",
	"kELSEIF",
	"kENDEVENT",
	"kENDFUNCTION",
	"kENDGROUP",
	"kENDIF",
	"kENDPROPERTY",
	"kENDSTATE",
	"kENDSTRUCT",
	"kENDWHILE",
	"kEVENT",
	"kEXTENDS",
	"kFALSE",
	"kFLOAT",
	"kFUNCTION",
	"kGLOBAL",
	"kGROUP",
	"kHIDDEN",
	"kIF",
	"kIMPORT",
	"kINT",
	"kIS",
	"kLENGTH",
	"kMANDATORY",
	"kNATIVE",
	"kNEW",
	"kNONE",
	"kPARENT",
	"kPROPERTY",
	"kRETURN",
	"kSCRIPTNAME",
	"kSELF",
	"kSTATE",
	"kSTRING",
	"kSTRUCT",
	"kTRUE",
	"kVAR",
	"kWHILE",
	#Caprica extensions
	"kBREAK",
	"kCASE",
	"kCONTINUE",
	"kDO",
	"kENDFOR",
	"kENDFOREACH",
	"kENDSWITCH",
	"kFOR",
	"kFOREACH",
	"kLOOPWHILE",
	"kSWITCH",
	"kTO",
	"kIN",
	"kSTEP"
]

class Token(object):
	"""Token objects."""
	__slots__ = ["type", "line", "column", "value"]
	def __init__(self, aType, aValue, aLine, aColumn):
	# aType: TokenEnum
	# aValue: string
	# aLine: int
	# aColumn: int
		self.type = aType
		self.line = aLine
		self.column = aColumn
		self.value = aValue

	def __str__(self):
		return """
===== Token =====
Type: %s
Value: '%s'
Line: %d
Column: %d
""" % (
		TokenDescription[self.type],
		self.value,
		self.line,
		self.column
	)

class LexicalError(Exception):
	"""Lexical error."""
	def __init__(self, aMessage, aLine, aColumn):
	# aMessage: string
	# aLine: int
	# aColumn: int
		self.message = aMessage
		self.line = aLine
		self.column = aColumn

# Using regex is faster than e.g. grouping characters by splitting an input string.
class Lexical(object):
	"""Lexical analysis."""
	__slots__ = [
		"tokenRegex", # regex pattern
		"keywordRegex", # regex pattern
		"capricaExtensions" # bool
	]

	def __init__(self):
		tokenSpecifications = [
			(TokenEnum.COMMENTBLOCK, r";/[\S\s]*?(?=/;)/;"),
			(TokenEnum.COMMENTLINE, r";[^\n]*"),
			(TokenEnum.DOCSTRING, r"{[\S\s]*?(?=})}"),
			(TokenEnum.LEFTPARENTHESIS, r"\("),
			(TokenEnum.RIGHTPARENTHESIS, r"\)"),
			(TokenEnum.LEFTBRACKET, r"\["),
			(TokenEnum.RIGHTBRACKET, r"\]"),
			(TokenEnum.MULTILINE, r"\\[^\n]*?(?=\n)\n"),
			(TokenEnum.COMMA, r","),
			(TokenEnum.DOT, r"\."),
			(TokenEnum.EQUAL, r"=="),
			(TokenEnum.NOTEQUAL, r"!="),
			(TokenEnum.GREATERTHANOREQUAL, r">="),
			(TokenEnum.LESSTHANOREQUAL, r"<="),
			(TokenEnum.GREATERTHAN, r">"),
			(TokenEnum.LESSTHAN, r"<"),
			(TokenEnum.NOT, r"!"),
			(TokenEnum.AND, r"&&"),
			(TokenEnum.OR, r"\|\|"),
			(TokenEnum.ASSIGNADDITION, r"\+="),
			(TokenEnum.ASSIGNSUBTRACTION, r"-="),
			(TokenEnum.ASSIGNMULTIPLICATION, r"\*="),
			(TokenEnum.ASSIGNDIVISION, r"/="),
			(TokenEnum.ASSIGNMODULUS, r"%="),
			(TokenEnum.ASSIGN, r"="),
			(TokenEnum.IDENTIFIER, r"[a-z_][0-9a-z_]*"),
			(TokenEnum.FLOAT, r"(\d+\.\d+)"),
			(TokenEnum.INT, r"((0x(\d|[a-f])+)|((\d+))(?![a-z_]))"),
			(TokenEnum.ADDITION, r"\+"),
			(TokenEnum.SUBTRACTION, r"-"),
			(TokenEnum.MULTIPLICATION, r"\*"),
			(TokenEnum.DIVISION, r"/"),
			(TokenEnum.MODULUS, r"%"),
			(TokenEnum.STRING, r"\".*?(?:(?<=\\\\)\"|(?<!\\)\")"),
			(TokenEnum.COLON, r"\:"),
			(TokenEnum.NEWLINE, r"[\n\r]"),
			(TokenEnum.WHITESPACE, r"[ \t]"),
			(TokenEnum.UNMATCHED, r"."),
		]
		self.tokenRegex = re.compile("|".join("(?P<t%s>%s)" % pair for pair in tokenSpecifications), re.IGNORECASE) # Papyrus is case-insensitive.
		self.capricaExtensions = True
		self.Reset(False)

	def Reset(self, aCaprica):
		assert isinstance(aCaprica, bool) #Prune
		# aCaprica: bool
		if aCaprica != self.capricaExtensions:
			self.capricaExtensions = aCaprica
			keywordSpecifications = [
				(TokenEnum.kAS, r"\bas\b"),
				(TokenEnum.kAUTO, r"\bauto\b"),
				(TokenEnum.kAUTOREADONLY, r"\bautoreadonly\b"),
				(TokenEnum.kBETAONLY, r"\bbetaonly\b"),
				(TokenEnum.kBOOL, r"\bbool\b"),
				(TokenEnum.kCOLLAPSED, r"\bcollapsed\b"),
				(TokenEnum.kCOLLAPSEDONBASE, r"\bcollapsedonbase\b"),
				(TokenEnum.kCOLLAPSEDONREF, r"\bcollapsedonref\b"),
				(TokenEnum.kCONDITIONAL, r"\bconditional\b"),
				(TokenEnum.kCONST, r"\bconst\b"),
				(TokenEnum.kCUSTOMEVENT, r"\bcustomevent\b"),
				(TokenEnum.kDEBUGONLY, r"\bdebugonly\b"),
				(TokenEnum.kDEFAULT, r"\bdefault\b"),
				(TokenEnum.kELSE, r"\belse\b"),
				(TokenEnum.kELSEIF, r"\belseif\b"),
				(TokenEnum.kENDEVENT, r"\bendevent\b"),
				(TokenEnum.kENDFUNCTION, r"\bendfunction\b"),
				(TokenEnum.kENDGROUP, r"\bendgroup\b"),
				(TokenEnum.kENDIF, r"\bendif\b"),
				(TokenEnum.kENDPROPERTY, r"\bendproperty\b"),
				(TokenEnum.kENDSTATE, r"\bendstate\b"),
				(TokenEnum.kENDSTRUCT, r"\bendstruct\b"),
				(TokenEnum.kENDWHILE, r"\bendwhile\b"),
				(TokenEnum.kEVENT, r"\bevent\b"),
				(TokenEnum.kEXTENDS, r"\bextends\b"),
				(TokenEnum.kFALSE, r"\bfalse\b"),
				(TokenEnum.kFLOAT, r"\bfloat\b"),
				(TokenEnum.kFUNCTION, r"\bfunction\b"),
				(TokenEnum.kGLOBAL, r"\bglobal\b"),
				(TokenEnum.kGROUP, r"\bgroup\b"),
				(TokenEnum.kHIDDEN, r"\bhidden\b"),
				(TokenEnum.kIF, r"\bif\b"),
				(TokenEnum.kIMPORT, r"\bimport\b"),
				(TokenEnum.kINT, r"\bint\b"),
				(TokenEnum.kIS, r"\bis\b"),
				(TokenEnum.kLENGTH, r"\blength\b"),
				(TokenEnum.kMANDATORY, r"\bmandatory\b"),
				(TokenEnum.kNATIVE, r"\bnative\b"),
				(TokenEnum.kNEW, r"\bnew\b"),
				(TokenEnum.kNONE, r"\bnone\b"),
				(TokenEnum.kPARENT, r"\bparent\b"),
				(TokenEnum.kPROPERTY, r"\bproperty\b"),
				(TokenEnum.kRETURN, r"\breturn\b"),
				(TokenEnum.kSCRIPTNAME, r"\bscriptname\b"),
				(TokenEnum.kSELF, r"\bself\b"),
				(TokenEnum.kSTATE, r"\bstate\b"),
				(TokenEnum.kSTRING, r"\bstring\b"),
				(TokenEnum.kSTRUCT, r"\bstruct\b"),
				(TokenEnum.kTRUE, r"\btrue\b"),
				(TokenEnum.kVAR, r"\bvar\b"),
				(TokenEnum.kWHILE, r"\bwhile\b"),
			]
			#Caprica extensions
			if self.capricaExtensions:
				keywordSpecifications.extend(
					[
						(TokenEnum.kBREAK, r"\bbreak\b"),
						(TokenEnum.kCASE, r"\bcase\b"),
						(TokenEnum.kCONTINUE, r"\bcontinue\b"),
						(TokenEnum.kDO, r"\bdo\b"),
						(TokenEnum.kENDFOR, r"\bendfor\b"),
						(TokenEnum.kENDFOREACH, r"\bendforeach\b"),
						(TokenEnum.kENDSWITCH, r"\bendswitch\b"),
						(TokenEnum.kFOR, r"\bfor\b"),
						(TokenEnum.kFOREACH, r"\bforeach\b"),
						(TokenEnum.kLOOPWHILE, r"\bloopwhile\b"),
						(TokenEnum.kSWITCH, r"\bswitch\b"),
						(TokenEnum.kTO, r"\bto\b"),
						(TokenEnum.kIN, r"\bin\b"),
						(TokenEnum.kSTEP, r"\bstep\b"),
					]
				)
			self.keywordRegex = re.compile("|".join("(?P<t%s>%s)" % pair for pair in keywordSpecifications), re.IGNORECASE) # Papyrus is case-insensitive.

	def Process(self, aString):
		"""Generates tokens from a string."""
		assert isinstance(aString, str) #Prune
	# aString: string (contains source code to tokenize)
		line = 1
		column = -1
		for match in self.tokenRegex.finditer(aString):
			t = match.lastgroup
			v = match.group(t)
			t = int(match.lastgroup[1:])
			if t == TokenEnum.WHITESPACE:
				continue
			elif t == TokenEnum.IDENTIFIER:
				keyword = self.keywordRegex.match(v)
				if keyword:
					t = int(keyword.lastgroup[1:])
				yield Token(t, v, line, match.start()-column)
				continue
			elif t == TokenEnum.COMMENTLINE:
				yield Token(TokenEnum.COMMENTLINE, None, line, match.start()-column)
				continue
			elif t == TokenEnum.COMMENTBLOCK:
				i = v.count("\n")
				if i > 0:
					line += i
					column = match.end()-1
				yield Token(TokenEnum.COMMENTBLOCK, None, line, match.start()-column)
				continue
			elif t == TokenEnum.MULTILINE:
				line += 1
				column = match.end()-1
				continue
			elif t == TokenEnum.DOCSTRING or t == TokenEnum.STRING:
				if t == TokenEnum.DOCSTRING:
					v = v[1:-1]
				yield Token(t, v, line, match.start()-column)
				i = v.count("\n")
				if i > 0:
					line += i
					column = match.end()-1
				continue
			elif t == TokenEnum.UNMATCHED:
				raise LexicalError("Encountered an unexpected character ('%s')." % v, line, match.start()-column)
			yield Token(t, v, line, match.start()-column)
			if t == TokenEnum.NEWLINE:
				line += 1
				column = match.end()-1
		yield Token(TokenEnum.NEWLINE, "\n", line, 1)
