import re

#1: Lexical analysis
class TokenEnum(object):
	"""Types of tokens."""
	COMMA = 0
	COMMENTBLOCK = 1
	COMMENTLINE = 2
	DOCSTRING = 3
	FLOAT = 4
	IDENTIFIER = 5
	INT = 6
	KEYWORD = 7
	LEFTBRACKET = 8
	LEFTPARENTHESIS = 9
	MULTILINE = 10
	NEWLINE = 11
	RIGHTBRACKET = 12
	RIGHTPARENTHESIS = 13
	STRING = 14
	UNMATCHED = 15
	WHITESPACE = 16
	# Operators
	ADDITION = 17
	AND = 18
	ASSIGN = 19
	ASSIGNADDITION = 20
	ASSIGNDIVISION = 21
	ASSIGNMODULUS = 22
	ASSIGNMULTIPLICATION = 23
	ASSIGNSUBTRACTION = 24
	DIVISION = 25
	DOT = 26
	EQUAL = 27
	GREATERTHAN = 28
	GREATERTHANOREQUAL = 29
	LESSTHAN = 30
	LESSTHANOREQUAL = 31
	MODULUS = 32
	MULTIPLICATION = 33
	NOT = 34
	NOTEQUAL = 35
	OR = 36
	SUBTRACTION = 37
	COLON = 38

TokenDescription = [
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
	"COLON"
]


class KeywordEnum(object):
	"""Types of keywords."""
	AS = 0
	AUTO = 1
	AUTOREADONLY = 2
	BETAONLY = 3
	BOOL = 4
	COLLAPSED = 5
	COLLAPSEDONBASE = 6
	COLLAPSEDONREF = 7
	CONDITIONAL = 8
	CONST = 9
	CUSTOMEVENT = 10
	DEBUGONLY = 11
	ELSE = 12
	ELSEIF = 13
	ENDEVENT = 14
	ENDFUNCTION = 15
	ENDGROUP = 16
	ENDIF = 17
	ENDPROPERTY = 18
	ENDSTATE = 19
	ENDSTRUCT = 20
	ENDWHILE = 21
	EVENT = 22
	EXTENDS = 23
	FALSE = 24
	FLOAT = 25
	FUNCTION = 26
	GLOBAL = 27
	GROUP = 28
	HIDDEN = 29
	IF = 30
	IMPORT = 31
	INT = 32
	LENGTH = 33
	MANDATORY = 34
	NATIVE = 35
	NEW = 36
	NONE = 37
	PARENT = 38
	PROPERTY = 39
	RETURN = 40
	SCRIPTNAME = 41
	SELF = 42
	STATE = 43
	STRING = 44
	STRUCT = 45
	TRUE = 46
	VAR = 47
	WHILE = 48

KeywordDescription = [
	"AS",
	"AUTO",
	"AUTOREADONLY",
	"BETAONLY",
	"BOOL",
	"COLLAPSED",
	"COLLAPSEDONBASE",
	"COLLAPSEDONREF",
	"CONDITIONAL",
	"CONST",
	"CUSTOMEVENT",
	"DEBUGONLY",
	"ELSE",
	"ELSEIF",
	"ENDEVENT",
	"ENDFUNCTION",
	"ENDGROUP",
	"ENDIF",
	"ENDPROPERTY",
	"ENDSTATE",
	"ENDSTRUCT",
	"ENDWHILE",
	"EVENT",
	"EXTENDS",
	"FALSE",
	"FLOAT",
	"FUNCTION",
	"GLOBAL",
	"GROUP",
	"HIDDEN",
	"IF",
	"IMPORT",
	"INT",
	"LENGTH",
	"MANDATORY",
	"NATIVE",
	"NEW",
	"NONE",
	"PARENT",
	"PROPERTY",
	"RETURN",
	"SCRIPTNAME",
	"SELF",
	"STATE",
	"STRING",
	"STRUCT",
	"TRUE",
	"VAR",
	"WHILE"
]

class Token(object):
	"""Token objects."""
	__slots__ = ["type", "line", "column", "value"]
	def __init__(self, aType, aValue, aLine, aColumn):
		self.type = aType
		self.line = aLine
		self.column = aColumn
		self.value = aValue

class LexicalError(Exception):
	"""Lexical error."""
	def __init__(self, aMessage, aLine, aColumn):
		self.message = aMessage
		self.line = aLine
		self.column = aColumn

