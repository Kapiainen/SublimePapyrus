import os, re, sys, collections

# General #########################################################################################
class SharedResources(object):
	def __init__(self):
		self.CMP_EQUAL = "CMP_EQUAL"
		self.CMP_GREATER_THAN = "CMP_GREATER_THAN"
		self.CMP_GREATER_THAN_OR_EQUAL = "CMP_GREATER_THAN_OR_EQUAL"
		self.CMP_LESS_THAN = "CMP_LESS_THAN"
		self.CMP_LESS_THAN_OR_EQUAL = "CMP_LESS_THAN_OR_EQUAL"
		self.CMP_NOT_EQUAL = "CMP_NOT_EQUAL"

		self.BOOL = "BOOL"
		self.COMMA = "COMMA"
		self.COMMENT_BLOCK = "COMMENT_BLOCK"
		self.COMMENT_LINE = "COMMENT_LINE"
		self.DOCUMENTATION_STRING = "DOCUMENTATION_STRING"
		self.FLOAT = "FLOAT"
		self.IDENTIFIER = "IDENTIFIER"
		self.INT = "INT"
		self.LEFT_BRACKET = "LEFT_BRACKET"
		self.LEFT_PARENTHESIS = "LEFT_PARENTHESIS"
		self.MULTILINE = "MULTILINE"
		self.NEWLINE = "NEWLINE"
		self.RIGHT_BRACKET = "RIGHT_BRACKET"
		self.RIGHT_PARENTHESIS = "RIGHT_PARENTHESIS"
		self.STRING = "STRING"
		self.UNMATCHED = "UNMATCHED"
		self.WHITESPACE = "WHITESPACE"

		self.LOG_AND = "LOG_AND"
		self.LOG_NOT = "LOG_NOT"
		self.LOG_OR = "LOG_OR"

		self.OP_ADDITION = "OP_ADDITION"
		self.OP_ADDITION_ASSIGN = "OP_ADDITION_ASSIGN"
		self.OP_ASSIGN = "OP_ASSIGN"
		self.OP_DIVISION = "OP_DIVISION"
		self.OP_DIVISION_ASSIGN = "OP_DIVISION_ASSIGN"
		self.OP_DOT = "OP_DOT"
		self.OP_MODULUS = "OP_MODULUS"
		self.OP_MODULUS_ASSIGN = "OP_MODULUS_ASSIGN"
		self.OP_MULTIPLICATION = "OP_MULTIPLICATION"
		self.OP_MULTIPLICATION_ASSIGN = "OP_MULTIPLICATION_ASSIGN"
		self.OP_SUBTRACTION = "OP_SUBTRACTION"
		self.OP_SUBTRACTION_ASSIGN = "OP_SUBTRACTION_ASSIGN"

		self.KW_AS = "AS"
		self.KW_AUTO = "AUTO"
		self.KW_AUTOREADONLY = "AUTOREADONLY"
		self.KW_BOOL = "BOOL"
		self.KW_CONDITIONAL = "CONDITIONAL"
		self.KW_ELSE = "ELSE"
		self.KW_ELSEIF = "ELSEIF"
		self.KW_ENDEVENT = "ENDEVENT"
		self.KW_ENDFUNCTION = "ENDFUNCTION"
		self.KW_ENDIF = "ENDIF"
		self.KW_ENDPROPERTY = "ENDPROPERTY"
		self.KW_ENDSTATE = "ENDSTATE"
		self.KW_ENDWHILE = "ENDWHILE"
		self.KW_EVENT = "EVENT"
		self.KW_EXTENDS = "EXTENDS"
		self.KW_FALSE = "FALSE"
		self.KW_FLOAT = "FLOAT"
		self.KW_FUNCTION = "FUNCTION"
		self.KW_GLOBAL = "GLOBAL"
		self.KW_HIDDEN = "HIDDEN"
		self.KW_IF = "IF"
		self.KW_IMPORT = "IMPORT"
		self.KW_INT = "INT"
		self.KW_LENGTH = "LENGTH"
		self.KW_NATIVE = "NATIVE"
		self.KW_NEW = "NEW"
		self.KW_NONE = "NONE"
		self.KW_PARENT = "PARENT"
		self.KW_PROPERTY = "PROPERTY"
		self.KW_RETURN = "RETURN"
		self.KW_SCRIPTNAME = "SCRIPTNAME"
		self.KW_SELF = "SELF"
		self.KW_STATE = "STATE"
		self.KW_STRING = "STRING"
		self.KW_TRUE = "TRUE"
		self.KW_WHILE = "WHILE"

		self.STAT_PARAMETER = "STAT_PARAMETER"
		self.STAT_ASSIGNMENT = "STAT_ASSIGNMENT"
		self.STAT_DOCUMENTATION = "STAT_DOCUMENTATION"
		self.STAT_ELSEIF = "STAT_ELSEIF"
		self.STAT_KEYWORD = "STAT_KEYWORD"
		self.STAT_EVENTDEF = "STAT_EVENTDEF"
		self.STAT_EXPRESSION = "STAT_EXPRESSION"
		self.STAT_FUNCTIONDEF = "STAT_FUNCTIONDEF"
		self.STAT_IF = "STAT_IF"
		self.STAT_IMPORT = "STAT_IMPORT"
		self.STAT_PROPERTYDEF = "STAT_PROPERTYDEF"
		self.STAT_RETURN = "STAT_RETURN"
		self.STAT_SCRIPTHEADER = "STAT_SCRIPTHEADER"
		self.STAT_STATEDEF = "STAT_STATEDEF"
		self.STAT_VARIABLEDEF = "STAT_VARIABLEDEF"
		self.STAT_WHILE = "STAT_WHILE"

		self.NODE_EXPRESSION = "NODE_EXPRESSION"
		self.NODE_ARRAYATOM = "NODE_ARRAYATOM"
		self.NODE_ARRAYFUNCORID = "NODE_ARRAYFUNCORID"
		self.NODE_CONSTANT = "NODE_CONSTANT"
		self.NODE_FUNCTIONCALL = "NODE_FUNCTIONCALL"
		self.NODE_FUNCTIONCALLARGUMENT = "NODE_FUNCTIONCALLARGUMENT"
		self.NODE_IDENTIFIER = "NODE_IDENTIFIER"
		self.NODE_LENGTH = "NODE_LENGTH"
		self.NODE_ARRAYCREATION = "NODE_ARRAYCREATION"
		self.NODE_BINARYOPERATOR = "NODE_BINARYOPERATOR"
		self.NODE_UNARYOPERATOR = "NODE_UNARYOPERATOR"

		self.DEFINITION_PROPERTY = "DEFINITION_PROPERTY"
		self.DEFINITION_FUNCTION = "DEFINITION_FUNCTION"
		self.DEFINITION_EVENT = "DEFINITION_EVENT"
		self.DEFINITION_STATE = "DEFINITION_STATE"

# Lexical analysis ################################################################################
class Token(object):
	__slots__ = ["type", "value", "line", "column"]
	def __init__(self, aType, aValue, aLine, aColumn):
		self.type = aType
		self.value = aValue
		self.line = aLine
		self.column = aColumn

class LexicalError(Exception):
	def __init__(self, message, line, column):
		super(LexicalError, self).__init__(message)
		self.message = message
		self.line = line
		self.column = column

class Lexical(SharedResources):
	def __init__(self):
		super(Lexical, self).__init__()
		self.token_specs = self.GetTokenSpecifications()
		self.keywords = self.GetKeywords()
		self.regex = None

	def Abort(self, message, line, column):
		raise LexicalError(message, line, column)

	def GetTokenSpecifications(self):
		return [
			(self.COMMENT_BLOCK, r";/[\S\s]*?(?=/;)/;"),
			(self.COMMENT_LINE, r";[^\n]*"),
			(self.DOCUMENTATION_STRING, r"{[\S\s]*?(?=})}"),
			(self.LEFT_PARENTHESIS, r"\("),
			(self.RIGHT_PARENTHESIS, r"\)"),
			(self.LEFT_BRACKET, r"\["),
			(self.RIGHT_BRACKET, r"\]"),
			(self.MULTILINE, r"\\[^\n]*?(?=\n)\n"),
			(self.COMMA, r","),
			(self.OP_DOT, r"\."),
			(self.CMP_EQUAL, r"=="),
			(self.CMP_NOT_EQUAL, r"!="),
			(self.CMP_GREATER_THAN_OR_EQUAL, r">="),
			(self.CMP_LESS_THAN_OR_EQUAL, r"<="),
			(self.CMP_GREATER_THAN, r">"),
			(self.CMP_LESS_THAN, r"<"),
			(self.LOG_NOT, r"!"),
			(self.LOG_AND, r"&&"),
			(self.LOG_OR, r"\|\|"),
			(self.OP_ADDITION_ASSIGN, r"\+="),
			(self.OP_SUBTRACTION_ASSIGN, r"-="),
			(self.OP_MULTIPLICATION_ASSIGN, r"\*="),
			(self.OP_DIVISION_ASSIGN, r"/="),
			(self.OP_MODULUS_ASSIGN, r"%="),
			(self.OP_ASSIGN, r"="),
			(self.BOOL, r"(true|false)"),
			(self.IDENTIFIER, r"[a-z_][0-9a-z_]*"),
			(self.FLOAT, r"(-\d+\.\d+)|(\d+\.\d+)"),
			(self.INT, r"((0x(\d|[a-f])+)|((\d+))(?![a-z_]))"),
			(self.OP_ADDITION, r"\+"),
			(self.OP_SUBTRACTION, r"-"),
			(self.OP_MULTIPLICATION, r"\*"),
			(self.OP_DIVISION, r"/"),
			(self.OP_MODULUS, r"%"),
			(self.STRING, r"\".*?(?:(?<=\\\\)\"|(?<!\\)\")"),
			(self.NEWLINE, r"[\n\r]"),
			(self.WHITESPACE, r"[ \t]"),
			(self.UNMATCHED, r"."),
		]

	def GetKeywords(self):
		return [
			"AS",
			"AUTO",
			"AUTOREADONLY",
			"BOOL",
			"CONDITIONAL",
			"ELSE",
			"ELSEIF",
			"ENDEVENT",
			"ENDFUNCTION",
			"ENDIF",
			"ENDPROPERTY",
			"ENDSTATE",
			"ENDWHILE",
			"EVENT",
			"EXTENDS",
			"FALSE",
			"FLOAT",
			"FUNCTION",
			"GLOBAL",
			"HIDDEN",
			"IF",
			"IMPORT",
			"INT",
			"LENGTH",
			"NATIVE",
			"NEW",
			"NONE",
			"PARENT",
			"PROPERTY",
			"RETURN",
			"SELF",
			"SCRIPTNAME",
			"STATE",
			"STRING",
			"TRUE",
			"WHILE",
		]

	def Process(self, asString): # Takes a string and yields tokens.
		if not self.regex: # If total regex pattern has not been compiled yet, then do so now.
			temp = "|".join("(?P<%s>%s)" % pair for pair in self.token_specs)
			self.regex = re.compile(temp, re.IGNORECASE)
		tokens = []
		line = 1
		column = -1
		skip = [False, ""]
		multiline = 0
		for match in self.regex.finditer(asString):
			t = match.lastgroup
			v = match.group(t)
			if t == self.WHITESPACE:
				continue
			elif t == self.COMMENT_LINE:
				continue
			elif t == self.COMMENT_BLOCK:
				i = v.count("\n")
				line += i
				column = match.end()-1
				continue
			elif t == self.MULTILINE:
				multiline += 1
				continue
			if t == self.IDENTIFIER:
				temp = v.upper()
				if temp in self.keywords:
					t = temp
			elif t == self.DOCUMENTATION_STRING:
				i = v.count("\n")
				line += i
				v = v[1:-1]
				column = match.end()-1
			elif t == self.UNMATCHED:
				self.Abort("Encountered an unexpected '%s' character." % v, line, match.start()-column)
			yield Token(t, v, line, match.start()-column)
			line += multiline
			multiline = 0
			if t == self.NEWLINE:
				line += 1
				column = match.end()-1
		yield Token(self.NEWLINE, "\n", line, 1)

