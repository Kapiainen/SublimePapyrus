# It is faster to store Statement/Node type as an attribute in a Statement object than it is to use the isinstance() function.
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
	#Caprica extensions
	BREAK = 27
	CONTINUE = 28
	SWITCH = 29
	CASE = 30
	DEFAULT = 31
	ENDSWITCH = 32
	FOR = 33
	ENDFOR = 34
	FOREACH = 35
	ENDFOREACH = 36
	DO = 37
	LOOPWHILE = 38

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
	"WHILE",
	#Caprica extensions
	"BREAK",
	"CONTINUE",
	"SWITCH",
	"CASE",
	"DEFAULT",
	"ENDSWITCH",
	"FOR",
	"ENDFOR",
	"FOREACH",
	"ENDFOREACH",
	"DO",
	"LOOPWHILE"
]

class NodeEnum(object):
	ARRAYATOM = 0
	ARRAYCREATION = 1
	ARRAYFUNCORID = 2
	BINARYOPERATOR = 3
	CONSTANT = 4
	EXPRESSION = 5
	FUNCTIONCALL = 6
	FUNCTIONCALLARGUMENT = 7
	IDENTIFIER = 8
	LENGTH = 9
	STRUCTCREATION = 10
	UNARYOPERATOR = 11

NodeDescription = [
	"ARRAYATOM",
	"ARRAYCREATION",
	"ARRAYFUNCORID",
	"BINARYOPERATOR",
	"CONSTANT",
	"EXPRESSION",
	"FUNCTIONCALL",
	"FUNCTIONCALLARGUMENT",
	"IDENTIFIER",
	"LENGTH",
	"STRUCTCREATION",
	"UNARYOPERATOR"
]

