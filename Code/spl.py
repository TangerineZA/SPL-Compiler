# Imports
import re

# Tokens
TT_NUMBER = 'NUMBER'
TT_USERDEFINEDNAME = 'USERDEFINEDNAME'
TT_SHORTSTRING = 'SHORTSTRING'
TT_LSQUAREBRACKET = 'LSQUAREBRACKET'
TT_RSQUAREBRACKET = 'RSQUAREBRACKET'
TT_LBRACE = 'LBRACE'
TT_RBRACE = 'RBRACE'
TT_LBRACKET = 'LBRACKET'
TT_RBRACKET = 'RBRACKET'
TT_COMMA = 'COMMA'
TT_SEMICOLON = 'SEMICOLON'
TT_KEYWORD = 'KEYWORD'

# TODO: add TT_BOOL

WHITESPACES = ' \t\n'
KEYWORDS = ['arr', 'sub', 'mult', 'add', 'larger', 'eq', 'or', 'and', 'not',
            'input', 'true', 'false', 'if', 'then', 'else', 'proc', 'main',
            'return', 'halt', 'num', 'bool', 'string']
NUMBER_REGEX = '^[0-9]*[.,]{0,1}[0-9]*$'
SHORT_STRING_REGEX = '^([A-Z][ ][0-9]){0,15}$'
USER_DEFINED_NAME_REGEX = '[a-z].([a-z] | [0-9])*'
BOOLEAN_WORDS = ['true', 'false']


class Token:
    def __init__(self, token_type, token_id, contents):
        self.type = token_type
        self.contents = contents
        self.id = token_id

    def __repr__(self):
        if self.contents:
            return f'{self.type}:{self.contents}'
        return f'{self.type}'


# Lexer
class Lexer:
    def __init__(self, text):
        self.text = text
        self.splitText = text.split()
        self.tokens = []

    def break_up(self, full_word):
        constructed_word = ''
        for x in range(0, len(full_word)):
            current_char = full_word[x]
            if constructed_word in KEYWORDS:
                self.tokens.append(Token(TT_KEYWORD, len(self.tokens), constructed_word))
                constructed_word = ''
            elif current_char == ',':
                self.tokens.append(Token(TT_COMMA, len(self.tokens)))
            elif current_char == ';':
                self.tokens.append(Token(TT_SEMICOLON, len(self.tokens)))
            elif current_char == '(':
                self.tokens.append(Token(TT_LBRACKET, len(self.tokens)))
            elif current_char == ')':
                self.tokens.append(Token(TT_RBRACKET, len(self.tokens)))
            elif current_char == '{':
                self.tokens.append(Token(TT_LBRACE, len(self.tokens)))
            elif current_char == '}':
                self.tokens.append(Token(TT_RBRACE, len(self.tokens)))
            elif current_char == '[':
                self.tokens.append(Token(TT_LSQUAREBRACKET, len(self.tokens)))
            elif current_char == ']':
                self.tokens.append(Token(TT_RSQUAREBRACKET, len(self.tokens)))
            elif full_word in KEYWORDS:
                self.tokens.append(Token(TT_KEYWORD, len(self.tokens), full_word))
            # Assume there's more word to add and check
            elif x != len(full_word):
                constructed_word = constructed_word.join(constructed_word, current_char)
            # Assume there is nothing left to add and check in constructed word - must be complete item
            elif x == len(full_word):
                if re.search(NUMBER_REGEX, constructed_word) is not None:
                    self.tokens.append(Token(TT_NUMBER, len(self.tokens), constructed_word))
                elif re.search(SHORT_STRING_REGEX, constructed_word) is not None:
                    self.tokens.append(Token(TT_SHORTSTRING, len(self.tokens), constructed_word))
                elif re.search(USER_DEFINED_NAME_REGEX, constructed_word) is not None:
                    self.tokens.append(Token(TT_USERDEFINEDNAME, len(self.tokens), constructed_word))
            else:
                print("UNRECOGNISED WORD: " + full_word)
                return False

    def runLexer(self):
        split_text = self.text.split()
        for x in range(len(split_text)):
            if not self.break_up(split_text[x]):
                return False
        print(self.tokens)
        return True