# Syntactic analysis ##############################################################################
class Statement(object):
	__slots__ = ["type", "line", "data"]
	def __init__(self, aType, aLine, aData):
		self.type = aType
		self.line = aLine
		self.data = aData

class Keyword(object):
	__slots__ = ["type"]
	def __init__(self, aType):
		self.type = aType

class Scriptheader(object):
	__slots__ = ["name", "parent", "flags"]
	def __init__(self, aName, aParent, aFlags):
		self.name = aName
		self.parent = aParent
		self.flags = aFlags

class Import(object):
	__slots__ = ["name"]
	def __init__(self, aName):
		self.name = aName

class FunctionDef(object):
	__slots__ = ["type", "typeIdentifier", "array", "name", "identifier", "parameters", "flags"]
	def __init__(self, aType, aTypeIdentifier, aArray, aName, aIdentifier, aParameters, aFlags):
		self.type = aType
		self.typeIdentifier = aTypeIdentifier
		self.array = aArray
		self.name = aName
		self.identifier = aIdentifier
		self.parameters = aParameters
		self.flags = aFlags

class EventDef(object):
	__slots__ = ["type", "name", "identifier", "parameters", "flags"]
	def __init__(self, aType, aName, aIdentifier, aParameters, aFlags):
		self.type = aType
		self.name = aName
		self.identifier = aIdentifier
		self.parameters = aParameters
		self.flags = aFlags

class ParameterDef(object):
	__slots__ = ["type", "typeIdentifier", "array", "name", "identifier", "expression"]
	def __init__(self, aType, aTypeIdentifier, aArray, aName, aIdentifier, aExpression):
		self.type = aType
		self.typeIdentifier = aTypeIdentifier
		self.array = aArray
		self.name = aName
		self.identifier = aIdentifier
		self.expression = aExpression

class If(object):
	__slots__ = ["expression"]
	def __init__(self, aExpression):
		self.expression = aExpression

class ElseIf(object):
	__slots__ = ["expression"]
	def __init__(self, aExpression):
		self.expression = aExpression

class While(object):
	__slots__ = ["expression"]
	def __init__(self, aExpression):
		self.expression = aExpression

class VariableDef(object):
	__slots__ = ["type", "typeIdentifier", "array", "name", "identifier", "value", "flags"]
	def __init__(self, aType, aTypeIdentifier, aArray, aName, aIdentifier, aValue, aFlags):
		self.type = aType
		self.typeIdentifier = aTypeIdentifier
		self.array = aArray
		self.name = aName
		self.identifier = aIdentifier
		self.value = aValue
		self.flags = aFlags

class PropertyDef(object):
	__slots__ = ["type", "typeIdentifier", "array", "name", "identifier", "value", "flags"]
	def __init__(self, aType, aTypeIdentifier, aArray, aName, aIdentifier, aValue, aFlags):
		self.type = aType
		self.typeIdentifier = aTypeIdentifier
		self.array = aArray
		self.name = aName
		self.identifier = aIdentifier
		self.value = aValue
		self.flags = aFlags

class Return(object):
	__slots__ = ["expression"]
	def __init__(self, aExpression):
		self.expression = aExpression

class Documentation(object):
	__slots__ = ["value"]
	def __init__(self, aValue):
		self.value = aValue

class StateDef(object):
	__slots__ = ["name", "auto"]
	def __init__(self, aName, aAuto):
		self.name = aName
		self.auto = aAuto

class Expression(object):
	__slots__ = ["expression"]
	def __init__(self, aExpression):
		self.expression = aExpression

class Assignment(object):
	__slots__ = ["operator", "leftExpression", "rightExpression"]
	def __init__(self, aOperator, aLeftExpression, aRightExpression):
		self.operator = aOperator
		self.leftExpression = aLeftExpression
		self.rightExpression = aRightExpression

# Abstract syntax tree node types
class Node(object):
	__slots__ = ["type", "data"]
	def __init__(self, aType, aData):
		self.type = aType
		self.data = aData

class BinaryOperatorNode(object):
	__slots__ = ["operator", "leftOperand", "rightOperand"]
	def __init__(self, aOperator, aLeftOperand, aRightOperand):
		self.operator = aOperator
		self.leftOperand = aLeftOperand
		self.rightOperand = aRightOperand

class UnaryOperatorNode(object):
	__slots__ = ["operator", "operand"]
	def __init__(self, aOperator, aOperand):
		self.operator = aOperator
		self.operand = aOperand

class ExpressionNode(object):
	__slots__ = ["child"]
	def __init__(self, aChild):
		self.child = aChild

class ArrayAtomNode(object):
	__slots__ = ["child", "expression"]
	def __init__(self, aChild, aExpression):
		self.child = aChild
		self.expression = aExpression

class ArrayFuncOrIdNode(object):
	__slots__ = ["child", "expression"]
	def __init__(self, aChild, aExpression):
		self.child = aChild
		self.expression = aExpression

class ConstantNode(object):
	__slots__ = ["token"]
	def __init__(self, aToken):
		self.token = aToken

class FunctionCallNode(object):
	__slots__ = ["name", "arguments"]
	def __init__(self, aName, aArguments):
		self.name = aName
		self.arguments = aArguments

class FunctionCallArgument(object):
	__slots__ = ["name", "expression"]
	def __init__(self, aName, aExpression):
		self.name = aName
		self.expression = aExpression

class IdentifierNode(object):
	__slots__ = ["token"]
	def __init__(self, aToken):
		self.token = aToken

class LengthNode(object):
	__slots__ = []

class ArrayCreationNode(object):
	__slots__ = ["typeToken", "sizeToken"]
	def __init__(self, aTypeToken, aSizeToken):
		self.typeToken = aTypeToken
		self.sizeToken = aSizeToken

class SyntacticError(Exception):
	def __init__(self, line, message):
		super(SyntacticError, self).__init__(message)
		self.message = message
		self.line = line
		
class ExpectedTypeError(SyntacticError):
	def __init__(self, line, baseTypes, message = ""):
		if baseTypes:
			super(ExpectedTypeError, self).__init__(line, ("%s %s" % (message, "Expected a type identifier.")).strip())
		else:
			super(ExpectedTypeError, self).__init__(line, ("%s %s" % (message, "Expected a non-base type identifier.")).strip())
		self.baseTypes = baseTypes

class ExpectedExpressionError(SyntacticError):
	def __init__(self, line, message = ""):
		super(ExpectedExpressionError, self).__init__(line, ("%s %s" % (message, "Expected an expression.")).strip())

class ExpectedIdentifierError(SyntacticError):
	def __init__(self, line, message = ""):
		super(ExpectedIdentifierError, self).__init__(line, ("%s%s" % (message, "Expected an identifier.")).strip())

class ExpectedLiteralError(SyntacticError):
	def __init__(self, line, message = ""):
		super(ExpectedLiteralError, self).__init__(line, ("%s %s" % (message, "Expected a literal.")).strip())

class ExpectedOperatorError(SyntacticError):
	def __init__(self, line, message = ""):
		super(ExpectedOperatorError, self).__init__(line, ("%s %s" % (message, "Expected an operator.")).strip())

class ExpectedKeywordError(SyntacticError):
	def __init__(self, line, message):
		super(ExpectedKeywordError, self).__init__(line, message)