class Identifier(object):
	__slots__ = [
		"namespace", # list of str
		"name", # str
	]

	def __init__(self, aIdentifier):
		assert isinstance(aIdentifier, list #Prune
		self.name = aIdentifier.pop()
		self.namespace = aIdentifier

class Type(object):
	__slots__ = [
		"identifier", # Identifier
		"isArray", # bool
		"isStruct" # bool
	]

	def __init__(self, aIdentifier, aArray, aStruct):
		assert isinstance(aIdentifier, Identifier) #Prune
		assert isinstance(aArray, bool) #Prune
		assert isinstance(aStruct, bool) #Prune
		self.identifier = aIdentifier
		self.isArray = aArray
		self.isStruct = aStruct

class Node(object):
	__slots__ = []

	def __init__(self):
		pass

class ArrayAtomNode(Node):
	__slots__ = [
		"child", # *Node
		"expression" # *Node
	]

	def __init__(self, aChild, aExpression):
		assert isinstance(aChild, Node) #Prune
		assert isinstance(aExpression, Node) #Prune
		self.child = aChild
		self.expression = aExpression

class ArrayCreationNode(Node):
	__slots__ = [
		""
	]

	def __init__(self):
		pass

class ArrayFuncOrIdNode(Node):
	__slots__ = [
		"child", # *Node
		"expression" # *Node
	]

	def __init__(self, aChild, aExpression):
		assert isinstance(aChild, Node) #Prune
		assert isinstance(aExpression, Node) #Prune
		self.child = aChild
		self.expression = aExpression

class BinaryOperatorNode(Node):
	__slots__ = [
		"operator", # Token
		"leftOperand", # *Node
		"rightOperand", # *Node
	]

	def __init__(self, aOperator, aLeftOperand, aRightOperand):
		assert isinstance(aOperator, Token) #Prune
		assert isinstance(aLeftOperand, Node) #Prune
		assert isinstance(aRightOperand, Node) #Prune
		self.operator = aOperator
		self.leftOperand = aLeftOperand
		self.rightOperand = aRightOperand

class ConstantNode(Node):
	__slots__ = [
		"value" # Token
	]

	def __init__(self, aValue):
		assert isinstance(aValue, Token) #Prune
		self.value = aValue

class ExpressionNode(Node):
	__slots__ = [
		"child", # *Node
	]

	def __init__(self, aChild):
		assert isinstance(aChild, Node) #Prune
		self.child = aChild

class FunctionCallArgumentNode(Node):
	__slots__ = [
		"identifier", # Identifier (optional)
		"value" # Expression
	]

	def __init__(self, aIdentifier, aValue):
		if aIdentifier: #Prune
			assert isinstance(aIdentifier, Identifier) #Prune
		assert isinstance(aValue, Expression) #Prune
		self.identifier = aIdentifier
		self.value = aValue

class FunctionCallNode(Node):
	__slots__ = [
		"identifier", # Identifier
		"arguments" # list of FunctionCallArgumentNode
	]

	def __init__(self, aIdentifier, aArguments):
		assert isinstance(aIdentifier, Identifier) #Prune
		assert isinstance(aArguments, list) #Prune
		self.identifier = aIdentifier
		self.arguments = aArguments

class IdentifierNode(Node):
	__slots__ = [
		"identifier" # Identifier
	]

	def __init__(self, aIdentifier):
		assert isinstance(aIdentifier, Identifier) #Prune
		self.identifier = aIdentifier

class LengthNode(Node):
	__slots__ = []

	def __init__(self):
		pass

class StructCreationNode(Node):
	__slots__ = [
		"identifier" # Identifier
	]

	def __init__(self, aIdentifier):
		assert isinstance(aIdentifier, Identifier) #Prune
		self.identifier = aIdentifier

class UnaryOperatorNode(Node):
	__slots__ = [
		"operator", # Token
		"operand" # *Node
	]

	def __init__(self, aOperator, aOperand):
		assert isinstance(aOperator, Token) #Prune
		assert isinstance(aOperand, Node) #Prune
		self.operator = aOperator
		self.operand = aOperand

class ExpressionStatement(object):
	__slots__ = [
		"expression", # Expression
		"line" # int
	]

	def __init__(self, aExpression):
		assert isinstance(aExpression, Expression) #Prune
		self.expression = aExpression

class FunctionParameter(object):
	__slots__ = [
		"identifier", # Identifier
		"type", # Type
		"defaultValue" # Expression
	]

	def __init__(self, aIdentifier, aType, aDefaultValue):
		assert isinstance(aIdentifier, Identifier) #Prune
		assert isinstance(aType, Type) #Prune
		assert isinstance(aDefaultValue, Expression) #Prune
		self.identifier = aIdentifier
		self.type = aType
		self.defaultValue = aDefaultValue

class FunctionFlags(object):
	__slots__ = [
		"isBetaOnly", # bool
		"isDebugOnly", # bool
		"isGlobal", # bool
		"isNative", # bool
	]

	def __init__(self, aBetaOnly, aDebugOnly, aGlobal, aNative):
		assert isinstance(aBetaOnly, bool) #Prune
		assert isinstance(aDebugOnly, bool) #Prune
		assert isinstance(aGlobal, bool) #Prune
		assert isinstance(aNative, bool) #Prune
		self.isBetaOnly = aBetaOnly
		self.isDebugOnly = aDebugOnly
		self.isGlobal = aGlobal
		self.isNative = aNative

class FunctionSignatureStatement(object):
	__slots__ = [
		"identifier", # Identifier
		"type", # Type
		"parameters", # list of FunctionParameter
		"flags", # FunctionFlags
		"line" # int
	]

	def __init__(self, aIdentifier, aType, aParameters, aFlags, aLine):
		assert isinstance(aIdentifier, Identifier) #Prune
		assert isinstance(aType, Type) #Prune
		assert isinstance(aParameters, list) #Prune
		assert isinstance(aFlags, FunctionFlags) #Prune
		assert isinstance(aLine, int) #Prune
		self.identifier = aIdentifier
		self.type = aType
		self.parameters = aParameters
		self.flags = aFlags
		self.line = aLine

class CustomEventStatement(object):
	__slots__ = [
		"identifier", # Identifier
		"line" # int
	]

	def __init__(self, aIdentifier, aLine):
		assert isinstance(aIdentifier, Identifier) #Prune
		assert isinstance(aLine, int) #Prune
		self.identifier = aIdentifier
		self.line = aLine

class DocstringStatement(object):
	__slots__ = [
		"value", # str
		"line" # int
	]

	def __init__(self, aValue, aLine):
		assert isinstance(aValue, str) #Prune
		assert isinstance(aLine, int) #Prune
		self.value = aValue
		self.line = aLine

class AssignmentStatement(object):
	__slots__ = [
		"operator", # Token
		"leftExpression", # ExpressionNode
		"rightExpression", # ExpressionNode
		"line" # int
	]

	def __init__(self, aOperator, aLeftExpression, aRightExpression, aLine):
		assert isinstance(aOperator, Token) #Prune
		assert isinstance(aLeftExpression, ExpressionNode) #Prune
		assert isinstance(aRightExpression, ExpressionNode) #Prune
		assert isinstance(aLine, int) #Prune
		self.operator = aOperator
		self.leftExpression = aLeftExpression
		self.rightExpression = aRightExpression
		self.line = aLine

class ElseStatement(object):
	__slots__ = [
		"line" # int
	]

	def __init__(self, aLine):
		assert isinstance(aLine, int) #Prune
		self.line = aLine

class ElseIfStatement(object):
	__slots__ = [
		"expression", # ExpressionNode
		"line" # int
	]

	def __init__(self, aExpression, aLine):
		assert isinstance(aExpression, ExpressionNode) #Prune
		assert isinstance(aLine, int) #Prune
		self.expression = aExpression
		self.line = aLine

class EndEventStatement(object):
	__slots__ = [
		"line" # int
	]

	def __init__(self, aLine):
		assert isinstance(aLine, int) #Prune
		self.line = aLine

class EndFunctionStatement(object):
	__slots__ = [
		"line" # int
	]

	def __init__(self, aLine):
		assert isinstance(aLine, int) #Prune
		self.line = aLine

class EndGroupStatement(object):
	__slots__ = [
		"line" # int
	]

	def __init__(self, aLine):
		assert isinstance(aLine, int) #Prune
		self.line = aLine

class EndIfStatement(object):
	__slots__ = [
		"line" # int
	]

	def __init__(self, aLine):
		assert isinstance(aLine, int) #Prune
		self.line = aLine

class EndPropertyStatement(object):
	__slots__ = [
		"line" # int
	]

	def __init__(self, aLine):
		assert isinstance(aLine, int) #Prune
		self.line = aLine

class EndStateStatement(object):
	__slots__ = [
		"line" # int
	]

	def __init__(self, aLine):
		assert isinstance(aLine, int) #Prune
		self.line = aLine

class EndStructStatement(object):
	__slots__ = [
		"line" # int
	]

	def __init__(self, aLine):
		assert isinstance(aLine, int) #Prune
		self.line = aLine

class EndWhileStatement(object):
	__slots__ = [
		"line" # int
	]

	def __init__(self, aLine):
		assert isinstance(aLine, int) #Prune
		self.line = aLine

class EventFlags(object):
	__slots__ = [
		"isNative" # bool
	]

	def __init__(self, aNative):
		assert isinstance(aNative, bool) #Prune
		self.isNative = aNative

class EventParameter(object):
	__slots__ = [
		"identifier", # Identifier
		"type", # Type
	]

	def __init__(self, aIdentifier, aType):
		assert isinstance(aIdentifier, Identifier) #Prune
		assert isinstance(aType, Type) #Prune
		self.identifier = aIdentifier
		self.type = aType

class EventSignatureStatement(object):
	__slots__ = [
		"identifier", # Identifier
		"remote", # Identifier
		"parameters", # list of EventParameter
		"flags", # EventFlags
		"line" # int
	]

	def __init__(self, aIdentifier, aRemote, aParameters, aFlags, aLine):
		assert isinstance(aIdentifier, Identifier) #Prune
		assert isinstance(aRemote, Identifier) #Prune
		assert isinstance(aParameters, list) #Prune
		assert isinstance(aFlags, EventFlags))
		assert isinstance(aLine, int) #Prune
		self.identifier = aIdentifier
		self.remote = aRemote
		self.parameters = aParameters
		self.flags = aFlags
		self.line = aLine