# Nodes
NT_SPLPROGRAM = 'SPLProgram'
NT_PROCDEFS = 'ProcedureDefinitions'
NT_ALGORITHM = 'Algorithm'
NT_TYP = 'TYP'
NT_VAR = 'Var'
NT_CONST = 'Const'
NT_LHS = 'LHS'
NT_LOOP = 'Loop'
NT_EXPR = 'Expr'
NT_PCALL = 'PCall'
NT_FIELD = 'Field'
NT_UNOP = 'UnOp'
NT_BINOP = 'BinOp'
NT_DEC = 'Dec'
NT_VARDECL = 'VarDecl'

TYP_WORDS = ['num', 'bool', 'string']

class Node:
    # Node class contains:
    # - ID (number, incremented for each node added)
    # - Node class (String, descriptor of node type)
    # - Node contents (Array of sub-nodes if parent node, or pointer to token if leaf)
    def __init__(self, node_id, node_class, node_contents):
        self.node_id = node_id
        self.node_class = node_class
        self.node_contents = node_contents

    def __repr__(self):
        return f'{self.node_id}:{self.node_class}:{self.node_contents}'


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.token_index = -1
        self.current_token = None
        self.advance()
        self.numNodes = 0

    def advance(self):
        self.token_index += 1
        if self.token_index < len(self.tokens):
            self.current_token = self.tokens[self.token_index]

    def TYP(self):
        token = self.current_token

        if token.type == TT_KEYWORD and token.contents in TYP_WORDS:
            self.advance()
            self.numNodes += 1
            return Node(self.numNodes, NT_TYP, token)

    def Var(self):
        token = self.current_token
        if token.type == TT_USERDEFINEDNAME:
            self.advance()
            self.numNodes += 1
            return Node(self.numNodes, NT_VAR, token)

    def Const(self):
        token = self.current_token
        if token.type in (TT_NUMBER, TT_SHORTSTRING) or (token.type == TT_KEYWORD and token.contents in BOOLEAN_WORDS):
            self.advance()
            self.numNodes += 1
            return Node(self.numNodes, NT_TYP, token)

    def Dec(self):
        # branching based on two possible Dec types:
        # 1 - arr $TYP[$Const] $Var
        # 2 - $TYP $Var

        children = []

        if self.current_token.type == TT_KEYWORD and self.current_token.contents == 'arr':
            self.advance()
            children.append(self.TYP())
            if self.current_token.type == TT_LSQUAREBRACKET:
                self.advance()
                children.append(self.Const())
                if self.current_token.type == TT_RSQUAREBRACKET:
                    self.advance()
                    children.append(self.Var())
                else:
                    self.parser_error()
            else:
                self.parser_error()

        elif self.current_token.type == TT_KEYWORD and self.current_token.contents in TYP_WORDS:

            children.append(self.TYP())
            children.append(self.Var())

        return Node(self.numNodes. NT_DEC, children)

    def SPLProgrm(self):

        pass

    def VarDecl(self):

        pass

    def BinOp(self):
        pass

    def UnOp(self):
        pass

    def Const(self):
        pass

    def Field(self):
        pass

    def Var(self):
        pass

    def PCall(self):
        pass

    def Expr(self):
        pass

    def LHS(self):
        pass

    def Loop(self):
        pass

    def Alternat(self):
        pass

    def parser_error(self):
        print('Parser Error!')
        #TODO: fill out with descriptive error message


class Error:
    def __init__(self, error_name, details):
        self.error_name = error_name
        self.details = details

    def as_string(self):
        result = f'{self.error_name}: {self.details}'
        return result