class Syntactic(SharedResources):
	def __init__(self):
		super(Syntactic, self).__init__()

	def Abort(self, message = None):
		if self.token:
			raise SyntacticError(self.token.line, message)
		else:
			raise SyntacticError(self.GetPreviousLine(), message)

	def Process(self, tokens):
		if tokens:
			self.keywordstat = lambda x: Statement(self.STAT_KEYWORD, x, Keyword(self.GetPreviousType()))
			self.stack = []
			self.tokens = tokens
			self.token_index = 0
			self.stat = None
			self.token = self.tokens[0]
			self.token_count = len(self.tokens)
			if self.Statement() >= 0:
				return self.stat
		return None

	def Consume(self):
		self.token_index = self.token_index + 1
		if self.token_index < self.token_count:
			self.token = self.tokens[self.token_index]
			return True
		else:
			self.token = None
			return False

	def Accept(self, asType):
		if self.token != None and asType == self.token.type:
			self.Consume()
			return True
		else:
			return False

	def Peek(self, amount = 1):
		if self.token_index+amount < self.token_count:
			return self.tokens[self.token_index+amount]
		else:
			return None

	def Expect(self, asType):
		if self.Accept(asType):
			return True
		else:
			if self.token != None:
				raise SyntacticError(self.token.line, "Unexpected symbol '%s' ('%s') on column %d. Expected '%s'." % (self.token.type, self.token.value, self.token.column, asType))
			else:
				raise SyntacticError(self.GetPreviousLine(), "Expected symbol '%s'." % (asType))

	def TokensRemaining(self):
		return self.token_index < self.token_count

	def GetIndex(self):
		return self.token_index

	def GetPreviousToken(self):
		if self.token_index > 0:
			return self.tokens[self.token_index-1]

	def GetPreviousType(self):
		if self.token_index > 0:
			return self.tokens[self.token_index-1].type

	def GetPreviousValue(self):
		if self.token_index > 0:
			return self.tokens[self.token_index-1].value

	def GetPreviousLine(self):
		if self.token_index > 0:
			return self.tokens[self.token_index-1].line

	def GetPreviousColumn(self):
		if self.token_index > 0:
			return self.tokens[self.token_index-1].column

	def GoTo(self, aiIndex):
		self.token_index = aiIndex - 1
		if self.token_index < -1:
			self.token = None
		else:
			self.Consume()

	def Attempt(self, func, args = None):
		start = self.GetIndex()
		if args:
			if func(args):
				return True
			else:
				self.GoTo(start)
				return False
		else:
			if func():
				return True
			else:
				self.GoTo(start)
				return False

	def AcceptType(self, baseTypes):
		if self.Accept(self.IDENTIFIER):
			return True
		elif baseTypes and (self.Accept(self.KW_BOOL) or self.Accept(self.KW_FLOAT) or self.Accept(self.KW_INT) or self.Accept(self.KW_STRING)):
			return True
		else:
			return False

	def ExpectType(self, baseTypes):
		if self.AcceptType(baseTypes):
			return True
		else:
			if self.token != None:
				message = "Unexpected symbol '%s' ('%s') on column %d." % (self.token.type, self.token.value, self.token.column)
				if baseTypes:
					raise ExpectedTypeError(self.GetPreviousLine(), True, message)
				else:
					raise ExpectedTypeError(self.GetPreviousLine(), False, message)
			else:
				if baseTypes:
					raise ExpectedTypeError(self.GetPreviousLine(), True)
				else:
					raise ExpectedTypeError(self.GetPreviousLine(), False)

	def AcceptLiteral(self):
		if self.Accept(self.BOOL) or self.Accept(self.FLOAT) or self.Accept(self.INT) or self.Accept(self.STRING) or self.Accept(self.KW_NONE):
			return True
		elif self.Accept(self.OP_SUBTRACTION) and (self.Accept(self.INT) or self.Accept(self.FLOAT)):
			return True
		else:
			return False

	def ExpectLiteral(self):
		if self.AcceptLiteral():
			return True
		else:
			if self.token != None:
				raise ExpectedLiteralError(self.token.line, "Unexpected symbol '%s' ('%s') on column %d." % (self.token.type, self.token.value, self.token.column))
			else:
				raise ExpectedLiteralError(self.GetPreviousLine())

	def AcceptComparison(self):
		if self.Accept(self.CMP_EQUAL) or self.Accept(self.CMP_NOT_EQUAL) or self.Accept(self.CMP_GREATER_THAN_OR_EQUAL) or self.Accept(self.CMP_LESS_THAN_OR_EQUAL) or self.Accept(self.CMP_GREATER_THAN) or self.Accept(self.CMP_LESS_THAN):
			return True
		else:
			return False

	def ExpectComparison(self):
		if self.AcceptComparison():
			return True
		else:
			if self.token != None:
				raise ExpectedOperatorError(self.token.line, "Unexpected symbol '%s' ('%s') on column %d. Expected a comparison operator." % (self.token.type, self.token.value, self.token.column))
			else:
				raise ExpectedOperatorError(self.GetPreviousLine(), "Expected a comparison operator.")

	def AcceptAssignment(self):
		if self.Accept(self.OP_ASSIGN) or self.Accept(self.OP_ADDITION_ASSIGN) or self.Accept(self.OP_SUBTRACTION_ASSIGN) or self.Accept(self.OP_MULTIPLICATION_ASSIGN) or self.Accept(self.OP_DIVISION_ASSIGN) or self.Accept(self.OP_MODULUS_ASSIGN):
			return True
		else:
			return False

	def ExpectAssignment(self):
		if self.AcceptAssignment():
			return True
		else:
			if self.token != None:
				raise ExpectedOperatorError(self.token.line, "Unexpected symbol '%s' ('%s') on column %d. Expected an assignment operator." % (self.token.type, self.token.value, self.token.column))
			else:
				raise ExpectedOperatorError(self.GetPreviousLine(), "Expected an assignment operator.")

	def AcceptIdentifier(self):
		if self.Accept(self.IDENTIFIER) or self.Accept(self.KW_SELF) or self.Accept(self.KW_PARENT):
			return True
		else:
			return False

	def ExpectIdentifier(self):
		if self.AcceptIdentifier():
			return True
		else:
			if self.token != None:
				raise ExpectedIdentifierError(self.token.line, "Unexpected symbol '%s' ('%s') on column %d." % (self.token.type, self.token.value, self.token.column))
			else:
				raise ExpectedIdentifierError(self.GetPreviousLine())

	def Statement(self):
		line = -1
		if self.token:
			line = self.token.line
		if self.token.type == self.KW_IF:
			self.If()
		elif self.token.type == self.KW_ELSEIF:
			self.ElseIf()
		elif self.token.type == self.KW_ELSE:
			self.Accept(self.KW_ELSE)
			self.stat = self.keywordstat(line)
		elif self.token.type == self.KW_ENDIF:
			self.Accept(self.KW_ENDIF)
			self.stat = self.keywordstat(line)
		elif self.token.type == self.KW_WHILE:
			self.While()
		elif self.token.type == self.KW_ENDWHILE:
			self.Accept(self.KW_ENDWHILE)
			self.stat = self.keywordstat(line)
		elif self.token.type == self.IDENTIFIER or self.token.type == self.KW_BOOL or self.token.type == self.KW_FLOAT or self.token.type == self.KW_INT or self.token.type == self.KW_STRING:
			nextToken = self.Peek()
			if nextToken and nextToken.type == self.LEFT_BRACKET:
				nextToken = self.Peek(2)
				if nextToken and nextToken.type == self.RIGHT_BRACKET:
					nextToken = self.Peek(3)
					if not nextToken:
						self.Abort("Expected FUNCTION, PROPERTY, or an identifier.")
					if nextToken.type == self.KW_FUNCTION:
						self.FunctionDef()
					elif nextToken.type == self.KW_PROPERTY:
						self.PropertyDef()
					elif nextToken.type == self.IDENTIFIER:
						self.VariableDef()
					else:
						self.ExpressionOrAssignment()
				else:
					self.ExpressionOrAssignment()
			elif nextToken:
				if nextToken.type == self.KW_FUNCTION:
					self.FunctionDef()
				elif nextToken.type == self.KW_PROPERTY:
					self.PropertyDef()
				elif nextToken.type == self.IDENTIFIER:
					self.VariableDef()
				else:
					self.ExpressionOrAssignment()
			else:
				self.ExpressionOrAssignment()
		elif self.token.type == self.KW_FUNCTION:
			self.FunctionDef()
		elif self.token.type == self.KW_RETURN:
			self.Return()
		elif self.token.type == self.KW_IMPORT:
			self.Import()
		elif self.token.type == self.KW_ENDFUNCTION:
			self.Accept(self.KW_ENDFUNCTION)
			self.stat = self.keywordstat(line)
		elif self.token.type == self.KW_EVENT:
			self.EventDef()
		elif self.token.type == self.KW_ENDEVENT:
			self.Accept(self.KW_ENDEVENT)
			self.stat = self.keywordstat(line)
		elif self.token.type == self.KW_ENDPROPERTY:
			self.Accept(self.KW_ENDPROPERTY)
			self.stat = self.keywordstat(line)
		elif self.token.type == self.DOCUMENTATION_STRING:
			self.Accept(self.DOCUMENTATION_STRING)
			self.stat = Statement(self.STAT_DOCUMENTATION, line, Documentation(self.GetPreviousValue()))
		elif self.token.type == self.KW_STATE or (self.token.type == self.KW_AUTO and self.Peek().type == self.KW_STATE):
			self.State()
		elif self.token.type == self.KW_ENDSTATE:
			self.Accept(self.KW_ENDSTATE)
			self.stat = self.keywordstat(line)
		elif self.token.type == self.KW_SCRIPTNAME:
			self.ScriptHeader()
		elif self.ExpressionOrAssignment():
			pass
		if self.Accept(self.NEWLINE): # End of line
			return 1
		else:
			if self.token == None: # End of script
				return 0
			else: # Non-consumed token
				self.Abort("Unexpected %s symbol ('%s') on column %d." % (self.token.type, self.token.value, self.token.column))
				return -1

	def ExpressionOrAssignment(self):
		self.Expression()
		left = self.Pop()
		if self.AcceptAssignment():
			operator = self.GetPreviousToken()
			self.Expression()
			right = self.Pop()
			self.stat = Statement(self.STAT_ASSIGNMENT, self.GetPreviousLine(), Assignment(operator, left, right))
			return True
		elif self.token == None:
			self.stat = Statement(self.STAT_EXPRESSION, self.GetPreviousLine(), Expression(left))
			return True

	def State(self):
		if self.Accept(self.KW_AUTO):
			self.Expect(self.KW_STATE)
			self.Expect(self.IDENTIFIER)
			self.stat = Statement(self.STAT_STATEDEF, self.GetPreviousLine(), StateDef(self.GetPreviousValue(), True))
			return True
		elif self.Accept(self.KW_STATE):
			self.Expect(self.IDENTIFIER)
			self.stat = Statement(self.STAT_STATEDEF, self.GetPreviousLine(), StateDef(self.GetPreviousValue(), False))
			return True

	def While(self):
		if self.Accept(self.KW_WHILE):
			self.Expression()
			self.stat = Statement(self.STAT_WHILE, self.GetPreviousLine(), While(self.Pop()))
			return True

	def PropertyDef(self):
		self.ExpectType(True)
		line = self.GetPreviousLine()
		typ = None
		if self.GetPreviousType() == self.IDENTIFIER:
			typ = self.GetPreviousValue()
		else:
			typ = self.GetPreviousType()
		array = False
		if self.Accept(self.LEFT_BRACKET):
			self.Expect(self.RIGHT_BRACKET)
			array = True
		self.Expect(self.KW_PROPERTY)
		self.Expect(self.IDENTIFIER)
		name = self.GetPreviousValue()
		value = None
		flags = []
		if self.Accept(self.OP_ASSIGN):
			self.ExpectLiteral()
			value = self.GetPreviousToken()
			if self.Accept(self.KW_AUTO):
				flags.append(self.GetPreviousType())
				if self.Accept(self.KW_HIDDEN):
					flags.append(self.GetPreviousType())
					if self.Accept(self.KW_CONDITIONAL):
						flags.append(self.GetPreviousType())
				elif self.Accept(self.KW_CONDITIONAL):
					flags.append(self.GetPreviousType())
					if self.Accept(self.KW_HIDDEN):
						flags.append(self.GetPreviousType())
			elif self.Accept(self.KW_AUTOREADONLY):
				flags.append(self.GetPreviousType())
				if self.Accept(self.KW_HIDDEN):
					flags.append(self.GetPreviousType())
					if self.Accept(self.KW_CONDITIONAL):
						flags.append(self.GetPreviousType())
				elif self.Accept(self.KW_CONDITIONAL):
					flags.append(self.GetPreviousType())
					if self.Accept(self.KW_HIDDEN):
						flags.append(self.GetPreviousType())
			else:
				raise ExpectedKeywordError(line, "Initializing properties requires the AUTO or AUTOREADONLY keywords.")
		else:
			if self.Accept(self.KW_AUTO) or self.Accept(self.KW_AUTOREADONLY):
				flags.append(self.GetPreviousType())
				if self.Accept(self.KW_HIDDEN):
					flags.append(self.GetPreviousType())
					if self.Accept(self.KW_CONDITIONAL):
						flags.append(self.GetPreviousType())
				elif self.Accept(self.KW_CONDITIONAL):
					flags.append(self.GetPreviousType())
					if self.Accept(self.KW_HIDDEN):
						flags.append(self.GetPreviousType())
			else:
				if self.Accept(self.KW_HIDDEN):
					flags.append(self.GetPreviousType())
		self.stat = Statement(self.STAT_PROPERTYDEF, line, PropertyDef(typ.upper(), typ, array, name.upper(), name, value, flags))
		return True

	def Return(self):
		if self.Accept(self.KW_RETURN):
			if self.TokensRemaining():
				self.Expression()
				self.stat = Statement(self.STAT_RETURN, self.GetPreviousLine(), Return(self.Pop()))
				return True
			else:
				self.stat = Statement(self.STAT_RETURN, self.GetPreviousLine(), Return(None))
				return True

	def VariableDef(self):
		self.ExpectType(True)
		line = self.GetPreviousLine()
		typ = None
		if self.GetPreviousType() == self.IDENTIFIER:
			typ = self.GetPreviousValue()
		else:
			typ = self.GetPreviousType()
		array = False
		if self.Accept(self.LEFT_BRACKET):
			self.Expect(self.RIGHT_BRACKET)
			array = True
		self.Expect(self.IDENTIFIER)
		name = self.GetPreviousValue()
		value = None
		if self.Accept(self.OP_ASSIGN):
			self.Expression()
			value = self.Pop()
		flags = []
		if self.Accept(self.KW_CONDITIONAL):
			flags.append(self.GetPreviousType())
		self.stat = Statement(self.STAT_VARIABLEDEF, line, VariableDef(typ.upper(), typ, array, name.upper(), name, value, flags))
		return True

	def ScriptHeader(self):
		self.Expect(self.KW_SCRIPTNAME)
		line = self.GetPreviousLine()
		self.Expect(self.IDENTIFIER)
		name = self.GetPreviousValue()
		parent = None
		if self.Accept(self.KW_EXTENDS):
			self.ExpectType(False)
			parent = self.GetPreviousValue()
		flags = []
		if self.Accept(self.KW_CONDITIONAL):
			flags.append(self.GetPreviousType())
			if self.Accept(self.KW_HIDDEN):
				flags.append(self.GetPreviousType())
		elif self.Accept(self.KW_HIDDEN):
			flags.append(self.GetPreviousType())
			if self.Accept(self.KW_CONDITIONAL):
				flags.append(self.GetPreviousType())
		if parent:
			self.stat = Statement(self.STAT_SCRIPTHEADER, line, Scriptheader(name.upper(), parent.upper(), flags))
		else:
			self.stat = Statement(self.STAT_SCRIPTHEADER, line, Scriptheader(name.upper(), None, flags))
		return True

	def FunctionDef(self):
		params = []

		def Parameter():
			self.ExpectType(True)
			typ = self.GetPreviousValue()
			array = False
			if self.Accept(self.LEFT_BRACKET):
				self.Expect(self.RIGHT_BRACKET)
				array = True
			self.Expect(self.IDENTIFIER)
			name = self.GetPreviousValue()
			value = None
			if self.Accept(self.OP_ASSIGN):
				defaultValues = True
				if not self.Expression():
					self.Abort("Expected an expression.")
					return False
				value = self.Pop()
			params.append(ParameterDef(typ.upper(), typ, array, name.upper(), name, value))
			return True

		typ = None
		array = False
		if self.AcceptType(True):
			typ = self.GetPreviousValue()
			if self.Accept(self.LEFT_BRACKET):
				self.Expect(self.RIGHT_BRACKET)
				array = True
		self.Expect(self.KW_FUNCTION)
		line = self.GetPreviousLine()
		self.Expect(self.IDENTIFIER)
		name = self.GetPreviousValue()
		nextToken = self.Peek()
		self.Expect(self.LEFT_PARENTHESIS)
		if nextToken and nextToken.type != self.RIGHT_PARENTHESIS:			
			Parameter()
			while self.Accept(self.COMMA):
				Parameter()
		self.Expect(self.RIGHT_PARENTHESIS)	
		flags = []
		if self.Accept(self.KW_GLOBAL):
			flags.append(self.GetPreviousType())
			if self.Accept(self.KW_NATIVE):
				flags.append(self.GetPreviousType())
		elif self.Accept(self.KW_NATIVE):
			flags.append(self.GetPreviousType())
			if self.Accept(self.KW_GLOBAL):
				flags.append(self.GetPreviousType())
		if typ:
			self.stat = Statement(self.STAT_FUNCTIONDEF, line, FunctionDef(typ.upper(), typ, array, name.upper(), name, params, flags))
		else:
			self.stat = Statement(self.STAT_FUNCTIONDEF, line, FunctionDef(None, None, False, name.upper(), name, params, flags))
		return True

	def EventDef(self):
		self.Expect(self.KW_EVENT)
		line = self.GetPreviousLine()
		params = []

		def Parameter():
			self.ExpectType(True)
			typ = self.GetPreviousValue()
			array = False
			if self.Accept(self.LEFT_BRACKET):
				self.Expect(self.RIGHT_BRACKET)
				array = True
			self.Expect(self.IDENTIFIER)
			name = self.GetPreviousValue()
			params.append(ParameterDef(typ.upper(), typ, array, name.upper(), name, None))
			return True

		self.Expect(self.IDENTIFIER)
		name = self.GetPreviousValue()
		nextToken = self.Peek()
		self.Expect(self.LEFT_PARENTHESIS)
		if nextToken and nextToken.type != self.RIGHT_PARENTHESIS:
			Parameter()
			while self.Accept(self.COMMA):
				Parameter()
		self.Expect(self.RIGHT_PARENTHESIS)
		flags = []
		if self.Accept(self.KW_NATIVE):
			flags.append(self.GetPreviousType())
		self.stat = Statement(self.STAT_EVENTDEF, line, EventDef(None, name.upper(), name, params, flags))
		return True

	def Import(self):
		self.Expect(self.KW_IMPORT)
		self.ExpectType(False)
		name = self.GetPreviousValue()
		self.stat = Statement(self.STAT_IMPORT, self.GetPreviousLine(), Import(name.upper()))
		return True

	def If(self):
		self.Expect(self.KW_IF)
		self.Expression()
		self.stat = Statement(self.STAT_IF, self.GetPreviousLine(), If(self.Pop()))
		return True

	def ElseIf(self):
		self.Expect(self.KW_ELSEIF)
		self.Expression()
		self.stat = Statement(self.STAT_ELSEIF, self.GetPreviousLine(), ElseIf(self.Pop()))
		return True

	def Shift(self, item = None):
		if item:
			self.stack.append(item)
		else:
			self.stack.append(self.GetPreviousToken())

	def Pop(self):
		if len(self.stack) > 0:
			return self.stack.pop()
		else:
			return None

	def ReduceBinaryOperator(self):
		operand2 = self.Pop()
		operator = self.Pop()
		operand1 = self.Pop()
		self.Shift(Node(self.NODE_BINARYOPERATOR, BinaryOperatorNode(operator, operand1, operand2)))

	def ReduceUnaryOperator(self):
		operand = self.Pop()
		operator = self.Pop()
		self.Shift(Node(self.NODE_UNARYOPERATOR, UnaryOperatorNode(operator, operand)))

	def Expression(self):
		def Reduce():
			self.Shift(Node(self.NODE_EXPRESSION, ExpressionNode(self.Pop())))

		self.AndExpression()
		while self.Accept(self.LOG_OR):
			self.Shift()
			self.AndExpression()
			self.ReduceBinaryOperator()
		Reduce()
		return True

	def AndExpression(self):
		self.BoolExpression()
		while self.Accept(self.LOG_AND):
			self.Shift()
			self.BoolExpression()
			self.ReduceBinaryOperator()
		return True

	def BoolExpression(self):
		self.AddExpression()
		while self.AcceptComparison():
			self.Shift()
			self.AddExpression()
			self.ReduceBinaryOperator()
		return True

	def AddExpression(self):
		self.MultExpression()
		while self.Accept(self.OP_ADDITION) or self.Accept(self.OP_SUBTRACTION):
			self.Shift()
			self.MultExpression()
			self.ReduceBinaryOperator()
		return True

	def MultExpression(self):
		self.UnaryExpression()
		while self.Accept(self.OP_MULTIPLICATION) or self.Accept(self.OP_DIVISION) or self.Accept(self.OP_MODULUS):
			self.Shift()
			self.UnaryExpression()
			self.ReduceBinaryOperator()
		return True

	def UnaryExpression(self):
		unaryOp = False
		if self.Accept(self.OP_SUBTRACTION) or self.Accept(self.LOG_NOT):
			self.Shift()
			unaryOp = True
		self.CastAtom()
		if unaryOp:
			self.ReduceUnaryOperator()
		return True

	def CastAtom(self):
		self.DotAtom()
		if self.Accept(self.KW_AS):
			self.Shift()
			self.ExpectType(True)
			self.Shift(Node(self.NODE_IDENTIFIER, IdentifierNode(self.GetPreviousToken())))
			self.ReduceBinaryOperator()
		return True

	def DotAtom(self):
		if self.AcceptLiteral():
			self.Shift(Node(self.NODE_CONSTANT, ConstantNode(self.GetPreviousToken())))
			return True
		elif self.ArrayAtom():
			while self.Accept(self.OP_DOT):
				self.Shift()
				self.ArrayFuncOrId()
				self.ReduceBinaryOperator()
			return True

	def ArrayAtom(self):
		def Reduce():
			temp = self.Pop()
			self.Shift(Node(self.NODE_ARRAYATOM, ArrayAtomNode(self.Pop(), temp)))

		self.Atom()
		if self.Accept(self.LEFT_BRACKET):
			self.Expression()
			self.Expect(self.RIGHT_BRACKET)
			Reduce()
		return True

	def Atom(self):
		if self.Accept(self.KW_NEW):
			self.ExpectType(True)
			typ = self.GetPreviousToken()
			self.Expect(self.LEFT_BRACKET)
			if not self.Accept(self.INT):
				self.Abort("Expected an int literal.")
			size = self.GetPreviousToken()
			self.Expect(self.RIGHT_BRACKET)
			self.Shift(Node(self.NODE_ARRAYCREATION, ArrayCreationNode(typ, size)))
			return True
		elif self.Accept(self.LEFT_PARENTHESIS):
			self.Expression()
			self.Expect(self.RIGHT_PARENTHESIS)
			return True
		elif self.FuncOrId():
			return True

	def ArrayFuncOrId(self):
		def Reduce():
			temp = self.Pop()
			self.Shift(Node(self.NODE_ARRAYFUNCORID, ArrayFuncOrIdNode(self.Pop(), temp)))

		self.FuncOrId()
		if self.Accept(self.LEFT_BRACKET):
			self.Expression()
			self.Expect(self.RIGHT_BRACKET)
			Reduce()
		return True

	def FuncOrId(self):
		nextToken = self.Peek()
		if nextToken and nextToken.type == self.LEFT_PARENTHESIS:
			self.FunctionCall()
			return True
		elif self.Accept(self.KW_LENGTH):
			self.Shift(Node(self.NODE_LENGTH, LengthNode()))
			return True
		elif self.ExpectIdentifier():
			self.Shift(Node(self.NODE_IDENTIFIER, IdentifierNode(self.GetPreviousToken())))
			return True

	def FunctionCall(self):
		def Reduce():
			arguments = []
			temp = self.Pop() # Right parenthesis
			temp = self.Pop()
			while temp.type == self.NODE_FUNCTIONCALLARGUMENT:
				arguments.insert(0, temp)
				temp = self.Pop()
			self.Shift(Node(self.NODE_FUNCTIONCALL, FunctionCallNode(self.Pop(), arguments)))

		def Argument():
			ident = None
			nextToken = self.Peek()
			if nextToken and nextToken.type == self.OP_ASSIGN:
				if self.Accept(self.IDENTIFIER):
					ident = self.GetPreviousToken()
					self.Accept(self.OP_ASSIGN)
					self.Expression()
					expr = self.Pop()
					self.Shift(Node(self.NODE_FUNCTIONCALLARGUMENT, FunctionCallArgument(ident, expr)))
					return True
				else:
					if self.token:
						raise ExpectedIdentifierError(self.token.line, "Unexpected %s symbol ('%s')." % (self.token.type, self.token.value))
					else:
						raise ExpectedIdentifierError(self.GetPreviousLine())
			else:
				self.Expression()
				expr = self.Pop()
				self.Shift(Node(self.NODE_FUNCTIONCALLARGUMENT, FunctionCallArgument(ident, expr)))
				return True

		self.Expect(self.IDENTIFIER)
		self.Shift()
		self.Expect(self.LEFT_PARENTHESIS)
		self.Shift()
		if self.Accept(self.RIGHT_PARENTHESIS):
			self.Shift()
			Reduce()
			return True
		else:
			Argument()
			while self.Accept(self.COMMA):
				Argument()
			self.Expect(self.RIGHT_PARENTHESIS)
			self.Shift()
			Reduce()
			return True