class GroupFlags(object):
	__slots__ = [
		"isCollapsed", # bool
		"isCollapsedOnBase", # bool
		"isCollapsedOnRef" # bool
	]

	def __init__(self, aCollapsed, aCollapsedOnBase, aCollapsedOnRef):
		assert isinstance(aCollapsed, bool) #Prune
		assert isinstance(aCollapsedOnBase, bool) #Prune
		assert isinstance(aCollapsedOnRef, bool) #Prune
		self.isCollapsed = aCollapsed
		self.isCollapsedOnBase = aCollapsedOnBase
		self.isCollapsedOnRef = aCollapsedOnRef

class GroupSignatureStatement(object):
	__slots__ = [
		"identifier", # Identifier
		"flags", # GroupFlags
		"line" # int
	]

	def __init__(self, aIdentifier, aFlags, aLine):
		assert isinstance(aIdentifier, Identifier) #Prune
		assert isinstance(aFlags, GroupFlags) #Prune
		assert isinstance(aLine, int) #Prune
		self.identifier = aIdentifier
		self.flags = aFlags
		self.line = aLine

class IfStatement(object):
	__slots__ = [
		"expression", # ExpressionNode
		"line" # int
	]

	def __init__(self, aExpression, aLine):
		assert isinstance(aExpression, ExpressionNode) #Prune
		assert isinstance(aLine, int) #Prune
		self.expression = aExpression
		self.line = aLine