class Lexical(object):
	"""Lexical analysis."""
	__slots__ = ["regex", "keywords"]
	def __init__(self):
		self.regex = re.compile(
			"|".join(
				"(?P<t%s>%s)" % pair for pair in [
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
					(TokenEnum.FLOAT, r"(-\d+\.\d+)|(\d+\.\d+)"),
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
			),
			re.IGNORECASE
		)
		self.keywords = [
			"AS",
			"AUTO",
			"AUTOREADONLY",
			"BETAONLY",
			"BOOL",
			"COLLAPSED",
			"COLLAPSEDONBASE",
			"COLLAPSEDONREF",
			"CONDITIONAL",
			"CONST",
			"CUSTOMEVENT",
			"DEBUGONLY",
			"ELSE",
			"ELSEIF",
			"ENDEVENT",
			"ENDFUNCTION",
			"ENDGROUP",
			"ENDIF",
			"ENDPROPERTY",
			"ENDSTATE",
			"ENDSTRUCT",
			"ENDWHILE",
			"EVENT",
			"EXTENDS",
			"FALSE",
			"FLOAT",
			"FUNCTION",
			"GLOBAL",
			"GROUP",
			"HIDDEN",
			"IF",
			"IMPORT",
			"INT",
			"LENGTH",
			"MANDATORY",
			"NATIVE",
			"NEW",
			"NONE",
			"PARENT",
			"PROPERTY",
			"RETURN",
			"SCRIPTNAME",
			"SELF",
			"STATE",
			"STRING",
			"STRUCT",
			"TRUE",
			"VAR",
			"WHILE"
		]

	def Process(self, asString):
		"""Generates tokens from a string."""
		line = 1
		column = -1
		for match in self.regex.finditer(asString):
			t = match.lastgroup
			v = match.group(t)
			t = int(match.lastgroup[1:])
			if t == TokenEnum.WHITESPACE:
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
			if t == TokenEnum.IDENTIFIER:
				try:
					kw = self.keywords.index(v.upper())
					if kw >= 0:
						t = TokenEnum.KEYWORD
						v = kw
				except ValueError:
					pass
			elif t == TokenEnum.DOCSTRING or t == TokenEnum.STRING:
				yield Token(t, v[1:-1], line, match.start()-column)
				i = v.count("\n")
				if i > 0:
					line += i
					column = match.end()-1
				continue
			elif t == TokenEnum.UNMATCHED:
				raise LexicalError("Encountered an unexpected character ('%s')." % v, line, match.start()-column)
				#self.Abort("Encountered an unexpected character ('%s')." % v, line, match.start()-column)
			yield Token(t, v, line, match.start()-column)
			if t == TokenEnum.NEWLINE:
				line += 1
				column = match.end()-1
		yield Token(TokenEnum.NEWLINE, "\n", line, 1)

#2: Syntactic analysis
# Statement types
class StatementEnum(object):
	ASSIGNMENT = 0
	CUSTOMEVENT = 1
	DOCSTRING = 2
	ELSE = 3
	ELSEIF = 4
	ENDEVENT = 5
	ENDFUNCTION = 6
	ENDGROUP = 7
	ENDIF = 8
	ENDPROPERTY = 9
	ENDSTATE = 10
	ENDSTRUCT = 11
	ENDWHILE = 12
	EVENTSIGNATURE = 13
	EXPRESSION = 14
	FUNCTIONSIGNATURE = 15
	GROUPSIGNATURE = 16
	IF = 17
	IMPORT = 18
	PARAMETER = 19
	PROPERTYSIGNATURE = 20
	RETURN = 21
	SCRIPTSIGNATURE = 22
	STATESIGNATURE = 23
	STRUCTSIGNATURE = 24
	VARIABLE = 25
	WHILE = 26

StatementDescription = [
	"ASSIGNMENT",
	"CUSTOMEVENT",
	"DOCSTRING",
	"ELSE",
	"ELSEIF",
	"ENDEVENT",
	"ENDFUNCTION",
	"ENDGROUP",
	"ENDIF",
	"ENDPROPERTY",
	"ENDSTATE",
	"ENDSTRUCT",
	"ENDWHILE",
	"EVENTSIGNATURE",
	"EXPRESSION",
	"FUNCTIONSIGNATURE",
	"GROUPSIGNATURE",
	"IF",
	"IMPORT",
	"PARAMETER",
	"PROPERTYSIGNATURE",
	"RETURN",
	"SCRIPTSIGNATURE",
	"STATESIGNATURE",
	"STRUCTSIGNATURE",
	"VARIABLE",
	"WHILE"
]

class Statement(object):
	__slots__ = ["statementType", "line"]
	def __init__(self, aStatementType, aLine):
		self.statementType = aStatementType
		self.line = aLine

class Keyword(Statement):
	__slots__ = []
	def __init__(self, aStat, aLine):
		super(Keyword, self).__init__(aStat, aLine)

class KeywordExpression(Statement):
	__slots__ = ["expression"]
	def __init__(self, aStat, aLine, aExpression):
		super(KeywordExpression, self).__init__(aStat, aLine)
		self.expression = aExpression

class Type(object):
	__slots__ = ["name", "array"]
	def __init__(self, aName, aArray):
		self.name = aName # String
		self.array = aArray # Bool

class Assignment(Statement):
	__slots__ = ["leftExpression", "rightExpression"]
	def __init__(self, aLine, aLeftExpression, aRightExpression):
		super(Assignment, self).__init__(StatementEnum.ASSIGNMENT, aLine)
		self.leftExpression = aLeftExpression
		self.rightExpression = aRightExpression

class CustomEvent(Keyword):
	__slots__ = ["name"]
	def __init__(self, aLine, aName):
		super(CustomEvent, self).__init__(StatementEnum.CUSTOMEVENT, aLine)
		self.name = aName

class DocString(Statement):
	__slots__ = ["value"]
	def __init__(self, aLine, aValue):
		super(DocString, self).__init__(StatementEnum.DOCSTRING, aLine)
		self.value = aValue

class Else(Keyword):
	__slots__ = []
	def __init__(self, aLine):
		super(Else, self).__init__(StatementEnum.ELSE, aLine)

class EndGroup(Keyword):
	__slots__ = []
	def __init__(self, aLine):
		super(EndGroup, self).__init__(StatementEnum.ENDGROUP, aLine)

class ElseIf(KeywordExpression):
	__slots__ = []
	def __init__(self, aStat, aLine, aExpression):
		super(ElseIf, self).__init__(StatementEnum.ELSEIF, aLine, aExpression)

class EndEvent(Keyword):
	__slots__ = []
	def __init__(self, aLine):
		super(EndEvent, self).__init__(StatementEnum.ENDEVENT, aLine)

class EndFunction(Keyword):
	__slots__ = []
	def __init__(self, aLine):
		super(EndFunction, self).__init__(StatementEnum.ENDFUNCTION, aLine)

class EndIf(Keyword):
	__slots__ = []
	def __init__(self, aLine):
		super(EndIf, self).__init__(StatementEnum.ENDIF, aLine)

class EndProperty(Keyword):
	__slots__ = []
	def __init__(self, aLine):
		super(EndProperty, self).__init__(StatementEnum.ENDPROPERTY, aLine)

class EndState(Keyword):
	__slots__ = []
	def __init__(self, aLine):
		super(EndState, self).__init__(StatementEnum.ENDSTATE, aLine)

class EndStruct(Keyword):
	__slots__ = []
	def __init__(self, aLine):
		super(EndStruct, self).__init__(StatementEnum.ENDSTRUCT, aLine)

class EndWhile(Keyword):
	__slots__ = []
	def __init__(self, aLine):
		super(EndWhile, self).__init__(StatementEnum.ENDWHILE, aLine)

class Expression(Statement):
	__slots__ = ["expression"]
	def __init__(self, aLine, aExpression):
		super(Expression, self).__init__(StatementEnum.EXPRESSION, aLine)
		self.expression = aExpression

class Parameter(object):#Statement):
	__slots__ = ["line", "name", "type", "value"]
	def __init__(self, aLine, aName, aType, aValue):
		#super(Parameter, self).__init__(StatementEnum.PARAMETER, aLine)
		self.line = aLine
		self.name = aName # String
		self.type = aType # Instance of Type
		self.value = aValue # Literal expression

class FunctionSignature(Statement):
	__slots__ = ["name", "type", "flags", "parameters"]
	def __init__(self, aLine, aName, aType, aFlags, aParameters):
		super(FunctionSignature, self).__init__(StatementEnum.FUNCTIONSIGNATURE, aLine)
		self.name = aName
		self.type = aType
		self.flags = aFlags
		self.parameters = aParameters

class GroupSignature(Statement):
	__slots__ = ["name", "flags"]
	def __init__(self, aLine, aName, aFlags):
		super(GroupSignature, self).__init__(StatementEnum.GROUPSIGNATURE, aLine)
		self.name = aName
		self.flags = aFlags

class EventSignature(Statement):
	__slots__ = ["name", "flags", "parameters"]
	def __init__(self, aLine, aName, aFlags, aParameters):
		super(EventSignature, self).__init__(StatementEnum.EVENTSIGNATURE, aLine)
		self.name = aName
		self.flags = aFlags
		self.parameters = aParameters

class If(KeywordExpression):
	__slots__ = []
	def __init__(self, aLine, aExpression):
		super(If, self).__init__(StatementEnum.IF, aLine, aExpression)

class Import(Statement):
	__slots__ = ["script"]
	def __init__(self, aLine, aScript):
		super(Import, self).__init__(StatementEnum.IMPORT, aLine)
		self.script = aScript

class PropertySignature(Statement):
	__slots__ = ["name", "type", "flags", "value"]
	def __init__(self, aLine, aName, aType, aFlags, aValue):
		super(PropertySignature, self).__init__(StatementEnum.PROPERTYSIGNATURE, aLine)
		self.name = aName # String
		self.type = aType # Instance of Type
		self.flags = aFlags # List of Lex.KeywordEnum properties
		self.value = aValue # Literal expression

class Return(KeywordExpression):
	__slots__ = []
	def __init__(self, aLine, aExpression):
		super(Return, self).__init__(StatementEnum.RETURN, aLine, aExpression)

class ScriptSignature(Statement):
	__slots__ = ["name", "parent", "flags"]
	def __init__(self, aLine, aName, aParent, aFlags):
		super(ScriptSignature, self).__init__(StatementEnum.SCRIPTSIGNATURE, aLine)
		self.name = aName
		self.parent = aParent
		self.flags = aFlags

class StateSignature(Statement):
	__slots__ = ["name", "auto"]
	def __init__(self, aLine, aName, aAuto):
		super(StateSignature, self).__init__(StatementEnum.STATESIGNATURE, aLine)
		self.name = aName
		self.auto = aAuto

class StructSignature(Statement):
	__slots__ = ["name", "auto"]
	def __init__(self, aLine, aName, aAuto):
		super(StructSignature, self).__init__(StatementEnum.STRUCTSIGNATURE, aLine)
		self.name = aName

class Variable(Statement):
	__slots__ = ["name", "type", "flags", "value"]
	def __init__(self, aLine, aName, aType, aFlags, aValue):
		super(Variable, self).__init__(StatementEnum.VARIABLE, aLine)
		self.name = aName # String
		self.type = aType # Instance of Type
		self.flags = aFlags # List of Lex.KeywordEnum properties
		self.value = aValue # Expression

class While(KeywordExpression):
	__slots__ = []
	def __init__(self, aLine, aExpression):
		super(While, self).__init__(StatementEnum.WHILE, aLine, aExpression)

class SyntacticError(Exception):
	def __init__(self, aMessage, aLine):
		self.message = aMessage
		self.line = aLine

class Syntactic(object):
	def __init__(self):
		self.stack = None

	def Abort(self, aMessage):
		if self.tokenIndex >= self.tokenCount and self.tokenCount > 0:
			self.tokenIndex -= 1
		if self.stack:
			print(self.stack)
#			for s in self.stack:
#				print(TokenDescription[s.type])
#		print(TokenDescription[self.tokens[self.tokenIndex].type])
		raise SyntacticError(aMessage, self.tokens[self.tokenIndex].line)

	def Accept(self, aToken):
		if self.tokenIndex < self.tokenCount:
			if self.tokens[self.tokenIndex].type == aToken:
				self.tokenIndex += 1
				return True
		return False

	def Expect(self, aToken):
		if self.tokenIndex < self.tokenCount:
			if self.tokens[self.tokenIndex].type == aToken:
				self.tokenIndex += 1
				return True
			self.Abort("Expected a %s symbol instead of a %s symbol." % (TokenDescription[aToken], TokenDescription[self.tokens[self.tokenIndex].type]))
		self.Abort("Expected a %s symbol but no tokens remain." % (TokenDescription[aToken]))

	def AcceptKeyword(self, aKeyword):
		if self.tokenIndex < self.tokenCount:
			if self.tokens[self.tokenIndex].type == TokenEnum.KEYWORD:
				if self.tokens[self.tokenIndex].value == aKeyword:
					self.tokenIndex += 1
					return True
		return False

	def ExpectKeyword(self, aKeyword):
		if self.tokenIndex < self.tokenCount:
			if self.tokens[self.tokenIndex].type == TokenEnum.KEYWORD:
				if self.tokens[self.tokenIndex].value == aKeyword:
					self.tokenIndex += 1
					return True
				self.Abort("Expected the %s keyword instead of the %s keyword." % (KeywordDescription[aKeyword], KeywordDescription[self.tokens[self.tokenIndex].value]))
			self.Abort("Expected a %s symbol instead of a %s symbol." % (TokenDescription[TokenEnum.KEYWORD], TokenDescription[self.tokens[self.tokenIndex].type]))
		self.Abort("Expected a %s symbol but no tokens remain." % (TokenDescription[TokenEnum.KEYWORD]))

	def Peek(self, aN = 1):
		i = self.tokenIndex + aN
		if i < self.tokenCount:
			return self.tokens[i]
		return None

	def PeekBackwards(self, aN = 1):
		i = self.tokenIndex - aN
		if i >= 0:
			return self.tokens[i]
		return None

	def Consume(self):
		if self.tokenIndex < self.tokenCount:
			self.tokenIndex += 1
			return
		self.Abort("No tokens remain.")

	def AcceptFlags(self, aFlags):
		if aFlags:
			successfulFlags = []
			attempts = len(aFlags)
			while attempts > 0:
				i = 0
				flagCount = len(aFlags)
				while i < flagCount:
					if self.AcceptKeyword(aFlags[i]):
						successfulFlags.append(aFlags.pop(i))
						break
					i += 1
				if attempts == len(aFlags):
					return None
				attempts -= 1
			return successfulFlags
		return None

	def Process(self, aTokens):
		if not aTokens:
			return
		self.line = aTokens[0].line
		result = None
		self.tokens = aTokens
		self.tokenIndex = 0
		self.tokenCount = len(self.tokens)
		namespace = None
		nextToken = self.Peek()
		if nextToken and nextToken.type == TokenEnum.COLON and self.Accept(TokenEnum.IDENTIFIER):
			namespace = [self.PeekBackwards()]
			self.Consume()
			nextToken = self.Peek()
			while nextToken and nextToken.type == TokenEnum.COLON and self.Accept(TokenEnum.IDENTIFIER):
				namespace.append(self.PeekBackwards())
				self.Consume()
				nextToken = self.Peek()
			print(namespace)
		if self.tokens[0].type == TokenEnum.KEYWORD:
			keyword = self.tokens[0].value
			#	Functions, properties, and variables
			#		BOOL
			#		FLOAT
			#		INT
			#		STRING
			#		VAR
			
			if keyword == KeywordEnum.BOOL or keyword == KeywordEnum.FLOAT or keyword == KeywordEnum.INT or keyword == KeywordEnum.STRING or keyword == KeywordEnum.VAR:
				#if keyword == KeywordEnum.FUNCTION:
				#	function
				#elif keyword == KeywordEnum.PROPERTY:
				#	property
				#else:
				#	variable
				self.Consume()
				pass

			#	Definitions
			#		IF
			#		ELSEIF
			#		ELSE
			#		ENDIF
			#		WHILE
			#		ENDWHILE
			#		IMPORT
			#		RETURN
			#		FUNCTION
			#		ENDFUNCTION
			#		EVENT
			#		ENDEVENT
			#		STRUCT
			#		ENDSTRUCT
			#		ENDPROPERTY
			#		GROUP
			#		ENDGROUP
			#		CUSTOMEVENT
			#		STATE
			#		ENDSTATE
			#		AUTO
			#			STATE
			#		SCRIPTNAME
			
			elif keyword == KeywordEnum.IF:
				self.Consume()
				pass
			elif keyword == KeywordEnum.ELSEIF:
				self.Consume()
				pass
			elif keyword == KeywordEnum.ELSE:
				result = Else(self.line)
			elif keyword == KeywordEnum.ENDIF:
				result = EndIf(self.line)
			elif keyword == KeywordEnum.WHILE:
				self.Consume()
				pass
			elif keyword == KeywordEnum.ENDWHILE:
				result = EndWhile(self.line)
			elif keyword == KeywordEnum.IMPORT:
				self.Consume()
				self.Expect(TokenEnum.IDENTIFIER)
				result = Import(self.line, self.PeekBackwards())
			elif keyword == KeywordEnum.RETURN:
				self.Consume()
				pass
			elif keyword == KeywordEnum.FUNCTION:
				self.Consume()
				self.Expect(TokenEnum.IDENTIFIER)
				name = self.PeekBackwards()
				parameters = None
#				nextToken = self.Peek()
				self.Expect(TokenEnum.LEFTPARENTHESIS)
#				if nextToken and nextToken.type != self.RIGHT_PARENTHESIS:
#					def Parameter():
#						self.ExpectType(True)
#						typ = self.GetPreviousValue()
#						array = False
#						if self.Accept(self.LEFT_BRACKET):
#							self.Expect(self.RIGHT_BRACKET)
#							array = True
#						self.Expect(self.IDENTIFIER)
#						name = self.GetPreviousValue()
#						value = None
#						if self.Accept(self.OP_ASSIGN):
#							defaultValues = True
#							if not self.Expression():
#								self.Abort("Expected an expression.")
#							value = self.Pop()
#						params.append(ParameterDef(typ.upper(), typ, array, name.upper(), name, value))
#						return True
#					Parameter()
#					while self.Accept(TokenEnum.COMMA):
#						Parameter()
				self.Expect(TokenEnum.RIGHTPARENTHESIS)	
				result = FunctionSignature(self.line, name, None, self.AcceptFlags([KeywordEnum.NATIVE, KeywordEnum.GLOBAL, KeywordEnum.DEBUGONLY, KeywordEnum.BETAONLY]), parameters)
			elif keyword == KeywordEnum.ENDFUNCTION:
				self.Consume()
				result = EndFunction(self.line)
			elif keyword == KeywordEnum.EVENT:
				self.Consume()
				pass
			elif keyword == KeywordEnum.ENDEVENT:
				self.Consume()
				result = EndEvent(self.line)
			elif keyword == KeywordEnum.STRUCT:
				self.Consume()
				pass
			elif keyword == KeywordEnum.ENDSTRUCT:
				self.Consume()
				result = EndStruct(self.line)
			elif keyword == KeywordEnum.ENDPROPERTY:
				self.Consume()
				result = EndProperty(self.line)
			elif keyword == KeywordEnum.GROUP:
				self.Consume()
				pass
			elif keyword == KeywordEnum.ENDGROUP:
				self.Consume()
				result = EndGroup(self.line)
			elif keyword == KeywordEnum.CUSTOMEVENT:
				self.Consume()
				self.Expect(TokenEnum.IDENTIFIER)
				result = CustomEvent(self.line, self.PeekBackwards())
			elif keyword == KeywordEnum.STATE:
				self.Consume()
				self.Expect(TokenEnum.IDENTIFIER)
				result = StateSignature(self.line, self.PeekBackwards(), False)
			elif keyword == KeywordEnum.ENDSTATE:
				self.Consume()
				result = EndState(self.line)
			elif keyword == KeywordEnum.AUTO:
				self.Consume()
				self.ExpectKeyword(KeywordEnum.STATE)
				self.Expect(TokenEnum.IDENTIFIER)
				result = StateSignature(self.line, self.PeekBackwards(), True)
			elif keyword == KeywordEnum.SCRIPTNAME:
				self.Consume()
				self.Expect(TokenEnum.IDENTIFIER)
				name = self.PeekBackwards()
				parent = None
				if self.AcceptKeyword(KeywordEnum.EXTENDS):
					self.Expect(TokenEnum.IDENTIFIER)
					parent = self.PeekBackwards()
				result = ScriptSignature(self.line, name, parent, self.AcceptFlags([KeywordEnum.HIDDEN, KeywordEnum.CONDITIONAL, KeywordEnum.NATIVE]))

			#	Expressions (or assignments)
			#		FALSE
			#		NEW
			#		NONE
			#		PARENT
			#		SELF
			#		TRUE
			#
			#	Other keywords
			#		AS
			#		AUTOREADONLY
			#		BETAONLY
			#		COLLAPSED
			#		COLLAPSEDONBASE
			#		COLLAPSEDONREF
			#		CONDITIONAL
			#		CONST
			#		DEBUGONLY
			#		EXTENDS
			#		GLOBAL
			#		HIDDEN
			#		LENGTH
			#		MANDATORY
			#		NATIVE
			#		PROPERTY

			else:
				pass
		if self.tokenIndex < self.tokenCount:
			if self.tokens[self.tokenIndex].type == TokenEnum.KEYWORD:
				self.Abort("Unexpected %s symbol (%s)." % (TokenDescription[self.tokens[self.tokenIndex].type], KeywordDescription[self.tokens[self.tokenIndex].value]))
			else:
				self.Abort("Unexpected %s symbol (%s)." % (TokenDescription[self.tokens[self.tokenIndex].type], self.tokens[self.tokenIndex].value))
		if not result:
			self.Abort("Could not form a valid statement.")
		return result

## Node types
#class NodeEnum(object):
#	ARRAYATOM = 0
#	ARRAYCREATION = 1
#	ARRAYFUNCORID = 2
#	BINARYOPERATOR = 3
#	CONSTANT = 4
#	EXPRESSION = 5
#	FUNCTIONCALL = 6
#	FUNCTIONCALLARGUMENT = 7
#	IDENTIFIER = 8
#	LENGTH = 9
#	UNARYOPERATOR = 10
#
#NodeDescription = [
#	"ARRAYATOM", #ARRAYATOM
#	"ARRAYCREATION", #ARRAYCREATION
#	"ARRAYFUNCORID", #ARRAYFUNCORID
#	"BINARYOPERATOR", #BINARYOPERATOR
#	"CONSTANT", #CONSTANT
#	"EXPRESSION", #EXPRESSION
#	"FUNCTIONCALL", #FUNCTIONCALL
#	"FUNCTIONCALLARGUMENT", #FUNCTIONCALLARGUMENT
#	"IDENTIFIER", #IDENTIFIER
#	"LENGTH", #LENGTH
#	"UNARYOPERATOR" #UNARYOPERATOR
#]
#
#class Node(object):
#	__slots__ = ["type"]
#	def __init__(self, aType):
#		self.type = aType
#
#class BinaryOperatorNode(Node):
#	__slots__ = ["operator", "leftOperand", "rightOperand"]
#	def __init__(self, aOperator, aLeftOperand, aRightOperand):
#		super(BinaryOperatorNode, self).__init__(NodeEnum.BINARYOPERATOR)
#		self.operator = aOperator
#		self.leftOperand = aLeftOperand
#		self.rightOperand = aRightOperand
#
#class UnaryOperatorNode(Node):
#	__slots__ = ["operator", "operand"]
#	def __init__(self, aOperator, aOperand):
#		super(UnaryOperatorNode, self).__init__(NodeEnum.UNARYOPERATOR)
#		self.operator = aOperator
#		self.operand = aOperand
#
#class ExpressionNode(Node):
#	__slots__ = ["child"]
#	def __init__(self, aChild):
#		super(ExpressionNode, self).__init__(NodeEnum.EXPRESSION)
#		self.child = aChild
#
#class ArrayAtomNode(Node):
#	__slots__ = ["child", "expression"]
#	def __init__(self, aChild, aExpression):
#		super(ArrayAtomNode, self).__init__(NodeEnum.ARRAYATOM)
#		self.child = aChild
#		self.expression = aExpression
#
#class ArrayFuncOrIdNode(Node):
#	__slots__ = ["child", "expression"]
#	def __init__(self, aChild, aExpression):
#		super(ArrayFuncOrIdNode, self).__init__(NodeEnum.ARRAYFUNCORID)
#		self.child = aChild
#		self.expression = aExpression
#
#class ConstantNode(Node):
#	__slots__ = ["value"]
#	def __init__(self, aValue):
#		super(ConstantNode, self).__init__(NodeEnum.CONSTANT)
#		self.value = aValue
#
#class FunctionCallNode(Node):
#	__slots__ = ["name", "arguments"]
#	def __init__(self, aName, aArguments):
#		super(FunctionCallNode, self).__init__(NodeEnum.FUNCTIONCALL)
#		self.name = aName
#		self.arguments = aArguments
#
#class FunctionCallArgument(Node):
#	__slots__ = ["name", "expression"]
#	def __init__(self, aName, aExpression):
#		super(FunctionCallArgument, self).__init__(NodeEnum.FUNCTIONCALLARGUMENT)
#		self.name = aName
#		self.expression = aExpression
#
#class IdentifierNode(Node):
#	__slots__ = ["value"]
#	def __init__(self, aValue):
#		super(IdentifierNode, self).__init__(NodeEnum.IDENTIFIER)
#		self.value = aValue
#
#class LengthNode(Node):
#	__slots__ = []
#	def __init__(self):
#		super(LengthNode, self).__init__(NodeEnum.LENGTH)
#
#class ArrayCreationNode(Node):
#	__slots__ = ["arrayType", "size"]
#	def __init__(self, aArrayType, aSize):
#		super(ArrayCreationNode, self).__init__(NodeEnum.ARRAYCREATION)
#		self.arrayType = aArrayType
#		self.size = aSize
#
#class SyntacticError(Exception):
#	def __init__(self, aMessage, aLine):
#		self.message = aMessage
#		self.line = aLine
#
#class Syntactic(object):
#	def __init__(self):
#		pass
#
#	def Accept(self, aToken):
#		if self.tokenIndex < self.tokenLength:
#			if self.tokens[self.tokenIndex].type == aToken:
#				self.tokenIndex += 1
#				return True
#		return False
#
#	def Expect(self, aToken):
#		if self.tokenIndex < self.tokenLength:
#			if self.tokens[self.tokenIndex].type == aToken:
#				self.tokenIndex += 1
#				return True
#			self.Abort("Expected a %s symbol instead of a %s symbol." % (TokenDescription[aToken], TokenDescription[self.tokens[self.tokenIndex].type]))
#		self.Abort("Expected a %s symbol but no tokens remain." % (TokenDescription[aToken]))
#
#	def PeekBackwards(self, aN = 1):
#		i = self.tokenIndex - aN
#		if i >= 0:
#			return self.tokens[i]
#
#	def Peek(self, aN = 1):
#		i = self.tokenIndex + aN
#		if i < self.tokenLength:
#			return self.tokens[i]
#
#	def Consume(self):
#		if self.tokenIndex < self.tokenLength:
#			self.tokenIndex += 1
#			return
#		self.Abort("No tokens remain.")
#
#	def AcceptKeyword(self, aKeyword):
#		if self.tokenIndex < self.tokenLength:
#			if self.tokens[self.tokenIndex].type == TokenEnum.KEYWORD:
#				if self.tokens[self.tokenIndex].value == aKeyword:
#					self.tokenIndex += 1
#					return True
#		return False
#
#	def ExpectKeyword(self, aKeyword):
#		if self.tokenIndex < self.tokenLength:
#			if self.tokens[self.tokenIndex].type == TokenEnum.KEYWORD:
#				if self.tokens[self.tokenIndex].value == aKeyword:
#					self.tokenIndex += 1
#					return True
#				self.Abort("Expected the %s keyword instead of the %s keyword." % (KeywordDescription[aKeyword], KeywordDescription[self.tokens[self.tokenIndex].value]))
#			self.Abort("Expected a %s symbol instead of a %s symbol." % (TokenDescription[TokenEnum.KEYWORD], TokenDescription[self.tokens[self.tokenIndex].type]))
#		self.Abort("Expected a %s symbol but no tokens remain." % (TokenDescription[TokenEnum.KEYWORD]))
#
#	def Abort(self, aMessage):
#		if self.tokenIndex >= self.tokenLength and self.tokenLength > 0:
#			self.tokenIndex -= 1
#		if self.stack:
#			print(self.stack)
#			for s in self.stack:
#				print(TokenDescription[s.type])
##		print(TokenDescription[self.tokens[self.tokenIndex].type])
#		raise SyntacticError(aMessage, self.tokens[self.tokenIndex].line)
#
#	def Process(self, aTokens):
#		self.tokens = aTokens
#		self.tokenIndex = 0
#		self.tokenLength = len(aTokens)
#		self.line = self.tokens[0].line
#		result = None
#		if self.Accept(TokenEnum.DOCSTRING):
#			result = DocString(self.line, self.PeekBackwards().value)
#		#elif self.Accept(TokenEnum.IDENTIFIER):
#		elif self.tokens[self.tokenIndex].type == TokenEnum.IDENTIFIER:
#			# Variable, property, function, expression, or assignment
#			nextToken1 = self.Peek(1)
#			nextToken2 = self.Peek(2)
#			if nextToken1 and nextToken1.type == TokenEnum.LEFTBRACKET:
#				if nextToken2 and nextToken2.type == TokenEnum.RIGHTBRACKET:
#					typ = self.tokens[self.tokenIndex]
#					self.Consume()
#					self.Consume()
#					self.Consume()
#					if self.Accept(TokenEnum.IDENTIFIER):
#						# Array variable
#						result = self.Variable(typ.value, True)
#					elif self.tokens[self.tokenIndex].type == TokenEnum.KEYWORD:
#						if self.tokens[self.tokenIndex].value == KeywordEnum.FUNCTION:
#							self.Consume()
#							result = self.Function(typ.value, True)
#						elif self.tokens[self.tokenIndex].value == KeywordEnum.PROPERTY:
#							self.Consume()
#							result = self.Property(typ.value, True)
#						else:
#							self.Abort("Expected the %s or the %s keyword." % (KeywordDescription[KeywordEnum.FUNCTION], KeywordDescription[KeywordEnum.PROPERTY]))
##				else:
##					result = self.ExpressionOrAssignment()
#			else:
#				#if self.Accept(TokenEnum.IDENTIFIER):
#				if nextToken1 and nextToken1.type == TokenEnum.IDENTIFIER:
#					# Non-array variable
#					result = self.Variable(typ.value, False)
#				#elif self.tokens[self.tokenIndex].type == TokenEnum.KEYWORD:
#				elif nextToken1.type == TokenEnum.KEYWORD:
#					#if self.tokens[self.tokenIndex].value == KeywordEnum.FUNCTION:
#					if nextToken1.value == KeywordEnum.FUNCTION:
#						typ = self.tokens[self.tokenIndex]
#						self.Consume()
#						self.Consume()
#						result = self.Function(typ.value, False)
#					#elif self.tokens[self.tokenIndex].value == KeywordEnum.PROPERTY:
#					elif nextToken1.value == KeywordEnum.PROPERTY:
#						typ = self.tokens[self.tokenIndex]
#						self.Consume()
#						self.Consume()
#						result = self.Property(typ.value, False)
#					else:
#						self.Abort("Expected the %s or the %s keyword." % (KeywordDescription[KeywordEnum.FUNCTION], KeywordDescription[KeywordEnum.PROPERTY]))
#			if not result:
#				result = self.ExpressionOrAssignment()
#		elif self.tokens[self.tokenIndex].type == TokenEnum.KEYWORD and (self.tokens[self.tokenIndex].value == KeywordEnum.BOOL or self.tokens[self.tokenIndex].value == KeywordEnum.FLOAT or self.tokens[self.tokenIndex].value == KeywordEnum.INT or self.tokens[self.tokenIndex].value == KeywordEnum.STRING):
#			# Variable, property, or function
#			self.Consume()
#			typ = self.PeekBackwards()
#			array = False
#			nextToken1 = self.Peek(1)
#			nextToken2 = self.Peek(2)
#			if nextToken1 and nextToken1.type == TokenEnum.LEFTBRACKET and nextToken2 and nextToken2.type == TokenEnum.RIGHTBRACKET:
#				self.Consume()
#				self.Consume()
#				array = True
#			if self.Accept(TokenEnum.IDENTIFIER):
#				result = self.Variable(typ.value, array)
#			elif self.tokens[self.tokenIndex].type == TokenEnum.KEYWORD:
#				if self.tokens[self.tokenIndex].value == KeywordEnum.FUNCTION:
#					self.Consume()
#				elif self.tokens[self.tokenIndex].value == KeywordEnum.PROPERTY:
#					self.Consume()
#					result = self.Property(typ, array)
#				else:
#					self.Abort("Expected the %s or the %s keyword." % (KeywordDescription[KeywordEnum.FUNCTION], KeywordDescription[KeywordEnum.PROPERTY]))
#		elif self.tokens[self.tokenIndex].type == TokenEnum.KEYWORD:
#			if self.tokens[self.tokenIndex].value == KeywordEnum.FALSE or self.tokens[self.tokenIndex].value == KeywordEnum.TRUE or self.tokens[self.tokenIndex].value == KeywordEnum.NEW or self.tokens[self.tokenIndex].value == KeywordEnum.NONE or self.tokens[self.tokenIndex].value == KeywordEnum.PARENT or self.tokens[self.tokenIndex].value == KeywordEnum.SELF:
#				result = self.ExpressionOrAssignment()
#			else:
#				#IF
#				if self.tokens[self.tokenIndex].value == KeywordEnum.IF:
#					self.Consume()
#					pass
#				#ELSE
#				elif self.tokens[self.tokenIndex].value == KeywordEnum.ELSE:
#					self.Consume()
#					result = Else(self.line)
#				#ELSEIF
#				elif self.tokens[self.tokenIndex].value == KeywordEnum.ELSEIF:
#					self.Consume()
#					pass
#				#ENDIF
#				elif self.tokens[self.tokenIndex].value == KeywordEnum.ENDIF:
#					self.Consume()
#					result = EndIf(self.line)
#				#WHILE
#				elif self.tokens[self.tokenIndex].value == KeywordEnum.WHILE:
#					self.Consume()
#					pass
#				#ENDWHILE
#				elif self.tokens[self.tokenIndex].value == KeywordEnum.ENDWHILE:
#					self.Consume()
#					result = EndWhile(self.line)
#				#RETURN
#				elif self.tokens[self.tokenIndex].value == KeywordEnum.RETURN:
#					self.Consume()
#					pass
#				#FUNCTION
#				elif self.tokens[self.tokenIndex].value == KeywordEnum.FUNCTION:
#					self.Consume()
#					result = self.Function(None, False)
#				#ENDFUNCTION
#				elif self.tokens[self.tokenIndex].value == KeywordEnum.ENDFUNCTION:
#					self.Consume()
#					result = EndFunction(self.line)
#				#EVENT
#				elif self.tokens[self.tokenIndex].value == KeywordEnum.EVENT:
#					self.Consume()
#					params = []
#
#					def Param():
#						self.ExpectType(True)
#						typ = self.PeekBackwards()
#						array = False
#						if self.Accept(TokenEnum.LEFTBRACKET):
#							self.Expect(TokenEnum.RIGHTBRACKET)
#							array = True
#						self.Expect(TokenEnum.IDENTIFIER)
#						name = self.PeekBackwards()
#						params.append(Parameter(self.line, name.value, Type(typ.value, array), None))
#						return True
#
#					self.Expect(TokenEnum.IDENTIFIER)
#					name = self.PeekBackwards()
#					nextToken = self.Peek()
#					self.Expect(TokenEnum.LEFTPARENTHESIS)
#					if nextToken and nextToken.type != TokenEnum.RIGHTPARENTHESIS:
#						Param()
#						while self.Accept(TokenEnum.COMMA):
#							Param()
#					self.Expect(TokenEnum.RIGHTPARENTHESIS)
#					flags = None
#					if self.AcceptKeyword(KeywordEnum.NATIVE):
#						flags = [KeywordEnum.NATIVE]
#					if not params:
#						params = None
#					return EventSignature(self.line, name.value, flags, params)
#				#ENDEVENT
#				elif self.tokens[self.tokenIndex].value == KeywordEnum.ENDEVENT:
#					self.Consume()
#					result = EndEvent(self.line)
#				#ENDPROPERTY
#				elif self.tokens[self.tokenIndex].value == KeywordEnum.ENDPROPERTY:
#					self.Consume()
#					result = EndProperty(self.line)
#				#STATE
#				elif self.tokens[self.tokenIndex].value == KeywordEnum.STATE:
#					self.Consume()
#					self.Expect(TokenEnum.IDENTIFIER)
#					result = StateSignature(self.line, self.PeekBackwards().value, False)
#				#ENDSTATE
#				elif self.tokens[self.tokenIndex].value == KeywordEnum.ENDSTATE:
#					self.Consume()
#					result = EndState(self.line)
#				#AUTO
#				elif self.tokens[self.tokenIndex].value == KeywordEnum.AUTO:
#					self.Consume()
#					self.ExpectKeyword(KeywordEnum.STATE)
#					self.Expect(TokenEnum.IDENTIFIER)
#					result = StateSignature(self.line, self.PeekBackwards().value, True)
#				#IMPORT
#				elif self.tokens[self.tokenIndex].value == KeywordEnum.IMPORT:
#					self.Consume()
#					self.Expect(TokenEnum.IDENTIFIER)
#					result = Import(self.line, self.PeekBackwards().value)
#				#SCRIPTNAME
#				elif self.tokens[self.tokenIndex].value == KeywordEnum.SCRIPTNAME:
#					self.Consume()
#					if self.Accept(TokenEnum.IDENTIFIER):
#						name = self.PeekBackwards()
#						parent = None
#						flags = None
#						if self.AcceptKeyword(KeywordEnum.EXTENDS):
#							self.Expect(TokenEnum.IDENTIFIER)
#							parent = self.PeekBackwards()
#						if self.AcceptKeyword(KeywordEnum.CONDITIONAL):
#							flags = [KeywordEnum.CONDITIONAL]
#							if self.AcceptKeyword(KeywordEnum.HIDDEN):
#								flags.append(KeywordEnum.HIDDEN)
#						elif self.AcceptKeyword(KeywordEnum.HIDDEN):
#							flags = [KeywordEnum.CONDITIONAL]
#							if self.AcceptKeyword(KeywordEnum.CONDITIONAL):
#								flags.append(KeywordEnum.CONDITIONAL)
#						result = ScriptSignature(self.line, name.value, parent.value, flags)
#		if self.tokenIndex < self.tokenLength:
#			if self.tokens[self.tokenIndex].type == TokenEnum.KEYWORD:
#				self.Abort("Unexpected %s symbol (%s)." % (TokenDescription[self.tokens[self.tokenIndex].type], KeywordDescription[self.tokens[self.tokenIndex].value]))
#			else:
#				self.Abort("Unexpected %s symbol (%s)." % (TokenDescription[self.tokens[self.tokenIndex].type], self.tokens[self.tokenIndex].value))
#		return result
#
#	def Property(self, aType, aArray):
#		value = None #TODO Implement once Expression has been implemented
#		flags = None
#		self.Expect(TokenEnum.IDENTIFIER)
#		name = self.PeekBackwards()
#		if self.Accept(TokenEnum.ASSIGN):
#			# Replace with self.Expression()
#			if self.Accept(TokenEnum.FLOAT):
#				pass
#			elif self.Accept(TokenEnum.INT):
#				pass
#			elif self.Accept(TokenEnum.STRING):
#				pass
#			elif self.AcceptKeyword(KeywordEnum.TRUE):
#				pass
#			elif self.AcceptKeyword(KeywordEnum.FALSE):
#				pass
#			elif self.AcceptKeyword(KeywordEnum.NONE):
#				pass
#			elif self.Accept(TokenEnum.SUBTRACTION):
#				if self.Accept(TokenEnum.FLOAT):
#					pass
#				elif self.Accept(TokenEnum.INT):
#					pass
#			else:
#				self.Abort("Expected a literal.")
#			# End replace
#			if self.AcceptKeyword(KeywordEnum.AUTO):
#				flags = [KeywordEnum.AUTO]
#			elif self.AcceptKeyword(KeywordEnum.AUTOREADONLY):
#				flags = [KeywordEnum.AUTOREADONLY]
#			else:
#				self.Abort("Expected the %s or the %s keyword." % (KeywordDescription[KeywordEnum.AUTO], KeywordDescription[KeywordEnum.AUTOREADONLY]))
#			if self.AcceptKeyword(KeywordEnum.CONDITIONAL):
#				flags.append(KeywordEnum.CONDITIONAL)
#				if self.AcceptKeyword(KeywordEnum.HIDDEN):
#					flags.append(KeywordEnum.HIDDEN)
#			if self.AcceptKeyword(KeywordEnum.HIDDEN):
#				flags.append(KeywordEnum.HIDDEN)
#				if self.AcceptKeyword(KeywordEnum.CONDITIONAL):
#					flags.append(KeywordEnum.CONDITIONAL)
#		else:
#			if self.AcceptKeyword(KeywordEnum.AUTO):
#				flags = [KeywordEnum.AUTO]
#			elif self.AcceptKeyword(KeywordEnum.AUTOREADONLY):
#				flags = [KeywordEnum.AUTOREADONLY]
#			if flags:
#				if self.AcceptKeyword(KeywordEnum.CONDITIONAL):
#					flags.append(KeywordEnum.CONDITIONAL)
#					if self.AcceptKeyword(KeywordEnum.HIDDEN):
#						flags.append(KeywordEnum.HIDDEN)
#				elif self.AcceptKeyword(KeywordEnum.HIDDEN):
#					flags.append(KeywordEnum.HIDDEN)
#					if self.AcceptKeyword(KeywordEnum.CONDITIONAL):
#						flags.append(KeywordEnum.CONDITIONAL)
#		return PropertySignature(self.line, name.value, Type(aType, aArray), flags, value)
#
#	def Function(self, aType, aArray):
#		params = []
#
#		def Param():
#			#self.ExpectType(True)
#			typ = None
#			if self.Accept(TokenEnum.IDENTIFIER) or (self.tokens[self.tokenIndex].type == TokenEnum.KEYWORD and (self.tokens[self.tokenIndex].value == KeywordEnum.BOOL or self.tokens[self.tokenIndex].value == KeywordEnum.FLOAT or self.tokens[self.tokenIndex].value == KeywordEnum.INT or self.tokens[self.tokenIndex].value == KeywordEnum.STRING)):
#				self.Consume()
#				typ = self.PeekBackwards()
#			else:
#				self.Abort("Expected a parameter type.")
#			array = False
#			if self.Accept(TokenEnum.LEFTBRACKET):
#				self.Expect(TokenEnum.RIGHTBRACKET)
#				array = True
#			self.Expect(TokenEnum.IDENTIFIER)
#			name = self.PeekBackwards()
#			value = None
#			if self.Accept(TokenEnum.ASSIGN):
#				defaultValues = True
#				if not self.Expression():
#					self.Abort("Expected an expression.")
#				value = self.Pop()
#			params.append(Parameter(self.line, name.value, Type(typ.value, array), value))
#			return True
#
#		#typ = None
#		#array = False
#		#if self.AcceptType(True):
#		#	typ = self.GetPreviousValue()
#		#	if self.Accept(TokenEnum.LEFTBRACKET):
#		#		self.Expect(TokenEnum.RIGHTBRACKET)
#		#		array = True
#		#self.ExpectKeyword(KeywordEnum.FUNCTION)
#		self.Expect(TokenEnum.IDENTIFIER)
#		name = self.PeekBackwards()
#		nextToken = self.Peek()
#		self.Expect(TokenEnum.LEFTPARENTHESIS)
#		if nextToken and nextToken.type != TokenEnum.RIGHTPARENTHESIS:
#			Param()
#			while self.Accept(TokenEnum.COMMA):
#				Param()
#		self.Expect(TokenEnum.RIGHTPARENTHESIS)	
#		flags = None
#		if self.AcceptKeyword(KeywordEnum.GLOBAL):
#			flags = [KeywordEnum.GLOBAL]
#			if self.AcceptKeyword(KeywordEnum.NATIVE):
#				flags.append(KeywordEnum.NATIVE)
#		elif self.AcceptKeyword(KeywordEnum.NATIVE):
#			flags = [KeywordEnum.NATIVE]
#			if self.AcceptKeyword(KeywordEnum.GLOBAL):
#				flags.append(KeywordEnum.GLOBAL)
#		if aType:
#			return FunctionSignature(self.line, name.value, Type(aType, aArray), flags, params)
#		else:
#			return FunctionSignature(self.line, name.value, None, flags, params)
	#
#	def Variable(self, aType, aArray):
#		#self.ExpectType(True)
#		#line = self.GetPreviousLine()
#		#typ = None
#		#if self.GetPreviousType() == self.IDENTIFIER:
#		#	typ = self.GetPreviousValue()
#		#else:
#		#	typ = self.GetPreviousType()
#		#array = False
#		#if self.Accept(self.LEFT_BRACKET):
#		#	self.Expect(self.RIGHT_BRACKET)
#		#	array = True
#		#self.Expect(TokenEnum.IDENTIFIER)
#		name = self.PeekBackwards()
#		value = None
#		if self.Accept(TokenEnum.ASSIGN):
#			self.Expression()
#			value = self.Pop()
#		flags = None
#		if self.AcceptKeyword(KeywordEnum.CONDITIONAL):
#			flags = [KeywordEnum.CONDITIONAL]
#		return Variable(self.line, name.value, Type(aType, aArray), flags, value)
#
#	def ExpressionOrAssignment(self):
#		self.stack = []
#		self.Expression()
#		left = self.Pop()
#		if self.Accept(TokenEnum.ASSIGN) or self.Accept(TokenEnum.ASSIGNADDITION) or self.Accept(TokenEnum.ASSIGNSUBTRACTION) or self.Accept(TokenEnum.ASSIGNMULTIPLICATION) or self.Accept(TokenEnum.ASSIGNDIVISION) or self.Accept(TokenEnum.ASSIGNMODULUS):
#			operator = self.PeekBackwards()
#			self.Expression()
#			right = self.Pop()
#			return Assignment(self.line, left, right)
#		elif self.tokenIndex >= self.tokenLength or self.tokens[self.tokenIndex] == None:
#			return Expression(self.line, left)
#
#	def Shift(self, aItem = None):
#		if aItem:
#			self.stack.append(aItem)
#		else:
#			self.stack.append(self.PeekBackwards())
#
#	def Pop(self):
#		if len(self.stack) > 0:
#			return self.stack.pop()
#		else:
#			return None
#
#	def ReduceBinaryOperator(self):
#		operand2 = self.Pop()
#		operator = self.Pop()
#		operand1 = self.Pop()
#		self.Shift(BinaryOperatorNode(operator, operand1, operand2))
#
#	def ReduceUnaryOperator(self):
#		operand = self.Pop()
#		operator = self.Pop()
#		self.Shift(UnaryOperatorNode(operator, operand))
#
#	def Expression(self):
##		print(1)
#		def Reduce():
#			self.Shift(ExpressionNode(self.Pop()))
#
#		self.AndExpression()
#		while self.Accept(TokenEnum.OR):
#			self.Shift()
#			self.AndExpression()
#			self.ReduceBinaryOperator()
#		Reduce()
#		return True
#
#	def AndExpression(self):
##		print(2)
#		self.BoolExpression()
#		while self.Accept(TokenEnum.AND):
#			self.Shift()
#			self.BoolExpression()
#			self.ReduceBinaryOperator()
#		return True
#
#	def BoolExpression(self):
##		print(3)
#		self.AddExpression()
#		while self.Accept(TokenEnum.EQUAL) or self.Accept(TokenEnum.NOTEQUAL) or self.Accept(TokenEnum.GREATERTHANOREQUAL) or self.Accept(TokenEnum.LESSTHANOREQUAL) or self.Accept(TokenEnum.GREATERTHAN) or self.Accept(TokenEnum.LESSTHAN):
#			self.Shift()
#			self.AddExpression()
#			self.ReduceBinaryOperator()
#		return True
#
#	def AddExpression(self):
##		print(4)
#		self.MultExpression()
#		while self.Accept(TokenEnum.ADDITION) or self.Accept(TokenEnum.SUBTRACTION):
#			self.Shift()
#			self.MultExpression()
#			self.ReduceBinaryOperator()
#		return True
#
#	def MultExpression(self):
##		print(5)
#		self.UnaryExpression()
#		while self.Accept(TokenEnum.MULTIPLICATION) or self.Accept(TokenEnum.DIVISION) or self.Accept(TokenEnum.MODULUS):
#			self.Shift()
#			self.UnaryExpression()
#			self.ReduceBinaryOperator()
#		return True
#
#	def UnaryExpression(self):
##		print(6)
#		unaryOp = False
#		if self.Accept(TokenEnum.SUBTRACTION) or self.Accept(TokenEnum.NOT):
#			self.Shift()
#			unaryOp = True
#		self.CastAtom()
#		if unaryOp:
#			self.ReduceUnaryOperator()
#		return True
#
#	def CastAtom(self):
##		print(7)
#		self.DotAtom()
#		if self.AcceptKeyword(KeywordEnum.AS):
#			self.Shift()
#			#self.ExpectType(True)
#			if self.Accept(TokenEnum.IDENTIFIER) or (self.tokens[self.tokenIndex].type == TokenEnum.KEYWORD and (self.tokens[self.tokenIndex].value == KeywordEnum.BOOL or self.tokens[self.tokenIndex].value == KeywordEnum.FLOAT or self.tokens[self.tokenIndex].value == KeywordEnum.INT or self.tokens[self.tokenIndex].value == KeywordEnum.STRING)):
#				self.Consume()
#			else:
#				self.Abort("Expected a type.")
#			self.Shift(IdentifierNode(self.PeekBackwards().value))
#			self.ReduceBinaryOperator()
#		return True
#
#	def DotAtom(self):
##		print(8)
#		#if self.AcceptLiteral():
#		if self.AcceptKeyword(KeywordEnum.FALSE) or self.AcceptKeyword(KeywordEnum.TRUE) or self.Accept(TokenEnum.FLOAT) or self.Accept(TokenEnum.INT) or self.Accept(TokenEnum.STRING) or self.AcceptKeyword(KeywordEnum.NONE):
#			self.Shift(ConstantNode(self.PeekBackwards().value))
#			return True
#		elif self.Accept(TokenEnum.SUBTRACTION) and (self.Accept(TokenEnum.INT) or self.Expect(TokenEnum.FLOAT)):
#			self.Shift(ConstantNode(UnaryOperatorNode(self.PeekBackwards(2).value, self.PeekBackwards(1).value)))
#			return True
#		elif self.ArrayAtom():
#			while self.Accept(TokenEnum.DOT):
#				self.Shift()
#				self.ArrayFuncOrId()
#				self.ReduceBinaryOperator()
#			return True
#
#	def ArrayAtom(self):
##		print(9)
#		def Reduce():
#			temp = self.Pop()
#			self.Shift(ArrayAtomNode(self.Pop(), temp))
#
#		self.Atom()
#		if self.Accept(TokenEnum.LEFTBRACKET):
#			self.Expression()
#			self.Expect(TokenEnum.RIGHTBRACKET)
#			Reduce()
#		return True
#
#	def Atom(self):
##		print(10)
#		if self.AcceptKeyword(KeywordEnum.NEW):
#			self.ExpectType(True)
#			typ = self.PeekBackwards()
#			self.Expect(TokenEnum.LEFTBRACKET)
#			if not self.Accept(TokenEnum.INT):
#				self.Abort("Expected an int literal.")
#			size = self.PeekBackwards()
#			self.Expect(TokenEnum.RIGHTBRACKET)
#			self.Shift(ArrayCreationNode(typ, size))
#			return True
#		elif self.Accept(TokenEnum.LEFTPARENTHESIS):
#			self.Shift()
#			self.Expression()
#			self.Expect(TokenEnum.RIGHTPARENTHESIS)
#			expr = self.Pop()
#			self.Pop()
#			self.Shift(expr)
#			return True
#		elif self.FuncOrId():
#			return True
#
#	def ArrayFuncOrId(self):
##		print(11)
#		def Reduce():
#			temp = self.Pop()
#			self.Shift(ArrayFuncOrIdNode(self.Pop(), temp))
#
#		self.FuncOrId()
#		if self.Accept(TokenEnum.LEFTBRACKET):
#			self.Expression()
#			self.Expect(TokenEnum.RIGHTBRACKET)
#			Reduce()
#		return True
#
#	def FuncOrId(self):
##		print(12)
#		nextToken = self.Peek()
#		if nextToken and nextToken.type == TokenEnum.LEFTPARENTHESIS:
#			self.FunctionCall()
#			return True
#		elif self.Accept(KeywordEnum.LENGTH):
#			self.Shift(LengthNode())
#			return True
#		elif self.Accept(TokenEnum.IDENTIFIER) or self.AcceptKeyword(KeywordEnum.SELF) or self.AcceptKeyword(KeywordEnum.PARENT):
#			self.Shift(IdentifierNode(self.PeekBackwards().value))
#			return True
#		else:
#			self.Abort("Expected a function call, and identifier, or the LENGTH keyword")
#
#	def FunctionCall(self):
##		print(13)
#		def Reduce():
#			arguments = []
#			temp = self.Pop() # Right parenthesis
#			temp = self.Pop()
#			while temp.type == NodeEnum.FUNCTIONCALLARGUMENT:
#				arguments.insert(0, temp)
#				temp = self.Pop()
#			self.Shift(FunctionCallNode(self.Pop().value, arguments))
#
#		def Argument():
#			ident = None
#			nextToken = self.Peek()
#			if nextToken and nextToken.type == TokenEnum.ASSIGN:
#				self.Expect(TokenEnum.IDENTIFIER)
#				ident = self.PeekBackwards()
#				self.Expect(TokenEnum.ASSIGN)
#			self.Expression()
#			expr = self.Pop()
#			self.Shift(FunctionCallArgument(ident, expr))
#			return True
#
#		self.Expect(TokenEnum.IDENTIFIER)
#		self.Shift()
#		self.Expect(TokenEnum.LEFTPARENTHESIS)
#		self.Shift()
#		if self.Accept(TokenEnum.RIGHTPARENTHESIS):
#			self.Shift()
#			Reduce()
#			return True
#		else:
#			Argument()
#			while self.Accept(TokenEnum.COMMA):
#				Argument()
#			self.Expect(TokenEnum.RIGHTPARENTHESIS)
#			self.Shift()
#			Reduce()
#			return True
#
##3: Semantic analysis
#class Script(object):
#	__slots__ = ["name", "parent", "flags", "properties", "variables", "functions", "states"]
#	def __init__(self, aName, aParent, aFlags, aProperties, aVariables, aFunctions, aStates):
#		self.name = aName # String
#		self.parent = aParent # Script instance
#		self.flags = aFlags # List of Lex.KeywordEnum properties
#		self.properties = aProperties # Dict of Property instances
#		self.variables = aVariables # Dict of Variable instances
#		self.functions = aFunctions # Dict of Function/Event instances
#		self.states = aStates # Dict of State instances
#
#class Property(object):
#	__slots__ = ["starts", "ends", "signature", "functions"]
#	def __init__(self, aStarts, aEnds, aSignature, aFunctions):
#		self.starts = aStarts # Integer
#		self.ends = aEnds # Integer
#		self.signature = aSignature # Instance of Syn.PropertySignature
#		self.functions = aFunctions # Dict of Function/Event instances
#
#class Function(object):
#	__slots__ = ["starts", "ends", "name", "type", "flags", "parameters"]
#	def __init__(self, aStarts, aEnds, aName, aType, aFlags, aParameters):
#		self.starts = aStarts # Integer
#		self.ends = aEnds # Integer
#		self.name = aName # String
#		self.type = aType # Instance of Type
#		self.flags = aFlags # List of Lex.KeywordEnum properties
#		self.parameters = aParameters # List of Parameter instances
#
#class Event(Function):
#	def __init__(self, aStarts, aEnds, aName, aType, aFlags, aParameters):
#		super(Event, self).__init__(aStarts, aEnds, aName, None, aFlags, aParameters)
#
#class State(object):
#	__slots__ = ["starts", "ends", "functions"]
#	def __init__(self, aStarts, aEnds, aFunctions):
#		self.starts = aStarts # Integer
#		self.ends = aEnds # Integer
#		self.functions = aFunctions # Dict of Function/Event instances