#class LimitedSyntactic(Syntactic): #TODO Remove
#	def Statement(self):
#		# Only interested in specific types of statements.
#		line = -1
#		if self.token:
#			line = self.token.line
#		if self.token.type == self.KW_SCRIPTNAME:
#			self.ScriptHeader()
#		elif self.token.type == self.KW_EVENT:
#			self.EventDef()
#		elif self.token.type == self.KW_ENDEVENT:
#			self.Accept(self.KW_ENDEVENT)
#			self.stat = self.keywordstat(line)
#		elif self.token.type == self.KW_FUNCTION:
#			self.FunctionDef()
#		elif self.token.type == self.KW_ENDFUNCTION:
#			self.Accept(self.KW_ENDFUNCTION)
#		elif self.token.type == self.KW_ENDPROPERTY:
#			self.Accept(self.KW_ENDPROPERTY)
#			self.stat = self.keywordstat(line)
#		elif self.token.type == self.IDENTIFIER or self.token.type == self.KW_BOOL or self.token.type == self.KW_FLOAT or self.token.type == self.KW_INT or self.token.type == self.KW_STRING:
#			nextToken = self.Peek()
#			if nextToken and nextToken.type == self.LEFT_BRACKET:
#				nextToken = self.Peek(2)
#				if nextToken and nextToken.type == self.RIGHT_BRACKET:
#					nextToken = self.Peek(3)
#					if not nextToken:
#						self.Abort("Expected FUNCTION, PROPERTY, or an identifier.")
#					if nextToken.type == self.KW_FUNCTION:
#						self.FunctionDef()
#					elif nextToken.type == self.KW_PROPERTY:
#						self.PropertyDef()
#			elif nextToken:
#				if nextToken.type == self.KW_FUNCTION:
#					self.FunctionDef()
#				elif nextToken.type == self.KW_PROPERTY:
#					self.PropertyDef()
#		elif self.token.type == self.KW_STATE or (self.token.type == self.KW_AUTO and self.Peek().type == self.KW_STATE):
#			self.State()
#		elif self.token.type == self.KW_ENDSTATE:
#			self.Accept(self.KW_ENDSTATE)
#			self.stat = self.keywordstat(line)
#		else:
#			return -1
#		return 0

# Semantic analysis ###############################################################################
class CachedScript(object):
	__slots__ = ["extends", "properties", "functions", "states"]
	def __init__(self, aExtends, aProperties, aFunctions, aStates):
		self.extends = aExtends
		self.properties = aProperties
		self.functions = aFunctions
		self.states = aStates