class ImportStatement(object):
	__slots__ = [
		"identifier", # Identifier
		"line" # int
	]

	def __init__(self, aIdentifier, aLine):
		assert isinstance(aIdentifier, Identifier) #Prune
		assert isinstance(aLine, int) #Prune
		self.identifier = aIdentifier
		self.line = aLine

class PropertyFlags(object):
	__slots__ = [
		"isAuto", # bool
		"isAutoReadOnly", # bool
		"isConditional", # bool
		"isConst", # bool
		"isHidden", # bool
		"isMandatory" # bool
	]

	def __init__(self, aAuto, aAutoReadOnly, aConditional, aConst, aHidden, aMandatory):
		assert isinstance(aAuto, bool) #Prune
		assert isinstance(aAutoReadOnly, bool) #Prune
		assert isinstance(aConditional, bool) #Prune
		assert isinstance(aConst, bool) #Prune
		assert isinstance(aHidden, bool) #Prune
		assert isinstance(aMandatory, bool) #Prune
		self.isAuto = aAuto
		self.isAutoReadOnly = aAutoReadOnly
		self.isConditional = aConditional
		self.isConst = aConst
		self.isHidden = aHidden
		self.isMandatory = aMandatory

class PropertySignatureStatement(object):
	__slots__ = [
		"identifier", # Identifier
		"type", # Type
		"defaultValue", # ExpressionNode
		"line" # int
	]

	def __init__(self):
		pass
#RETURN
class (object):
	__slots__ = [
		"line" # int
	]

	def __init__(self):
		pass
#SCRIPTSIGNATURE
class (object):
	__slots__ = [
		"line" # int
	]

	def __init__(self):
		pass
#STATESIGNATURE
class (object):
	__slots__ = [
		"line" # int
	]

	def __init__(self):
		pass
#STRUCTSIGNATURE
class (object):
	__slots__ = [
		"line" # int
	]

	def __init__(self):
		pass
#VARIABLE
class (object):
	__slots__ = [
		"line" # int
	]

	def __init__(self):
		pass
#WHILE
class (object):
	__slots__ = [
		"line" # int
	]

	def __init__(self):
		pass
#	#Caprica extensions
#BREAK
class (object):
	__slots__ = [
		"line" # int
	]

	def __init__(self):
		pass
#CONTINUE
class (object):
	__slots__ = [
		"line" # int
	]

	def __init__(self):
		pass
#SWITCH
class (object):
	__slots__ = [
		"line" # int
	]

	def __init__(self):
		pass
#CASE
class (object):
	__slots__ = [
		"line" # int
	]

	def __init__(self):
		pass
#DEFAULT
class (object):
	__slots__ = [
		"line" # int
	]

	def __init__(self):
		pass
#ENDSWITCH
class (object):
	__slots__ = [
		"line" # int
	]

	def __init__(self):
		pass
#FOR
class (object):
	__slots__ = [
		"line" # int
	]

	def __init__(self):
		pass
#ENDFOR
class (object):
	__slots__ = [
		"line" # int
	]

	def __init__(self):
		pass
#FOREACH
class (object):
	__slots__ = [
		"line" # int
	]

	def __init__(self):
		pass
#ENDFOREACH
class (object):
	__slots__ = [
		"line" # int
	]

	def __init__(self):
		pass
#DO
class (object):
	__slots__ = [
		"line" # int
	]

	def __init__(self):
		pass
#LOOPWHILE
class (object):
	__slots__ = [
		"line" # int
	]

	def __init__(self):
		pass