class SemanticError(Exception):
	def __init__(self, message, line):
		super(SemanticError, self).__init__(message)
		self.message = message
		self.line = line

class NodeResult(object):
	__slots__ = ["type", "array", "object"]
	def __init__(self, aType, aArray, aObject):
		self.type = aType.upper()
		self.array = aArray
		self.object = aObject

class EmptyStateCancel(SemanticError):
	def __init__(self, aFunctions):
		super(EmptyStateCancel, self).__init__(None, None)
		self.functions = aFunctions

class StateCancel(SemanticError):
	def __init__(self, aFunctions):
		super(StateCancel, self).__init__(None, None)
		self.functions = aFunctions

class FunctionDefinitionCancel(SemanticError):
	def __init__(self, aType, aFunctions, aVariables, aImports):
		super(FunctionDefinitionCancel, self).__init__(None, None)
		self.type = aType
		self.functions = aFunctions
		self.variables = aVariables
		self.imports = aImports

class PropertyDefinitionCancel(SemanticError):
	def __init__(self, aType, aArray, aFunctions):
		super(PropertyDefinitionCancel, self).__init__(None, None)
		self.type = aType
		self.array = aArray
		self.functions = aFunctions

class Semantic(SharedResources):
	def __init__(self):
		super(Semantic, self).__init__()
		self.cache = {}
		self.lex = Lexical()
		self.syn = Syntactic()

	def Abort(self, message = None, line = None):
		if not line:
			if self.statements and self.statements[0]:
				line = self.statements[0].line
		if not line:
			line = 1
		raise SemanticError(message, line)

#	def GetCachedKeys(self): #TODO Remove if unused
#		result = [key for key, name in self.cache.items()]
#		if result:
#			return result
#		else:
#			return None

	# Variables and properties
	def PushVariableScope(self):
		self.variables.append({})

	def PopVariableScope(self):
		if len(self.variables) > 2:
			self.variables.pop()
		else:
			self.Abort("Popping too many scopes from self.variables.")

	def AddVariable(self, stat):
		if stat.type == self.STAT_VARIABLEDEF or stat.type == self.STAT_PROPERTYDEF:
			temp = self.GetVariable(stat.data.name)
			if not temp:
				self.variables[len(self.variables)-1][stat.data.name] = stat
				if not self.CacheScript(stat.data.type, line=stat.line):
					self.Abort("Could not import %s." % stat.data.type, stat.line)
					return False
				if self.GetPath(stat.data.name):
					self.Abort("Variables/properties cannot have the same name as a type.", stat.line)
					return False
				return True
			self.Abort("A variable or property has already been defined with the same name on line %d." % temp.line, stat.line)
			return False
		elif stat.type == self.STAT_FUNCTIONDEF or stat.type == self.STAT_EVENTDEF:
			if stat.data.parameters:
				for param in stat.data.parameters:
					temp = self.GetVariable(param.name)
					if not temp:
						self.variables[len(self.variables)-1][param.name] = Statement(self.STAT_PARAMETER, stat.line, param)
						if not self.CacheScript(param.type, line=stat.line):
							self.Abort("Could not import %s." % param.type, stat.line)
							return False
						if self.GetPath(param.name):
							self.Abort("Parameters cannot have the same name as a type.", stat.line)
							return False
					else:
						self.Abort("A variable or property has already been defined with the same name on line %d." % temp.line, stat.line)
						return False
			return True
		return False

	def GetVariable(self, name):
		name = name.upper()
		for scope in reversed(self.variables):
			temp = scope.get(name, None)
			if temp:
				return temp
		return None

	# Functions and events
	def PushFunctionScope(self):
		if len(self.functions) < 3:
			self.functions.append({})
		else:
			self.Abort("Pushing too many scopes to self.functions")

	def PopFunctionScope(self):
		if len(self.functions) > 2:
			self.functions.pop()
		else:
			self.Abort("Popping too many scopes from self.functions")

	def AddFunction(self, stat):
		if stat.type == self.STAT_FUNCTIONDEF or stat.type == self.STAT_EVENTDEF:
			exists = self.HasFunction(stat.data.name)
			if exists == 0:
				self.functions[len(self.functions)-1][stat.data.name] = stat
				return True
			elif exists == 1:
				old = self.GetFunction(stat.data.name)
				if stat.data.type != old.data.type:
					self.Abort("Return type does not match the return type of the overridden function.", stat.line)
					return False
				if len(stat.data.parameters) != len(old.data.parameters):
					self.Abort("Different number of parameters than in the overridden function.", stat.line)
					return False
				i = 0
				while i < len(stat.data.parameters):
					if stat.data.parameters[i].type != old.data.parameters[i].type:
						self.Abort("Parameter at index %d is of a different type than the corresponding parameter in the overridden function." % i, stat.line)
						return False
					i += 1
				self.functions[len(self.functions)-1][stat.data.name] = stat
				return True
			else:
				old = self.GetFunction(stat.data.name)
				self.Abort("A function or event has already been defined with the same name on line %d." % old.line, stat.line)
		self.Abort("Expected a function or event definition.", stat.line)
		return False

	def HasFunction(self, name):
		name = name.upper()
		currentScope = len(self.functions)
		matchScope = currentScope
		for scope in reversed(self.functions):
			if scope.get(name, None):
				if currentScope == matchScope:
					return -1 # Has been defined in the same scope
				else:
					return 1 # Has been defined in another scope
			else:
				matchScope -= 1
		return 0 # Has not been defined

	def GetFunction(self, name):
		name = name.upper()
		for scope in reversed(self.functions):
			temp = scope.get(name, None)
			if temp:
				return temp
		return None

	# States
	def AddState(self, stat):
		if stat.type == self.STAT_STATEDEF:
			name = stat.data.name.upper()
			exists = self.HasState(name)
			if exists >= 0:
				if stat.data.auto:
					for key, state in self.states[len(self.states)-1].items():
						if state.data.auto:
							self.Abort("An auto state has already been defined on line %d." % state.line, stat.line)
							return False
				self.states[len(self.states)-1][name] = stat
				return True
			else:
				state = self.GetState(name)
				self.Abort("A state by the same name already exists in this script on line %d." % state.line, stat.line)
				return False
		return False

	def HasState(self, name):
		name = name.upper()
		currentScope = len(self.states)
		matchScope = currentScope
		for scope in reversed(self.states):
			if scope.get(name, None):
				if currentScope == matchScope:
					return -1
				else:
					return 1
			else:
				matchScope -= 1
		return 0

	def GetState(self, name):
		name = name.upper()
		for scope in reversed(self.states):
			temp = scope.get(name, None)
			if temp:
				return temp
		return None

	# Other scripts
	def GetLineage(self, name):
		name = name.upper()
		script = self.cache.get(name, None) # Check the cache
		if not script: # Script has not been cached yet
			fullPath = self.GetPath(name)
			if fullPath:
				if not self.CacheScript(name, fullPath):
					return None
			else:
				self.Abort("Could not find parent script among source folders.")
				return None
		parentExtends = self.cache[name].extends
		extends = [name]
		if parentExtends:
			extends.extend(parentExtends)
		return extends

	def GetPath(self, name):
		name = (name + ".psc").upper()
		for path in self.paths:
			for f in os.listdir(path):
				if name == f.upper():
					return os.path.join(path, f)
		return None
#		Original #TODO Remove
#		for path in self.paths:
#			fullPath = os.path.join(path, name + ".psc")
#			if os.path.isfile(fullPath):
#				return fullPath
#		return None

	def CacheScript(self, name, path = None, line = None):
		name = name.upper()
		if name != self.KW_BOOL and name != self.KW_FLOAT and name != self.KW_INT and name != self.KW_STRING and name != self.KW_NONE and name != self.KW_SELF:
			if not self.cache.get(name, None): # Don't cache if it is already cached
				fullPath = path
				if not fullPath:
					fullPath = self.GetPath(name)
					if not fullPath:
						self.Abort("Could not find script ('%s')." % name, line)
						return False
				with open(fullPath) as f:
					scriptContents = f.read()
					lines = []
					tokens = []
					skip = False
					try:
						for token in self.lex.Process(scriptContents):
							if token.type == self.lex.NEWLINE:
								if not skip:
									if tokens:
										lines.append(tokens)
								skip = False
								tokens = []
							elif token.type == self.lex.UNMATCHED:
								skip = True
							else:
								tokens.append(token)
					except LexicalError as e:
						self.Abort("Found a lexical error in %s script." % name)
						return False
					extends = []
					functions = {}
					properties = {}
					states = {}
					statements = []
					try:
						for line in lines:
							stat = self.syn.Process(line)
							if stat:
								statements.append(stat)
					except SyntacticError as e:
						self.Abort("Found a syntactic error in %s script." % name)
						return False
					header = False
					if statements[0].type == self.STAT_SCRIPTHEADER:
						if statements[0].data.parent:
							header = True
							extends = self.GetLineage(statements[0].data.parent)
							parent = self.GetCachedScript(statements[0].data.parent)
							functions.update(parent.functions)
							properties.update(parent.properties)
							states.update(parent.states)
							functions["GOTOSTATE"] = Statement(self.STAT_FUNCTIONDEF, 0, FunctionDef(None, None, False, "GOTOSTATE", "GoToState", [ParameterDef(self.KW_STRING, "String", False, "ASNEWSTATE", "asNewState", None)], []))
							functions["GETSTATE"] = Statement(self.STAT_FUNCTIONDEF, 0, FunctionDef(self.KW_STRING, "String", False, "GETSTATE", "GetState", [], []))
							functions["ONINIT"] = Statement(self.STAT_EVENTDEF, 0, EventDef(None, "ONINIT", "OnInit", [], []))
							functions["ONBEGINSTATE"] = Statement(self.STAT_EVENTDEF, 0, EventDef(None, "ONBEGINSTATE", "OnBeginState", [], []))
							functions["ONENDSTATE"] = Statement(self.STAT_EVENTDEF, 0, EventDef(None, "ONENDSTATE", "OnEndState", [], []))
					i = 0
					while i < len(statements):
						if statements[i].type == self.STAT_FUNCTIONDEF or statements[i].type == self.STAT_EVENTDEF:
							functions[statements[i].data.name] = statements[i]
							if not self.KW_NATIVE in statements[i].data.flags:
								while i < len(statements) and not (statements[i].type == self.STAT_KEYWORD and (statements[i].data.type == self.KW_ENDFUNCTION or statements[i].data.type == self.KW_ENDEVENT)):
									i += 1
						elif statements[i].type == self.STAT_PROPERTYDEF:
							properties[statements[i].data.name] = statements[i]
							if not self.KW_AUTO in statements[i].data.flags and not self.KW_AUTOREADONLY in statements[i].data.flags:
								while i < len(statements) and not (statements[i].type == self.STAT_KEYWORD and statements[i].data.type == self.KW_ENDPROPERTY):
									i += 1
						elif statements[i].type == self.STAT_STATEDEF:
							states[statements[i].data.name] = statements[i]
							while i < len(statements) and not (statements[i].type == self.STAT_KEYWORD and statements[i].data.type == self.KW_ENDSTATE):
								i += 1
						elif statements[i].type == self.STAT_SCRIPTHEADER:
							if not header and statements[i].data.parent:
								header = True
								extends = self.GetLineage(statements[i].data.parent)
						i += 1

					self.cache[name] = CachedScript(extends, properties, functions, states)
		return True

	def GetCachedScript(self, name, line = None):
		name = name.upper()
		temp = self.cache.get(name, None)
		if temp:
			return temp
		else:
			if self.CacheScript(name, line):
				return self.cache.get(name, None)
		return None

	def Process(self, statements, paths, cancel = None): # Return True if successful, False if failed
		# Reset properties
		self.statements = None
		self.paths = paths
		self.cancel = cancel # This is != None only when called by the code completion system
		self.variables = [{}]
		self.functions = [{}]
		self.states = [{}]
		self.imports = []
		self.header = None
		# Script header
		if statements[0].type == self.STAT_SCRIPTHEADER:
			self.header = statements.pop(0)
			# Inherited properties, functions, events, and states
			if self.header.data.parent:
				extends = self.GetLineage(self.header.data.parent)
				if extends:
					parentScript = self.GetCachedScript(self.header.data.parent)
					self.variables[0].update(parentScript.properties)
					self.functions[0].update(parentScript.functions)
					self.states[0].update(parentScript.states)
				else:
					self.Abort(None, self.header.line)
					return False
			# Doc string
			docString = None
			if len(statements) > 0:
				if statements[0].type == self.STAT_DOCUMENTATION:
					docString = statements.pop(0)
		else:
			self.Abort("First line has to be the scriptheader.", statements[0].line)
			return False
		if not self.functions[0].get("GOTOSTATE", None):
			self.functions[0]["GOTOSTATE"] = Statement(self.STAT_FUNCTIONDEF, 0, FunctionDef(None, None, False, "GOTOSTATE", "GoToState", [ParameterDef(self.KW_STRING, "String", False, "ASNEWSTATE", "asNewState", None)], []))
		if not self.functions[0].get("GETSTATE", None):
			self.functions[0]["GETSTATE"] = Statement(self.STAT_FUNCTIONDEF, 0, FunctionDef(self.KW_STRING, "String", False, "GETSTATE", "GetState", [], []))
		if not self.functions[0].get("ONINIT", None):
			self.functions[0]["ONINIT"] = Statement(self.STAT_EVENTDEF, 0, EventDef(None, "ONINIT", "OnInit", [], []))
		if not self.functions[0].get("ONBEGINSTATE", None):
			self.functions[0]["ONBEGINSTATE"] = Statement(self.STAT_EVENTDEF, 0, EventDef(None, "ONBEGINSTATE", "OnBeginState", [], []))
		if not self.functions[0].get("ONENDSTATE", None):
			self.functions[0]["ONENDSTATE"] = Statement(self.STAT_EVENTDEF, 0, EventDef(None, "ONENDSTATE", "OnEndState", [], []))
		# Properties, functions, events, states, and scriptwide variables
		self.variables.append({})
		self.functions.append({})
		self.states.append({})
		definitions = []
		autoState = None
		while len(statements) > 0:
			stat = statements.pop(0)
			if stat.type == self.STAT_PROPERTYDEF:
				if not self.AddVariable(stat):
					return False
				if stat.data.value:
					if stat.data.array:
						if stat.data.value.type != self.KW_NONE:
							self.Abort("Array properties can only be initialized with NONE.", stat.line)
					else:
						if stat.data.type != stat.data.value.type and not self.CanAutoCast(NodeResult(stat.data.value.type, False, True), NodeResult(stat.data.type, False, True)):
							self.Abort("Initialization of %s property with a %s literal." % (stat.data.type, stat.data.value.type), stat.line)
				if self.KW_CONDITIONAL in stat.data.flags and not self.KW_CONDITIONAL in self.header.data.flags:
					self.Abort("The %s property has the CONDITIONAL flag, but the script header does not." % stat.data.name, stat.line)
				if not self.KW_AUTO in stat.data.flags and not self.KW_AUTOREADONLY in stat.data.flags:
					prop = [stat]
					while len(statements) > 0 and not (statements[0].type == self.STAT_KEYWORD and statements[0].data.type == self.KW_ENDPROPERTY):
						prop.append(statements.pop(0))
					if len(statements) > 0:
						prop.append(statements.pop(0))
						definitions.append({self.DEFINITION_PROPERTY:prop})
					else:
						self.Abort("Unterminated property definition.", prop[0].line)
						return False
				else:
					docString = None
					if len(statements) > 0:
						if statements[0].type == self.STAT_DOCUMENTATION:
							docString = statements.pop(0)
			elif stat.type == self.STAT_VARIABLEDEF:
				if not self.AddVariable(stat):
					return False
				if stat.data.value:
					if stat.data.array:
						if self.GetLiteral(stat.data.value) != self.KW_NONE:
							self.Abort("Array variables can only be initialized with NONE when defined outside of functions/events.", stat.line)
					else:
						value = self.GetLiteral(stat.data.value)
						if not value:
							self.Abort("Variables can only be initialized with literals when defined outside of functions/events.", stat.line)
						if stat.data.type != value and not self.CanAutoCast(NodeResult(value, False, True), NodeResult(stat.data.type, False, True)):
							self.Abort("Initialization of a %s variable with a %s literal." % (stat.data.type, value), stat.line)
				if self.KW_CONDITIONAL in stat.data.flags and not self.KW_CONDITIONAL in self.header.data.flags:
					self.Abort("The %s variable has the CONDITIONAL flag, but the script header does not." % stat.data.name, stat.line)
			elif stat.type == self.STAT_FUNCTIONDEF:
				if not self.AddFunction(stat):
					return False
				if not self.KW_NATIVE in stat.data.flags:
					func = [stat]
					while len(statements) > 0 and not (statements[0].type == self.STAT_KEYWORD and statements[0].data.type == self.KW_ENDFUNCTION):
						func.append(statements.pop(0))
					if len(statements) > 0:
						func.append(statements.pop(0))
						definitions.append({self.DEFINITION_FUNCTION:func})
					else:
						self.Abort("Unterminated function definition.", func[0].line)
						return False
				else:
					self.PushVariableScope()
					self.AddVariable(stat)
					self.PopVariableScope()
					docString = None
					if len(statements) > 0:
						if statements[0].type == self.STAT_DOCUMENTATION:
							docString = statements.pop(0)
			elif stat.type == self.STAT_EVENTDEF:
				if not self.AddFunction(stat):
					return False
				if not self.KW_NATIVE in stat.data.flags:
					event = [stat]
					while len(statements) > 0 and not (statements[0].type == self.STAT_KEYWORD and statements[0].data.type == self.KW_ENDEVENT):
						event.append(statements.pop(0))
					if len(statements) > 0:
						event.append(statements.pop(0))
						definitions.append({self.DEFINITION_EVENT:event})
					else:
						self.Abort("Unterminated event definition.", event[0].line)
						return False
				else:
					self.PushVariableScope()
					self.AddVariable(stat)
					self.PopVariableScope()
					docString = None
					if len(statements) > 0:
						if statements[0].type == self.STAT_DOCUMENTATION:
							docString = statements.pop(0)
			elif stat.type == self.STAT_IMPORT:
				if not stat.data.name in self.imports:
					self.imports.append(stat.data.name)
					if not self.CacheScript(stat.data.name, line=stat.line):
						return False
				else:
					self.Abort("%s has already been imported in this script." % stat.data.name, stat.line)
					return False
			elif stat.type == self.STAT_STATEDEF:
				if stat.data.auto:
					autoState = stat
				state = [stat]
				while len(statements) > 0 and not (statements[0].type == self.STAT_KEYWORD and statements[0].data.type == self.KW_ENDSTATE):
					state.append(statements.pop(0))
				if len(statements) > 0:
					state.append(statements.pop(0))
					definitions.append({self.DEFINITION_STATE:state})
				else:
					self.Abort("Unterminated state definition.", state[0].line)
					return False
			else:
				if stat.type == self.STAT_SCRIPTHEADER and self.header:
					self.Abort("Only one script header is allowed per script.", stat.line)
				else:
					self.Abort("Illegal statement in this scope.", stat.line)
				return False
		for obj in definitions:
			for typ, statements in obj.items():
				if typ == self.DEFINITION_FUNCTION or typ == self.DEFINITION_EVENT:
					self.PushVariableScope()
					self.FunctionBlock(statements)
					self.PopVariableScope()
				elif typ == self.DEFINITION_PROPERTY:
					self.PushFunctionScope()
					self.PropertyBlock(statements)
					self.PopFunctionScope()
				elif typ == self.DEFINITION_STATE:
					self.PushFunctionScope()
					self.StateBlock(statements)
					self.PopFunctionScope()
		if self.cancel:
			raise EmptyStateCancel(self.functions)
		return True

	def PropertyBlock(self, statements):
		start = statements.pop(0)
		if self.cancel:
			if start.line >= self.cancel:
				self.PopFunctionScope()
				raise EmptyStateCancel(self.functions)
		end = statements.pop()
		docString = None
		if len(statements) > 0:
			if statements[0].type == self.STAT_DOCUMENTATION:
				docString = statements.pop(0)
		functions = {}
		while len(statements) > 0:
			if statements[0].type == self.STAT_FUNCTIONDEF:
				stat = statements.pop(0)
				if stat.data.flags:
					self.Abort("Functions in property definitions cannot have any flags.", stat.line)
					return False
				if stat.data.name == "SET" or stat.data.name == "GET":
					if functions.get(stat.data.name, None):
						self.Abort("The %s function has already been defined in this property." % stat.data.name, stat.line)
						return False
					else:
						if stat.data.name == "GET":
							if stat.data.type != start.data.type or stat.data.array != start.data.array:
								self.Abort("The return type of the GET function and the property type must match.", stat.line)
								return False
				else:
					self.Abort("Only SET and GET functions may be defined in a property definition.", stat.line)
					return False
				func = [stat]
				while len(statements) > 0 and not (statements[0].type == self.STAT_KEYWORD and statements[0].data.type == self.KW_ENDFUNCTION):
					func.append(statements.pop(0))
				if len(statements) > 0:
					func.append(statements.pop(0))
					functions[stat.data.name] = func
				else:
					self.Abort("Unterminated function definition.", stat.line)
					return False
			else:
				self.Abort("Illegal statement in a property definition.", statements[0].line)
		if len(functions) == 0 and self.cancel == None:
			self.Abort("At least a SET or a GET function has to be defined in a property definition.", start.line)
			return False
		for key, func in functions.items():
			self.PushVariableScope()
			if not self.FunctionBlock(func):
				return False
			self.PopVariableScope()
		return True

	def FunctionBlock(self, statements):
		start = statements.pop(0)
		if self.cancel:
			if start.line >= self.cancel:
				self.PopVariableScope()
				if len(self.functions) > 2:
					raise StateCancel(self.functions)
				else:
					raise EmptyStateCancel(self.functions)
		end = statements.pop()
		typ = None
		if start.data.type:
			if start.data.array:
				typ = NodeResult(start.data.type, True, True)
			else:
				typ = NodeResult(start.data.type, False, True)
		docString = None
		if len(statements) > 0:
			if statements[0].type == self.STAT_DOCUMENTATION:
				docString = statements.pop(0)
		if not self.AddVariable(start):
			return False
		if start.type == self.STAT_FUNCTIONDEF:
			for param in start.data.parameters:
				if param.expression:
					if param.array:
						if self.GetLiteral(param.expression) != self.KW_NONE:
							self.Abort("Array parameters can only be initialized with NONE", start.line)
					else:
						value = self.GetLiteral(param.expression)
						if not value:
							self.Abort("Parameters can only be initialized with literals.", start.line)
						if param.type != value and not self.CanAutoCast(NodeResult(value, False, True), NodeResult(param.type, False, True)):
							self.Abort("Initialization of %s parameter with %s literal." % (param.type, value), start.line)
		self.statements = statements
		while len(self.statements) > 0:
			if self.cancel:
				if self.statements[0].line >= self.cancel:
					raise FunctionDefinitionCancel(start.data.type, self.functions, self.variables, self.imports)
			if self.statements[0].type == self.STAT_VARIABLEDEF:
				if not self.VariableDef():
					return False
			elif self.statements[0].type == self.STAT_ASSIGNMENT:
				if not self.Assignment():
					return False
			elif self.statements[0].type == self.STAT_EXPRESSION:
				if not self.Expression():
					return False
			elif self.statements[0].type == self.STAT_IF:
				self.PushVariableScope()
				if not self.IfBlock(typ):
					return False
				self.PopVariableScope()
			elif self.statements[0].type == self.STAT_WHILE:
				self.PushVariableScope()
				if not self.WhileBlock(typ):
					return False
				self.PopVariableScope()
			elif self.statements[0].type == self.STAT_RETURN:
				if not self.Return(typ):
					return False
			else:
				self.Abort("Illegal statement in a function definition.", self.statements[0].line)
				return False
		if self.cancel:
			if end.line >= self.cancel:
				raise FunctionDefinitionCancel(start.data.type, self.functions, self.variables, self.imports)
		return True

	def StateBlock(self, statements):
		start = statements.pop(0)
		if self.cancel:
			if start.line >= self.cancel:
				self.PopFunctionScope()
				raise EmptyStateCancel(self.functions)
		end = statements.pop()
		if not self.AddState(start):
			return False
		definitions = []
		while len(statements) > 0:
			if statements[0].type == self.STAT_FUNCTIONDEF:
				exists = self.HasFunction(statements[0].data.name)
				if exists == -1:
					self.Abort("%s has been defined in the state already." % statements[0].data.name, statements[0].line)
					return False
				if exists == 0:
					self.Abort("%s has not been defined in the empty state." % statements[0].data.name, statements[0].line)
					return False
				if not self.AddFunction(statements[0]):
					return False
				if not self.KW_NATIVE in statements[0].data.flags:
					func = [statements.pop(0)]
					while len(statements) > 0 and not (statements[0].type == self.STAT_KEYWORD and statements[0].data.type == self.KW_ENDFUNCTION):
						func.append(statements.pop(0))
					if len(statements) > 0:
						func.append(statements.pop(0))
						definitions.append({self.DEFINITION_FUNCTION:func})
					else:
						self.Abort("Unterminated function definition.", func[0].line)
						return False
			elif statements[0].type == self.STAT_EVENTDEF:
				exists = self.HasFunction(statements[0].data.name)
				if exists == 0:
					self.Abort("%s has not been defined in the empty state." % statements[0].data.name, statements[0].line)
					return False
				if exists == -1:
					self.Abort("%s has already been defined in the same state." % statements[0].data.name, statements[0].line)
					return False
				if not self.AddFunction(statements[0]):
					return False
				if not self.KW_NATIVE in statements[0].data.flags:
					event = [statements.pop(0)]
					while len(statements) > 0 and not (statements[0].type == self.STAT_KEYWORD and statements[0].data.type == self.KW_ENDEVENT):
						event.append(statements.pop(0))
					if len(statements) > 0:
						event.append(statements.pop(0))
						definitions.append({self.DEFINITION_EVENT:event})
					else:
						self.Abort("Unterminated event definition.", event[0].line)
						return False
			else:
				self.Abort("Illegal statement in a state definition.", statements[0].line)
				return False
		for obj in definitions:
			for typ, statements in obj.items():
				if typ == self.DEFINITION_FUNCTION or typ == self.DEFINITION_EVENT:
					self.PushVariableScope()
					if not self.FunctionBlock(statements):
						return False
					self.PopVariableScope()
		if self.cancel:
			if end.line >= self.cancel:
				raise StateCancel(self.functions)
		return True

	def IfBlock(self, typ):
		if not self.cancel:
			expr = self.NodeVisitor(self.statements[0].data.expression)
		start = self.statements.pop(0)
		while len(self.statements) > 0 and not (self.statements[0].type == self.STAT_KEYWORD and self.statements[0].data.type == self.KW_ENDIF):
			if self.cancel:
				if self.statements[0].line >= self.cancel:
					if typ:
						raise FunctionDefinitionCancel(typ.type, self.functions, self.variables, self.imports)
					else:
						raise FunctionDefinitionCancel(None, self.functions, self.variables, self.imports)
			if self.statements[0].type == self.STAT_VARIABLEDEF:
				if not self.VariableDef():
					return False
			elif self.statements[0].type == self.STAT_ASSIGNMENT:
				if not self.Assignment():
					return False
			elif self.statements[0].type == self.STAT_EXPRESSION:
				if not self.Expression():
					return False
			elif self.statements[0].type == self.STAT_IF:
				self.PushVariableScope()
				if not self.IfBlock(typ):
					return False
				self.PopVariableScope()
			elif self.statements[0].type == self.STAT_ELSEIF:
				self.PopVariableScope()
				self.PushVariableScope()
				if not self.cancel:
					expr = self.NodeVisitor(self.statements[0].data.expression)
				self.statements.pop(0)
			elif self.statements[0].type == self.STAT_KEYWORD and self.statements[0].data.type == self.KW_ELSE:
				self.PopVariableScope()
				self.PushVariableScope()
				self.statements.pop(0)
			elif self.statements[0].type == self.STAT_WHILE:
				self.PushVariableScope()
				if not self.WhileBlock(typ):
					return False
				self.PopVariableScope()
			elif self.statements[0].type == self.STAT_RETURN:
				if not self.Return(typ):
					return False
			else:
				self.Abort("Illegal statement in an if-block.", self.statements[0].line)
				return False
		if len(self.statements) > 0:
			self.statements.pop(0) # Pop EndIf statement
		else:
			self.Abort("Unterminated if-block.", start.line)
			return False
		return True

	def WhileBlock(self, typ):
		if not self.cancel:
			expr = self.NodeVisitor(self.statements[0].data.expression)
		self.statements.pop(0)
		while len(self.statements) > 0 and not (self.statements[0].type == self.STAT_KEYWORD and self.statements[0].data.type == self.KW_ENDWHILE):
			if self.cancel:
				if self.statements[0].line >= self.cancel:
					if typ:
						raise FunctionDefinitionCancel(typ.type, self.functions, self.variables, self.imports)
					else:
						raise FunctionDefinitionCancel(None, self.functions, self.variables, self.imports)
			if self.statements[0].type == self.STAT_VARIABLEDEF:
				if not self.VariableDef():
					return False
			elif self.statements[0].type == self.STAT_ASSIGNMENT:
				if not self.Assignment():
					return False
			elif self.statements[0].type == self.STAT_EXPRESSION:
				if not self.Expression():
					return False
			elif self.statements[0].type == self.STAT_IF:
				self.PushVariableScope()
				if not self.IfBlock(typ):
					return False
				self.PopVariableScope()
			elif self.statements[0].type == self.STAT_WHILE:
				self.PushVariableScope()
				if not self.WhileBlock(typ):
					return False
				self.PopVariableScope()
			elif self.statements[0].type == self.STAT_RETURN:
				if not self.Return(typ):
					return False
			else:
				self.Abort("Illegal statement in a while-loop.", self.statements[0].line)
				return False
		if len(self.statements) > 0:
			self.statements.pop(0) # Pop EndWhile statement
		else:
			self.Abort("Unterminated while-loop.", start.line)
			return False
		return True

	def VariableDef(self):
		if not self.AddVariable(self.statements[0]):
			return False
		if self.statements[0].data.value:
			if not self.cancel:
				expr = self.NodeVisitor(self.statements[0].data.value)
				if expr:
					if expr.array:
						if not self.statements[0].data.array:
							self.Abort("The expression resolves to an array type, but the variable is not an array variable.")
							return False
						if self.statements[0].data.type != expr.type:
							self.Abort("The expression resolves to an array type, but the variable is an array of another type.")
							return False
					elif self.statements[0].data.array:
						val = self.GetLiteral(self.statements[0].data.value)
						if val != self.KW_NONE:
							self.Abort("Array variables can only be initialized with NONE.")
							return False
					elif self.statements[0].data.type != expr.type:
						if not self.CanAutoCast(expr, NodeResult(self.statements[0].data.type, self.statements[0].data.array, True)):
							self.Abort("The expression resolves to the incorrect type and cannot be automatically cast to the correct type.")
							return False
				else:
					self.Abort(None)
					return False
		self.statements.pop(0)
		return True

	def Assignment(self):
		if not self.cancel:
			left = self.NodeVisitor(self.statements[0].data.leftExpression)
			if left == self.KW_NONE:
				self.Abort("The left-hand side expression resolves to NONE.")
				return False
			right = self.NodeVisitor(self.statements[0].data.rightExpression)
			if left.type != right.type and left.array != right.array and left.object != right.object and not self.CanAutoCast(right, left):
				self.Abort("The right-hand side expression does not resolve to the same type as the left-hand side expression and cannot be auto-cast.")
				return False
		self.statements.pop(0)
		return True

	def Expression(self):
		if not self.cancel:
			expr = self.NodeVisitor(self.statements[0].data.expression)
		self.statements.pop(0)
		return True

	def Return(self, typ):
		if self.statements[0].data.expression:
			if not self.cancel:
				expr = self.NodeVisitor(self.statements[0].data.expression)
				if typ:
					if expr.type != typ.type and expr.array != typ.array and not self.CanAutoCast(expr, typ):
						self.Abort("The returned value's type does not match the function's return type.")
						return False
		self.statements.pop(0)
		return True

	def NodeVisitor(self, node, expected = None):
		result = None
		#print("\nEntering node: %s" % node.type)
		#print("Expecting type: %s" % expected)
		#print(node)
		if node.type == self.NODE_EXPRESSION:
			result = self.NodeVisitor(node.data.child)
		elif node.type == self.NODE_ARRAYATOM or node.type == self.NODE_ARRAYFUNCORID:
			result = self.NodeVisitor(node.data.child, expected)
			if node.data.expression:
				if result.type == self.KW_NONE:
					self.Abort("Expected an array object instead of NONE.")
				elif not result.array:
					self.Abort("Expected an array object.")
				expr = self.NodeVisitor(node.data.expression)
				if expr.type != self.KW_INT or expr.array:
					self.Abort("Expected an expression that resolves to INT when accessing an array element.")
				result = NodeResult(result.type, False, result.object)
		elif node.type == self.NODE_CONSTANT:
			if node.data.token.type == self.BOOL:
				result = NodeResult(self.KW_BOOL, False, True)
			elif node.data.token.type == self.FLOAT:
				result = NodeResult(self.KW_FLOAT, False, True)
			elif node.data.token.type == self.INT:
				result = NodeResult(self.KW_INT, False, True)
			elif node.data.token.type == self.STRING:
				result = NodeResult(self.KW_STRING, False, True)
			elif node.data.token.type == self.KW_NONE:
				result = NodeResult(self.KW_NONE, False, True)
			else:
				self.Abort("Unknown literal type.")
		elif node.type == self.NODE_FUNCTIONCALL:
			func = None
			if expected and expected.type == self.KW_SELF:
				func = self.GetFunction(node.data.name.value.upper())
				if func:
					if func.data.type:
						if func.data.array:
							result = NodeResult(func.data.type, True, True)
						else:
							result = NodeResult(func.data.type, False, True)
					else:
						result = NodeResult(self.KW_NONE, False, True)
				else:
					self.Abort("This script does not have a function/event called %s." % node.data.name.value)
			elif expected and expected.type:
				if expected.array:
					script = self.GetCachedScript(expected.type)
					if script:
						funcName = node.data.name.value.upper()
						if funcName == "FIND":
							func = Statement(self.STAT_FUNCTIONDEF, 0, FunctionDef("INT", "Int", False, "FIND", "Find", [ParameterDef(expected.type, expected.type.capitalize(), False, "AKELEMENT", "akElement", None), ParameterDef("INT", "Int", False, "AISTARTINDEX", "aiStartIndex", Node(self.NODE_EXPRESSION, ExpressionNode(Node(self.NODE_CONSTANT, ConstantNode(Token(self.INT, "0", 0, 0))))))], [self.KW_NATIVE]))							
							result = NodeResult(self.KW_INT, False, True)
						elif funcName == "RFIND":
							func = Statement(self.STAT_FUNCTIONDEF, 0, FunctionDef("INT", "Int", False, "RFIND", "RFind", [ParameterDef(expected.type, expected.type.capitalize(), False, "AKELEMENT", "akElement", None), ParameterDef("INT", "Int", False, "AISTARTINDEX", "aiStartIndex", Node(self.NODE_EXPRESSION, ExpressionNode(Node(self.NODE_UNARYOPERATOR, UnaryOperatorNode(self.OP_SUBTRACTION, Node(self.NODE_CONSTANT, ConstantNode(Token(self.INT, "1", 0, 0))))))))], [self.KW_NATIVE]))
							result = NodeResult(self.KW_INT, False, True)
						else:
							self.Abort("Arrays objects only have FIND and RFIND functions.")
				else:
					script = self.GetCachedScript(expected.type)
					if script:
						func = script.functions.get(node.data.name.value.upper(), None)
						if func:
							if expected.object and self.KW_GLOBAL in func.data.flags:
								self.Abort("Attempted to call a global function on an object.")
							elif not expected.object and not self.KW_GLOBAL in func.data.flags:
								self.Abort("Attempted to call a non-global function by directly referencing the script.")
							if func.data.type:
								if func.data.array:
									result = NodeResult(func.data.type, True, True)
								else:
									result = NodeResult(func.data.type, False, True)
							else:
								result = NodeResult(self.KW_NONE, False, True)
						else:
							self.Abort("%s does not have a function/event called %s." % (expected.type, node.data.name.value))
			else:
				func = self.GetFunction(node.data.name.value)
				if func:
					if func.data.type:
						if func.data.array:
							result = NodeResult(func.data.type, True, True)
						else:
							result = NodeResult(func.data.type, False, True)
					else:
						result = NodeResult(self.KW_NONE, False, True)
				for imp in self.imports:
					script = self.GetCachedScript(imp)
					if script:
						temp = script.functions.get(node.data.name.value.upper(), None)
						if temp:
							if func:
								self.Abort("Ambiguous reference to a function called %s. It is unclear which version is being referenced." % node.data.name.value)
							func = temp
							if self.KW_GLOBAL in func.data.flags:
								if func.data.type:
									if func.data.array:
										result = NodeResult(func.data.type, True, True)
									else:
										result = NodeResult(func.data.type, False, True)
								else:
									result = NodeResult(self.KW_NONE, False, True)
				if not result:
					self.Abort("%s is not a function/event that exists in this scope." % node.data.name.value)
			if func:
				params = func.data.parameters[:]
				args = [a.data for a in node.data.arguments]
				outOfOrder = False
				while len(params) > 0:
					if not outOfOrder and len(args) > 0:
						if args[0].name:
							outOfOrder = True
					if outOfOrder:
						i = 0
						j = len(args)
						while i < j:
							if not args[i].name:
								self.Abort("Arguments are being passed out of order, but at least one argument does not specify which parameter it is passing a value to.")
							if args[i].name.value.upper() == params[0].name:
								argExpr = self.NodeVisitor(args[0].expression)
								paramType = None
								if params[0].array:
									paramType = NodeResult(params[0].type, True, True)
								else:
									paramType = NodeResult(params[0].type, False, True)
								if (argExpr.type != paramType.type or argExpr.array != paramType.array or argExpr.object != paramType.object) and not self.CanAutoCast(argExpr, paramType):
									aType = argExpr.type
									if argExpr.array:
										aType = "%s[]" % aType
									pType = paramType.type
									if paramType.array:
										pType = "%s[]" % pType
									self.Abort("Parameter %s is of type %s, but the argument evaluates to %s, which cannot be auto-cast to the parameter's type." % (params[0].name, pType, aType))
								args.pop(i)
								break
							i += 1
						if len(args) == j and not params[0].expression:
							self.Abort("An argument was not passed to the mandatory parameter %s." % params[0].name)
					else:
						if params[0].expression:
							if len(args) > 0:
								argExpr = self.NodeVisitor(args[0].expression)
								paramType = None
								if params[0].array:
									paramType = NodeResult(params[0].type, True, True)
								else:
									paramType = NodeResult(params[0].type, False, True)
								if (argExpr.type != paramType.type or argExpr.array != paramType.array or argExpr.object != paramType.object) and not self.CanAutoCast(argExpr, paramType):
									aType = argExpr.type
									if argExpr.array:
										aType = "%s[]" % aType
									pType = paramType.type
									if paramType.array:
										pType = "%s[]" % pType
									self.Abort("Parameter %s is of type %s, but the argument evaluates to %s, which cannot be auto-cast to the parameter's type." % (params[0].name, pType, aType))
								args.pop(0)
						else:
							if len(args) > 0:
								argExpr = self.NodeVisitor(args[0].expression)
								paramType = None
								if params[0].array:
									paramType = NodeResult(params[0].type, True, True)
								else:
									paramType = NodeResult(params[0].type, False, True)
								if (argExpr.type != paramType.type or argExpr.array != paramType.array or argExpr.object != paramType.object) and not self.CanAutoCast(argExpr, paramType):
									aType = argExpr.type
									if argExpr.array:
										aType = "%s[]" % aType
									pType = paramType.type
									if paramType.array:
										pType = "%s[]" % pType
									self.Abort("Parameter %s is of type %s, but the argument evaluates to %s, which cannot be auto-cast to the parameter's type." % (params[0].name, pType, aType))
								args.pop(0)
							else:
								self.Abort("Mandatory parameter %s was not given an argument." % params[0].name)
					params.pop(0)
				if len(args) > 0:
					paramCount = len(func.data.parameters)
					argCount = len(node.data.arguments)
					if argCount == paramCount:
						for arg in args:
							found = False
							argName = arg.name.value.upper()
							for param in func.data.parameters:
								if param.name == argName:
									found = True
							if not found:
								self.Abort("%s is not a parameter that exists in %s." % (argName, func.data.name))
						self.Abort("Multiple arguments were passed to at least one parameter.")
					elif argCount > paramCount:
						if argCount == 1:
							self.Abort("The %s function/event has %d parameters, but %d argument was passed to it." % (func.data.name, paramCount, argCount))
						else:
							self.Abort("The %s function/event has %d parameters, but %d arguments were passed to it." % (func.data.name, paramCount, argCount))
		elif node.type == self.NODE_IDENTIFIER:
			if expected and expected.type: # Another script
				if expected.type == self.KW_SELF:
					prop = self.GetVariable(node.data.token.value.upper())
					if prop and prop.type == self.STAT_PROPERTYDEF:
						if prop.data.array:
							result = NodeResult(prop.data.type, True, True)
						else:
							result = NodeResult(prop.data.type, False, True)
					else:
						self.Abort("This script does not have a property called %s." % (node.data.token.value))
				else:
					script = self.GetCachedScript(expected.type)
					if script:
						prop = script.properties.get(node.data.token.value.upper(), None)
						if prop:
							if prop.data.array:
								result = NodeResult(prop.data.type, True, True)
							else:
								result = NodeResult(prop.data.type, False, True)
						else:
							self.Abort("%s does not have a property called %s." % (expected.type, node.data.token.value))
					else:
						pass
			else: # Self or parent
				if node.data.token.type == self.KW_PARENT:
					if self.header.data.parent:
						result = NodeResult(self.header.data.parent, False, True)
					else:
						self.Abort("A parent script has not been defined in this script.")
				elif node.data.token.type == self.KW_SELF:
					result = NodeResult(self.KW_SELF, False, True)
				else:
					var = self.GetVariable(node.data.token.value)
					if var:
						if var.data.array:
							result = NodeResult(var.data.type, True, True)
						else:
							result = NodeResult(var.data.type, False, True)
					else:
						result = NodeResult(node.data.token.value, False, False)
						if not self.GetCachedScript(result.type):
							self.Abort("%s is not a script." % result.type)
		elif node.type == self.NODE_LENGTH:
			result = NodeResult(self.KW_INT, False, True)
		elif node.type == self.NODE_ARRAYCREATION:
			result = NodeResult(node.data.typeToken.value, True, True)
		elif node.type == self.NODE_BINARYOPERATOR:
			if node.data.operator.type == self.KW_AS:
				leftResult = self.NodeVisitor(node.data.leftOperand, expected)
				rightResult = NodeResult(node.data.rightOperand.data.token.value, False, True)
				if leftResult.array and rightResult.type != self.KW_STRING and rightResult.type != self.KW_BOOL:
					self.Abort("Arrays can only be cast to STRING and BOOL.")
				if rightResult.type != self.KW_BOOL and rightResult.type != self.KW_FLOAT and rightResult.type != self.KW_INT and rightResult.type != self.KW_STRING and not self.GetCachedScript(rightResult.type):
					self.Abort("%s is not a type that exists." % rightResult.type)
				result = rightResult
			elif node.data.operator.type == self.OP_DOT:
				leftResult = self.NodeVisitor(node.data.leftOperand, expected)
				expected = leftResult
				rightResult = self.NodeVisitor(node.data.rightOperand, expected)
				result = rightResult
			elif node.data.operator.type == self.OP_ADDITION or node.data.operator.type == self.OP_SUBTRACTION or node.data.operator.type == self.OP_MULTIPLICATION or node.data.operator.type == self.OP_DIVISION or node.data.operator.type == self.OP_MODULUS:
				leftResult = self.NodeVisitor(node.data.leftOperand, expected)
				rightResult = self.NodeVisitor(node.data.rightOperand, expected)
				if leftResult.type != rightResult.type and leftResult.array != rightResult.array and leftResult.object != rightResult.object:
					if self.CanAutoCast(leftResult, rightResult):
						result = rightResult
					elif self.CanAutoCast(rightResult, leftResult):
						result = leftResult
					else:
						self.Abort("The two operands of an arithmetic operation are of different types that cannot be auto-cast to be the same.")
				else:
					result = rightResult
			elif node.data.operator.type == self.LOG_AND or node.data.operator.type == self.LOG_OR:
				leftResult = self.NodeVisitor(node.data.leftOperand, expected)
				rightResult = self.NodeVisitor(node.data.rightOperand, expected)
				result = rightResult
			elif node.data.operator.type == self.CMP_EQUAL or node.data.operator.type == self.CMP_NOT_EQUAL or node.data.operator.type == self.CMP_LESS_THAN or node.data.operator.type == self.CMP_GREATER_THAN or node.data.operator.type == self.CMP_LESS_THAN_OR_EQUAL or node.data.operator.type == self.CMP_GREATER_THAN_OR_EQUAL:
				leftResult = self.NodeVisitor(node.data.leftOperand, expected)
				rightResult = self.NodeVisitor(node.data.rightOperand, expected)
				result = rightResult
		elif node.type == self.NODE_UNARYOPERATOR:
			result = self.NodeVisitor(node.data.operand)
		else:
			self.Abort("Unknown node type")
			return None
		#print("\nExiting node: %s" % node.type)
		#print("Returning type: %s" % result)
		if result:
			return result
		else:
			return None

	def CanAutoCast(self, src, dest):
		if not src or not dest:
			return False
		if dest.type == self.KW_BOOL:
			return True
		elif dest.type == self.KW_STRING:
			return True
		if src.array:
			return False
		elif dest.array:
			return False
		if dest.type == self.KW_INT:
			return False
		elif dest.type == self.KW_FLOAT:
			if src.type == self.KW_INT:
				return True
			else:
				return False
		else:
			if src.type == self.KW_NONE:
				return True
			else:
				if src.type == self.KW_SELF:
					if self.header.data.parent:
						if dest.type == self.header.data.parent:
							return True
						else:
							script = self.GetCachedScript(self.header.data.parent)
							if script:
								if dest.type in script.extends:
									return True
								else:
									return False
							else:
								return False
				else:
					script = self.GetCachedScript(src.type)
					if script:
						if dest.type in script.extends:
							return True
						else:
							return False
					else:
						return False

	def GetLiteral(self, expression, value = False):
		if expression.type == self.NODE_EXPRESSION:
			temp = expression.data.child
			if temp.type == self.NODE_CONSTANT:
				if value:
					return temp.data.token.value
				else:
					if temp.data.token.type == self.BOOL:
						return self.KW_BOOL
					elif temp.data.token.type == self.FLOAT:
						return self.KW_FLOAT
					elif temp.data.token.type == self.INT:
						return self.KW_INT
					elif temp.data.token.type == self.STRING:
						return self.KW_STRING
					elif temp.data.token.type == self.KW_NONE:
						return self.KW_NONE
					else:
						self.Abort("Unknown literal type.")
			elif temp.type == self.NODE_UNARYOPERATOR:
				if temp.data.operator.type == self.OP_SUBTRACTION:
					if temp.data.operand.type == self.NODE_CONSTANT:
						if value:
							return "-%s" % temp.data.operand.data.token.value
						else:
							if temp.data.operand.data.token.type == self.INT:
								return self.KW_INT
							elif temp.data.operand.data.token.type == self.FLOAT:
								return self.KW_FLOAT
							else:
								return None
		return None