# Imports
import os
import sys
import re
import copy

# Token type constants
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
TT_ASSIGNMENTOPERATOR = 'ASSIGNMENT_OPERATOR'

# Token convenience constants
WHITESPACES = ' \t\n'
KEYWORDS = ['arr', 'sub', 'mult', 'add', 'larger', 'eq', 'or', 'and', 'not',
            'input', 'true', 'false', 'if', 'then', 'else', 'proc', 'main',
            'return', 'halt', 'num', 'bool', 'string']
BRACKETED_WORDS = ['and(', 'or(', 'eq(', 'larger(', 'add(', 'sub(', 'mult(', 'input(', 'not(']
NUMBER_REGEX = '^[0-9]*[.,]{0,1}[0-9]*$'
SHORT_STRING_REGEX = '^([A-Z][ ][0-9]){0,15}$'
USER_DEFINED_NAME_REGEX = '[a-z].([a-z] | [0-9])*'
BOOLEAN_WORDS = ['true', 'false']


class Token:

    # The Token class uses the recommended tuple to contain three pieces of information:
    # 1 - the type of token
    # 2 - the contents of the token (i.e., the actual word)
    # 3 - the ID of the token for unique identification purposes

    def __init__(self, token_type, token_id, contents):
        self.type = token_type
        self.contents = contents
        self.id = token_id

    def __repr__(self):
        if self.contents:
            return f'{self.type}: {self.contents}, ID: {self.id}'
        return f'{self.type}'


# Lexer
class Lexer:
    def __init__(self, text: str):
        self.text = text
        self.tokens = []

    def break_up_and_split(self, full_text: str):
        split = full_text.split()

        for full_word in split:
            if full_word in KEYWORDS:
                self.tokens.append(Token(TT_KEYWORD, len(self.tokens), full_word))
                print('Added token ' + full_word + ' of type ' + TT_KEYWORD)
            elif full_word == ',':
                self.tokens.append(Token(TT_COMMA, len(self.tokens), ','))
                print('Added token ' + full_word + ' of type ' + TT_COMMA)
            elif full_word == ';':
                self.tokens.append(Token(TT_SEMICOLON, len(self.tokens), ';'))
                print('Added token ' + full_word + ' of type ' + TT_SEMICOLON)
            elif full_word == '(':
                self.tokens.append(Token(TT_LBRACKET, len(self.tokens), '('))
                print('Added token ' + full_word + ' of type ' + TT_LBRACKET)
            elif full_word == ')':
                self.tokens.append(Token(TT_RBRACKET, len(self.tokens), ')'))
                print('Added token ' + full_word + ' of type ' + TT_RBRACKET)
            elif full_word == '{':
                self.tokens.append(Token(TT_LBRACE, len(self.tokens), '{'))
                print('Added token ' + full_word + ' of type ' + TT_LBRACE)
            elif full_word == '}':
                self.tokens.append(Token(TT_RBRACE, len(self.tokens), '}'))
                print('Added token ' + full_word + ' of type ' + TT_RBRACE)
            elif full_word == '[':
                self.tokens.append(Token(TT_LSQUAREBRACKET, len(self.tokens), '['))
                print('Added token ' + full_word + ' of type ' + TT_LSQUAREBRACKET)
            elif full_word == ']':
                self.tokens.append(Token(TT_RSQUAREBRACKET, len(self.tokens), ']'))
                print('Added token ' + full_word + ' of type ' + TT_RSQUAREBRACKET)
            elif full_word == ':=':
                self.tokens.append(Token(TT_ASSIGNMENTOPERATOR, len(self.tokens), ':='))
                print('Added token ' + full_word + ' of type ' + TT_ASSIGNMENTOPERATOR)
            elif re.search(NUMBER_REGEX, full_word) is not None:
                self.tokens.append(Token(TT_NUMBER, len(self.tokens), full_word))
                print('Added token ' + full_word + ' of type ' + TT_NUMBER)
            elif re.search(SHORT_STRING_REGEX, full_word) is not None:
                self.tokens.append(Token(TT_SHORTSTRING, len(self.tokens), full_word))
                print('Added token ' + full_word + ' of type ' + TT_SHORTSTRING)
            elif re.search(USER_DEFINED_NAME_REGEX, full_word) is not None:
                self.tokens.append(Token(TT_USERDEFINEDNAME, len(self.tokens), full_word))
                print('Added token ' + full_word + ' of type ' + TT_USERDEFINEDNAME)
            else:
                self.subdivide(full_word)

    def subdivide(self, full_word):
        if full_word in BRACKETED_WORDS:
            fixed_word = full_word[:-1]
            self.tokens.append(Token(TT_KEYWORD, len(self.tokens), fixed_word))
            print('Added token ' + fixed_word + ' of type ' + TT_KEYWORD)
            self.tokens.append(Token(TT_LBRACKET, len(self.tokens), '('))
        else:
            self.advanced_subdivide(full_word)

    def advanced_subdivide(self, full_word):
        word_list = []
        partial_list = full_word.split('(')
        for part_word in partial_list:
            if part_word.contains(')'):
                partial_list.append(part_word.split(')'))
                partial_list.remove(part_word)
        word_list = partial_list
        if word_list[0] in BINOP_WORDS:
            self.tokens.append(Token(TT_KEYWORD, len(self.tokens), word_list[0]))
        elif word_list[0] in ('input', 'not'):
            self.tokens.append(Token(TT_KEYWORD, len(self.tokens), word_list[0]))
        if word_list[1] == '(':
            self.tokens.append(Token(TT_LBRACKET, len(self.tokens), word_list[1]))
        self.tokens.append(Token(TT_KEYWORD, len(self.tokens), word_list[2]))
        if word_list[3] == ',':
            self.tokens.append(Token(TT_COMMA, len(self.tokens), word_list[3]))
            self.tokens.append(Token(TT_KEYWORD, len(self.tokens), word_list[4]))
            self.tokens.append(Token(TT_RBRACKET, len(self.tokens), word_list[5]))
        elif word_list[3] == ')':
            self.tokens.append(Token(TT_RBRACKET, len(self.tokens), word_list[3]))



    def break_up(self, full_word):
        if re.search(NUMBER_REGEX, full_word) is not None:
            self.tokens.append(Token(TT_NUMBER, len(self.tokens), full_word))
        elif re.search(SHORT_STRING_REGEX, full_word) is not None:
            self.tokens.append(Token(TT_SHORTSTRING, len(self.tokens), full_word))
        elif re.search(USER_DEFINED_NAME_REGEX, full_word) is not None:
            self.tokens.append(Token(TT_USERDEFINEDNAME, len(self.tokens), full_word))
        elif full_word in KEYWORDS:
            self.tokens.append(Token(TT_KEYWORD, len(self.tokens), full_word))
            exit()

        constructed_word = ''
        print(full_word)
        for x in range(0, len(full_word)):
            print(x)
            current_char = full_word[x]
            if constructed_word in KEYWORDS:
                self.tokens.append(Token(TT_KEYWORD, len(self.tokens), constructed_word))
                constructed_word = ''
            elif current_char == ',':
                self.tokens.append(Token(TT_COMMA, len(self.tokens), ','))
            elif current_char == ';':
                self.tokens.append(Token(TT_SEMICOLON, len(self.tokens), ';'))
            elif current_char == '(':
                self.tokens.append(Token(TT_LBRACKET, len(self.tokens), '('))
            elif current_char == ')':
                self.tokens.append(Token(TT_RBRACKET, len(self.tokens), ')'))
            elif current_char == '{':
                self.tokens.append(Token(TT_LBRACE, len(self.tokens), '{'))
            elif current_char == '}':
                self.tokens.append(Token(TT_RBRACE, len(self.tokens), '}'))
            elif current_char == '[':
                self.tokens.append(Token(TT_LSQUAREBRACKET, len(self.tokens), '['))
            elif current_char == ']':
                self.tokens.append(Token(TT_RSQUAREBRACKET, len(self.tokens), ']'))
            elif current_char == ':' and full_word[x + 1] == '=':
                self.tokens.append(Token(TT_ASSIGNMENTOPERATOR, len(self.tokens), ':='))
            elif full_word in KEYWORDS:
                self.tokens.append(Token(TT_KEYWORD, len(self.tokens), full_word))
            # Assume there's more word to add and check
            elif x != len(full_word):
                constructed_word = constructed_word.join(constructed_word, current_char)
                print('lexer iteration of x is at: ' + str(x))
            # Assume there is nothing left to add and check in constructed word - must be complete item
            elif x == len(full_word):
                if re.search(NUMBER_REGEX, constructed_word) is not None:
                    self.tokens.append(Token(TT_NUMBER, len(self.tokens), constructed_word))
                elif re.search(SHORT_STRING_REGEX, constructed_word) is not None:
                    self.tokens.append(Token(TT_SHORTSTRING, len(self.tokens), constructed_word))
                elif re.search(USER_DEFINED_NAME_REGEX, constructed_word) is not None:
                    self.tokens.append(Token(TT_USERDEFINEDNAME, len(self.tokens), constructed_word))
            else:
                print('Lexer error!')
                print('UNRECOGNISED WORD: ' + full_word)
                quit()

    def run_lexer(self):
        self.break_up_and_split(self.text)
        print('\nLEXER OUTPUT:')
        for token in self.tokens:
            print(token)
        return self.tokens


# Node type constants
NT_SPLPROGRAM = 'SPLProgram'
NT_PROCDEFS = 'ProcedureDefinitions'
NT_ALGORITHM = 'Algorithm'
NT_ALTERNAT = 'Alternat'
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
NT_KEYWORD = 'Keyword'
NT_USERDEFINEDNAME = 'UserDefinedName'
NT_PD = 'PD'
NT_INSTR = 'Instruction'
NT_ASSIGN = 'Assignment'
NT_BRANCH = 'Branch'

# Node convenience constants
TYP_WORDS = ['num', 'bool', 'string']
BINOP_WORDS = ['and', 'or', 'eq', 'larger', 'add', 'sub', 'mult']


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
        return f'\n{self.node_id}:{self.node_class}:{self.node_contents}'

    def has_children(self):
        return isinstance(self.node_contents, list)


class Parser:
    def __init__(self, tokens: list):
        self.tokens = tokens
        self.token_index = -1
        self.current_token = None
        self.advance()
        self.num_nodes = 0

    def advance(self):
        # print('Advancing through tokens list...')
        self.token_index += 1
        if self.token_index < len(self.tokens):
            self.current_token = self.tokens[self.token_index]

    def Keyword(self):
        print('Adding Keyword: ' + self.current_token.contents)
        # Leaf node
        token = self.current_token
        if token.type == TT_KEYWORD:
            self.advance()
            self.num_nodes += 1
            return Node(self.num_nodes, NT_KEYWORD, token)
        else:
            self.parser_error()

    def UserDefinedName(self):
        print('Adding UserDefinedName')
        # Leaf node
        token = self.current_token
        if token.type == TT_USERDEFINEDNAME:
            self.advance()
            self.num_nodes += 1
            return Node(self.num_nodes, NT_USERDEFINEDNAME, token)

    def TYP(self):
        print('Adding TYP')
        # Leaf node
        token = self.current_token
        if token.type == TT_KEYWORD and token.contents in TYP_WORDS:
            self.advance()
            self.num_nodes += 1
            return Node(self.num_nodes, NT_TYP, token)

    def Var(self):
        print('Adding Var')
        # Leaf node
        token = self.current_token
        if token.type == TT_USERDEFINEDNAME:
            self.advance()
            self.num_nodes += 1
            new_node = Node(self.num_nodes, NT_VAR, token)
            return new_node

    def Const(self):
        print('Adding Const')
        # Leaf node
        token = self.current_token
        if token.type in (TT_NUMBER, TT_SHORTSTRING) or (token.type == TT_KEYWORD and token.contents in BOOLEAN_WORDS):
            self.advance()
            self.num_nodes += 1
            return Node(self.num_nodes, NT_TYP, token)

    def Dec(self):
        print('Adding Dec')
        # Compound node

        # Branching based on two possible Dec types:
        # 1 - arr $TYP[$Const] $Var
        # 2 - $TYP $Var

        # Children structure:
        # 1 - Keyword TYP Const Var
        # 2 - TYP Var

        children = []
        if self.current_token.type == TT_KEYWORD and self.current_token.contents == 'arr':
            print('Adding array')
            children.append(self.Keyword())
            children.append(self.TYP())
            if self.current_token.type == TT_LSQUAREBRACKET:
                self.advance()
                children.append(self.Const())
                if self.current_token.type == TT_RSQUAREBRACKET:
                    self.advance()
                    children.append(self.Var())
                    self.num_nodes += 1
                    return Node(self.num_nodes, NT_DEC, children)
        elif self.current_token.type == TT_KEYWORD and self.current_token.contents in TYP_WORDS:
            # print('Adding normal TYP VAR')
            children.append(self.TYP())
            # print('Added TYP in Dec')
            children.append(self.Var())
            # print('Added Var in Dec')
            self.num_nodes += 1
            print('Exiting Dec')
            return Node(self.num_nodes, NT_DEC, children)
        else:
            print('No type entered!')
            self.parser_error()

    vardec_recursion_layer = -1

    def VarDecl(self):
        self.vardec_recursion_layer += 1
        # print('Adding VarDecl - current recursion layer = ' + self.vardec_recursion_layer.__str__())
        # Compound node

        # Branching because nullable
        # 1 - Dec ; VarDecl
        # 2 - nothing

        # Children structure:
        # [1] - Declaration
        # [2] - Variable Declaration

        children = []
        if self.current_token.contents not in TYP_WORDS:
            return None

        dec = self.Dec()
        if dec is not None:
            # print('Appending Dec to VarDecl children')
            children.append(dec)
            # print('Present token: ' + self.current_token.type + ': ' + self.current_token.contents)
            if self.current_token.type == TT_KEYWORD and self.current_token.contents in TYP_WORDS:
                print('Recursively adding more variable declarations...')
                if self.current_token.contents in TYP_WORDS:
                    children.append(self.VarDecl())
                self.num_nodes += 1
                # print('Exiting VarDecl via return of Node - exiting layer: ' + self.vardec_recursion_layer.__str__())
                self.vardec_recursion_layer -= 1
                return Node(self.num_nodes, NT_VARDECL, children)

    def BinOp(self):
        print('Adding BinOp')
        # Compound node

        # No branching

        # Children structure:
        # Keyword leaf node - indicating which binary operation is occurring
        # Expression child node for first argument
        # Expression child node for second argument

        children = []
        if self.current_token.type == TT_KEYWORD and self.current_token.contents in BINOP_WORDS:
            children.append(self.Keyword())
            if self.current_token.type == TT_LBRACKET:
                self.advance()
                children.append(self.Expr())
                if self.current_token.type == TT_COMMA:
                    self.advance()
                    children.append(self.Expr())
                    if self.current_token.type == TT_RSQUAREBRACKET:
                        self.num_nodes += 1
                        return Node(self.num_nodes, NT_BINOP, children)

        self.parser_error()
        return None

    def UnOp(self):
        print('Adding UnOp')
        # Compound node

        # Branching based on which operator
        # 1 - input(Var)
        # 2 - not(Expr)

        # Children structure:
        # Keyword leaf node
        # Var child node if branch 1
        # Expr child node if branch 2

        children = []
        if self.current_token.type == TT_KEYWORD:
            # Save the operator for branching
            operator = self.current_token.contents
            children.append(self.Keyword())
            if self.current_token.type == TT_LBRACKET:
                self.advance()
                if operator == 'input':  # Branch 1
                    children.append(self.Var())
                elif operator == 'not':  # Branch 2
                    children.append(self.Expr())
                self.num_nodes += 1
                return Node(self.num_nodes, NT_UNOP, children)
            else:
                self.parser_error()
        else:
            self.parser_error()
            return None

    def Field(self):
        print('Adding Field')
        # Compound node

        # Branching based on Variable or Constant or just name
        # 1 - userDefinedName[Var]
        # 2 - userDefinedName[Const]

        # Children structure:
        # Name leaf node
        # Var child node if branch 1
        # Const child node if branch 2

        children = []
        if self.current_token.type == TT_USERDEFINEDNAME:
            self.num_nodes += 1
            children.append(self.UserDefinedName())
            self.advance()
            if self.current_token.type == TT_LSQUAREBRACKET:
                children.append(self.Var())
                if self.current_token.type == TT_RSQUAREBRACKET:
                    self.num_nodes += 1
                    return Node(self.num_nodes, NT_FIELD, children)
                else:
                    self.parser_error()
                    return None
            else:
                self.parser_error()
                return None
        else:
            self.parser_error()
            return None

    def PCall(self):
        print('Adding PCall')
        # Compound node

        # No branching

        # Children structure:
        # Keyword ('call')
        # Var (the user defined name)

        children = []

        if self.current_token.type == TT_KEYWORD and self.current_token.contents == 'call':
            children.append(self.Keyword())
            self.advance()
            if self.current_token.type == TT_USERDEFINEDNAME:
                children.append(self.Var())
                self.num_nodes += 1
                return Node(self.num_nodes, NT_PCALL, children)
            else:
                self.parser_error()
                return None
        else:
            self.parser_error()
            return None

    def Expr(self):
        print('Adding Expr')
        # Compound node

        # Branching based on which node type the expression consists of
        # 1 - Const
        # 2 - Var
        # 3 - Field
        # 4 - UnOp
        # 5 - BinOp

        # Children structure:
        # Merely a single child consisting of the node making up this expression

        children = []

        const = self.Const()
        if const is not None:
            children.append(const)
            self.num_nodes += 1
            return Node(self.num_nodes, NT_EXPR, children)
        else:
            var = self.Var()
            if var is not None:
                children.append(var)
                self.num_nodes += 1
                return Node(self.num_nodes, NT_EXPR, children)
            else:
                field = self.Field()
                if field is not None:
                    children.append(field)
                    self.num_nodes += 1
                    return Node(self.num_nodes, NT_EXPR, children)
                else:
                    unop = self.UnOp()
                    if unop is not None:
                        children.append(unop)
                        self.num_nodes += 1
                        return Node(self.num_nodes, NT_EXPR, children)
                    else:
                        binop = self.BinOp()
                        if binop is not None:
                            children.append(binop)
                            self.num_nodes += 1
                            return Node(self.num_nodes, NT_EXPR, children)
                        else:
                            self.parser_error()
                            return None

    def LHS(self):
        print('Adding LHS')
        # Compound node

        # Branching based on types
        # 1 - output
        # 2 - Field
        # 3 - Var

        # Children structure:
        # If branch 1: simply the keyword token
        # If branch 2: the Field node
        # If branch 3: the Var node

        token = self.current_token
        children = []
        if token.type == TT_KEYWORD and token.contents == 'output':
            self.num_nodes += 1
            self.advance()
            return Node(self.num_nodes, NT_LHS, token)
        elif token.type == TT_USERDEFINEDNAME:
            if self.tokens[self.token_index + 1].type == TT_LSQUAREBRACKET:
                children.append(self.Field())
            else:
                children.append(self.Var())
            self.num_nodes += 1
            return Node(self.num_nodes, NT_LHS, children)
        else:
            self.parser_error()
            return None

    def Loop(self):
        print('Adding loop')
        # Compound node

        # Branching:
        # 1 - do { Algorithm } until (Expr)
        # 2 -  while (Expr) do { Algorithm }

        # Children:
        # if branch 1:
        # Keyword, Algorithm, Keyword, Expr
        # if branch 2:
        # Keyword, Expr, Keyword, Algorithm

        children = []

        # Branch 1
        if self.current_token.type == TT_KEYWORD and self.current_token.contents == 'do':
            children.append(self.Keyword())
            if self.current_token.type == TT_LBRACE:
                self.advance()
                children.append(self.Algorithm())
                if self.current_token.type == TT_RBRACE:
                    self.advance()
                    if self.current_token.type == TT_KEYWORD and self.current_token.contents == 'until':
                        children.append(self.Keyword())
                        if self.current_token.type == TT_RBRACKET:
                            self.advance()
                            children.append(self.Expr())
                            if self.current_token.type == TT_LBRACKET:
                                self.num_nodes += 1
                                return Node(self.num_nodes, NT_LOOP, children)
        elif True:
            if self.current_token.type == TT_KEYWORD and self.current_token.contents == 'while':
                children.append(self.Keyword())
                if self.current_token.type == TT_LBRACKET:
                    self.advance()
                    children.append(self.Expr())
                    if self.current_token.type == TT_RBRACKET:
                        self.advance()
                        if self.current_token.type == TT_KEYWORD and self.current_token.contents == 'do':
                            children.append(self.Keyword())
                            if self.current_token.type == TT_LBRACE:
                                self.advance()
                                children.append(self.Algorithm())
                                if self.current_token.type == TT_RBRACE:
                                    self.num_nodes += 1
                                    return Node(self.num_nodes, NT_LOOP, children)

        # lazy approach to error handling is okay here - if not returning, will throw error,
        # i.e. will reach this parser_error() at the bottom

        self.parser_error()
        return None

    def Alternat(self):
        print('Adding alternat')
        # Compound node

        # Branch on nullable

        # Children:
        # Keyword Algorithm

        children = []

        if self.current_token.type == TT_KEYWORD and self.current_token.contents == 'else':
            children.append(self.Keyword())
            if self.current_token.type == TT_LBRACE:
                self.advance()
                children.append(self.Algorithm())  # lazy!! don't be like this! do error checking!
                if self.current_token.type == TT_RBRACE:
                    self.num_nodes += 1
                    return Node(self.num_nodes, NT_ALTERNAT, children)
            self.parser_error()
        else:
            pass

    def Branch(self):
        print('Adding branch')
        # Compound node

        # No branching

        # Children:
        # Keyword Expr Keyword Algorithm Alternat

        children = []

        if self.current_token.type == TT_KEYWORD and self.current_token.contents == 'if':
            children.append(self.Keyword())
            if self.current_token.type == TT_LBRACKET:
                self.advance()
                if self.current_token.type == TT_RBRACKET:
                    self.advance()
                    if self.current_token.type == TT_KEYWORD and self.current_token.contents == 'then':
                        children.append(self.Keyword())
                        if self.current_token.type == TT_LBRACE:
                            self.advance()
                            children.append(self.Algorithm())
                            if self.current_token.type == TT_RBRACE:
                                self.advance()
                                children.append(self.Alternat())

        self.parser_error()

    def Assign(self):
        print('Adding assignment')

        # Compound node

        # No branching

        # Children:
        # LHS Expr

        children = []

        children.append(self.LHS())
        if self.current_token.type == TT_ASSIGNMENTOPERATOR:
            self.advance()
            children.append(self.Expr())
            self.num_nodes += 1
            return Node(self.num_nodes, NT_ASSIGN, children)
        self.parser_error()
        return None

    def Instr(self):
        print('Adding Instruction')
        # Compound node

        # Branching:
        # 1 - Assign
        # 2 - Branch
        # 3 - Loop
        # 4 - PCall

        # Children:
        # Whichever branch is taken is the only child
        # Can return None for ease of working Algorithm

        children = []

        if self.current_token.type == TT_USERDEFINEDNAME or (
                self.current_token.type == TT_KEYWORD and self.current_token.contents == 'output'):
            children.append(self.Assign())
            self.num_nodes += 1
            print('Exiting instruction')
            return Node(self.num_nodes, NT_INSTR, children)
        elif self.current_token.type == TT_KEYWORD and self.current_token.contents == 'if':
            children.append(self.Branch())
            self.num_nodes += 1
            print('Exiting instruction')
            return Node(self.num_nodes, NT_INSTR, children)
        elif self.current_token.type == TT_KEYWORD and self.current_token.contents in ('do', 'loop'):
            children.append(self.Loop())
            self.num_nodes += 1
            print('Exiting instruction')
            return Node(self.num_nodes, NT_INSTR, children)
        elif self.current_token.type == TT_KEYWORD and self.current_token.contents == 'call':
            children.append(self.PCall())
            self.num_nodes += 1
            print('Exiting instruction')
            return Node(self.num_nodes, NT_INSTR, children)

        self.parser_error()

    def Algorithm(self):
        print('Adding Algorithm')
        # Compound

        # Branching based on nullable

        # Children:
        # Instr Algorithm

        children = []

        if self.current_token.type == TT_KEYWORD:
            # So if there is likely to be an instruction type
            if self.current_token.contents in ('do', 'loop', 'call', 'if'):

                if self.current_token.contents == 'do':
                    children.append(Node(0, NT_LOOP), None)
                elif self.current_token.contents == 'loop':
                    children.append(Node(0, NT_LOOP), None)
                elif self.current_token.contents == 'call':
                    children.append(Node(0, NT_PCALL), None)
                elif self.current_token.contents == 'if':
                    children.append(Node(0, NT_BRANCH), None)

                children.append(self.Instr())
                if self.current_token.type == TT_SEMICOLON:
                    self.advance()
                    children.append(self.Algorithm())
                    self.num_nodes += 1
                    return Node(self.num_nodes, NT_ALGORITHM, children)
        else:
            print('Algorithm is assignment operation')
            children.append(self.Assign())
            self.num_nodes += 1
            print('Exiting algorithm')
            return Node(self.num_nodes, NT_ALGORITHM, children)

        print('Algorithm null')

    def PD(self):
        print('Adding PD')
        print('Current token: ' + self.current_token.type + ':' + self.current_token.contents)
        # Compound

        # No branching - just:
        # 1 - PD → proc userDefinedName { ProcDefs Algorithm return ; VarDecl }

        # Children:
        # Keyword Var ProcDefs Algorithm Keyword VarDecl

        children = []

        if self.current_token.type == TT_KEYWORD and self.current_token.contents == 'proc':
            children.append(self.Keyword())
            if self.current_token.type == TT_USERDEFINEDNAME:
                children.append(self.Var())
                if self.current_token.type == TT_LBRACE:
                    self.advance()
                    # print('PD adding own ProcDefs now')
                    children.append(self.ProcDefs())
                    # print('PD ProcDefs done! Entering PD Algorithm')
                    children.append(self.Algorithm())
                    # print('ProcDefs and Algorithm done in PD... moving on to return value!')
                    if self.current_token.type == TT_KEYWORD and self.current_token.contents == 'return':
                        children.append(self.Keyword())
                        if self.current_token.type == TT_SEMICOLON:
                            self.advance()
                            children.append(self.VarDecl())
                            # print('PD done with variable declarations')
                            # print('Current token type: ' + self.current_token.type)
                            if self.current_token.type == TT_RBRACE:
                                self.advance()
                                self.num_nodes += 1
                                print('Exiting PD')
                                return Node(self.num_nodes, NT_PD, children)
        else:
            # print('PROCDEFS PASS')
            pass
        self.parser_error()

    def ProcDefs(self):
        print('Adding ProcDefs')
        # Compound

        # Branching on nullable

        # Children:
        # PD ProcDefs

        tokens_copy = self.get_fresh_token_list_copy()
        current_token_copy = tokens_copy[self.token_index]
        if current_token_copy.type != TT_KEYWORD or current_token_copy.contents != 'proc':
            print('ProcDefs null')
            return None

        children = []

        children.append(self.PD())
        if self.current_token.type == TT_COMMA:
            self.advance()
            children.append(self.ProcDefs())
            self.num_nodes += 1
            print('Exiting ProcDefs')
            return Node(self.num_nodes, NT_PROCDEFS, children)
        else:
            return Node(self.num_nodes, NT_PROCDEFS, children)

    def SPLProgr(self):
        print('Adding SPL program')
        # Compound

        # No branching - only:
        # ProcDefs main { Algorithm halt ; VarDecl }

        # Children:
        # ProcDefs Keyword Algorithm Keyword VarDecl

        children = []

        children.append(self.ProcDefs())
        print('Current token: ' + self.current_token.contents)
        if self.current_token.type == TT_KEYWORD and self.current_token.contents == 'main':
            children.append(self.Keyword())
            if self.current_token.type == TT_LBRACE:
                self.advance()
                children.append(self.Algorithm())
                if self.current_token.type == TT_KEYWORD and self.current_token.contents == 'halt':
                    children.append(self.Keyword())
                    if self.current_token.type == TT_SEMICOLON:
                        self.advance()
                        children.append(self.VarDecl())
                        print('Program variable declarations complete!')
                        if self.current_token.type == TT_RBRACE:
                            self.num_nodes += 1
                            return Node(self.num_nodes, NT_SPLPROGRAM, children)

        self.parser_error()

    def run_parser(self):
        # Runs recursive descent parser

        # Gets Node object of program and recursively steps down through each child node

        # Returns program's Node object

        program_node = self.SPLProgr()

        print(program_node)

        return program_node

    def parser_error(self, node_type=None):
        error_token = self.current_token
        error_token_index = self.token_index

        print('Parser Error!')
        print('Error occurred at ' + self.current_token.contents)

        # print('Error occurred at token number ' + error_token_index + '), type ' + error_token.type)

        if node_type is not None:
            print('Error occurred while trying to parse a node of type ' + node_type +
                  ' and running into an unexpected token: ' + error_token)

        quit()

    def get_fresh_token_list_copy(self):
        deep_copy = copy.deepcopy(self.tokens)
        return deep_copy


# Scope table entry
class ScopeTableEntry:
    def __init__(self, id, parent, children, node, text):
        self.id = id
        self.parent = parent
        self.children = children
        self.node = node
        self.text = text

    def __repr__(self):
        if self.parent is not None and self.node is not None:
            return f'\nID: {self.id} (Node type: {self.node.node_class}, node ID: {self.node.node_id}), ' \
                   f'Parent node: {self.parent.node_class}, parent parse tree ID: {self.parent.node_id}, ' \
                   f'Children: {self.children}'
        else:
            return f'\nID: {self.id}, ' \
                   f'Parent node: None, Children: {self.children}'

    def update_children(self, children: list):
        self.children = children

    def set_text(self, text):
        self.text = text


# Static semantic analyst
class Analyst:
    scope_level = 0
    parent_node = None

    def __init__(self, program_node: list, node_list: list):
        self.program_node = program_node
        self.node_list = node_list

    def recursive_scope_analysis(self, current_node, parent):
        # Creates scope table entry object from current node, recursively checks scope of children and creates object
        # for each child, and then adds children into original object upwards in tree, eventually returning the final
        # entry

        # print('Recursive scope analysis - scope level ' + str(self.scope_level))

        current_entry = ScopeTableEntry(self.scope_level, parent, None, current_node,None)
        # print('Instantiated current entry')
        if current_node is not None and current_node.has_children():
            # print('Current node has children')
            child_entries = []  # Array of child ScopeTableEntry object
            # print('Created empty array of child entries at level ' + str(self.scope_level))
            for child_node in current_node.node_contents:
                self.scope_level += 1
                # print('Delving into recursive layer')
                child_entries.append(self.recursive_scope_analysis(child_node, current_node))
                self.scope_level -= 1
            current_entry.update_children(child_entries)
        elif current_node is not None and type(current_node.node_contents) is not list:
            current_entry.set_text(current_node.node_contents)
        print(current_entry)
        return current_entry

        # Ultimately returns parent ScopeTableEntry object - might render actual scope table object a bit redundant,
        # but we can work on that later if necessary with a TODO

    def analyse_scope(self):
        # Returns scope table entry object, which categorises all given AST nodes into their respective scope levels
        print('Starting scope analysis...')
        self.parent_node = self.recursive_scope_analysis(self.program_node, None)
        print('Recursive scope analysis complete:')
        print(self.parent_node)
        return self.parent_node

    def analyse_syntactic_objects(self):
        # Checking for no procedures being named "main" done implicitly in parsing stage

        # Check that no child procedures are named after parent procedures
        # i.e., check each node's children for nodes of the same name
        # for child_node in self.program_node.children:
        #    current_pd_name = ''
        #    if child_node.node_class == NT_PD: # get the same of the PD node - the first UserDefinedName child
        #        current_pd_name = child_node.node_contents[1].node_contents.contents
        #        print('Checking procedure declaration for incorrectly nested names: ' + current_pd_name)
        #        for pd_child_node in child_node.node_contents:
        #            if child_node.node_class == NT_PD:  # get the same of the PD node - the first UserDefinedName child
        #                if child_node.node_contents[1].node_contents.contents == current_pd_name:
        #                    self.nested_procedure_def_error(current_pd_name) # TODO
        pass
        # possibly do some variable analysis - check whether there are any variables that are re-declared somewhere?

    def nested_procedure_def_error(self, proc_name):
        print('Nested program declaration error!')
        print('Redeclared procedure: ' + proc_name)
        print('COMPILATION TERMINATING')
        quit()

    def convert_types(self, type, content):
        if type == TT_NUMBER:
            if content.contains('-'):
                return 'N'
            else:
                return 'NN'
        if type == 'boolean':
            if content == 'true':
                return 'BT'
            else:
                return 'BF'
        if type == TT_SHORTSTRING:
            return 'S'

    variable_list = []
    def check_types(self, given_node):
        # search through whole program for variables
        # when a variable is found, add it to the list of named variables
        # when used, check if in list
        # if not, then decl-appl

        # when done, run through list and find any variables which haven't been used
        # emit appl-decl error

        for node in given_node.node_contents:
            # pass 1 - find all declarations
            if node.node_class == NT_VARDECL:
                new_var = VariableItem()
                child_node = node.node_contents[0]
                if child_node.node_contents[0].node_class == NT_TYP:
                    # getting type from further down declaration
                    new_var.set_type(self.convert_types(child_node.node_contents[0].node_class))
                    # getting name from further down declaration
                    new_var.set_name(child_node.node_contents[1].node_contents[0].node_contents)
                    self.variable_list.append(new_var)
                    for child in node.node_contents:
                        self.check_types(child)
                else:
                    new_var.set_array(True)
                    if child_node.node_contents[1].node_class == NT_TYP:
                        new_var.set_type(self.convert_types(child_node.node_contents[1].node_class))
                        new_var.set_name(child_node.node_contents[2].node_contents[0].node_contents)
                        self.variable_list.append(new_var)
                        for child in node.node_contents:
                            self.check_types(child)

            elif node.node_class == NT_VAR:
                var_name = node.node_contents[0].node_contents
                for variable_node in self.variable_list:
                    if variable_node.node_name == var_name:
                        variable_node.set_used(True)
                        self.variable_list.append(new_var)
                for child in node.node_contents:
                    self.check_types(child)

            elif node.node_class == NT_BINOP:
                if node.node_contents[2] == NT_EXPR and node.node_contents[4] == NT_EXPR:
                    new_var.set_type('B')
                    new_var.set_name('binop')
                    self.variable_list.append(new_var)
                    for child in node.node_contents:
                        self.check_types(child)
                else:
                    new_var.set_type('BF')
                    new_var.set_name('binop')
                    self.variable_list.append(new_var)
                    for child in node.node_contents:
                        self.check_types(child)

            elif node.node_class == NT_UNOP:
                new_var.set_type('B')
                new_var.set_name('unop')
                self.variable_list.append(new_var)
                for child in node.node_contents:
                    self.check_types(child)

            elif node.node_class == NT_BINOP:
                argument_1 = node.node_contents[1]
                argument_2 = node.node_contents[2]
                name_1 = ''
                type_1 = ''
                name_2 = ''
                type_2 = ''
                for variable in self.variable_list:
                    if variable.name == argument_1:
                        name_1 = variable.name
                        type_1 = variable.type
                    elif variable.name == argument_2:
                        name_2 = variable.name
                        type_2 = variable.type
                if type_1 != type_2:
                    print('Lack of value error! ' + name_1)
                    quit()
                else:
                    self.check_types(child)

        for variable in self.variable_list:
            if variable.used == False and variable.name != 'binop':
                print('Declared variable not used! APPL-DECL error! ' + var_name)
                quit()

            if variable.type == None:
                print('Declared variable not used! DECL-APPL error! ' + var_name)
                quit()

        print(self.variable_list)
        return self.variable_list


class VariableItem:
    name = None
    type = None
    used = False
    array = False
    value = None

    def __repr__(self):
        f'{self.name}, {self.type}, Used? {self.used}, Array? {self.array}'

    def set_name(self, name):
        self.name = name

    def set_type(self, type):
        self.type = type

    def set_used(self, used):
        self.used = used

    def set_array(self, is_array):
        self.array = is_array


# Types for reference:
# N - Numbers
# NN - Non-negative numbers
# B - Booleans
# T - True booleans
# F - False booleans
# S - Strings
# U - Unknown
# M - Mixed

class Vtable_node:
    var_name = ''
    var_id = ''
    var_value = ''
    var_type = ''

class Ftable_node:
    function_name = ''
    function_id = ''
    function_type = ''
    function_arg1 = None
    function_arg2 = None

class Vtable:
    def __init__(self):
        self.variable_list = []

    def add_variable(self, variable):
        self.variable_list.append(variable)

    def find_variable(self, variable_name):
        for variable in self.variable_list:
            if variable.var_name == variable_name:
                return variable

        return None

class Ftable:
    def __init__(self):
        self.function_list = []
        self.performs = None

    def add_function(self, function):
        self.function_list.append(function)

    def find_function(self, function_name):
        for function in self.function_list:
            if function.function_name == function_name:
                return function

        return None

class AstIntermediateGenerator:
    parent_node = None
    vtable = Vtable()
    ftable = Ftable()

    def __init__(self, parent_node):
        self.parent_node = parent_node
        self.v_recursive_level = 0
        self.f_id = 0

    def generate_vtable(self):
        self.generate_vtable_recursive(self.parent_node)

    def generate_vtable_recursive(self):
        for node in self.parent_node.node_contents:
            # pass 1 - find all declarations
            if node.node_class == NT_VARDECL:
                new_var = Vtable_node()
                child_node = node.node_contents[0]
                if child_node.node_contents[0].node_class == NT_TYP:
                    # getting type from further down declaration
                    new_var.variable_type = \
                        self.convert_types(child_node.node_contents[0].node_class,
                                           child_node.node_contents[0].node_contents)
                    # getting name from further down declaration
                    new_var.variable_name = child_node.node_contents[1].node_contents[0].node_contents
                    new_var.variable_value = child_node.node_contents[1].node_contents[0].node_contents
                    new_var.variable_id = self.v_recursive_level
                    self.v_recursive_level += 1
                    self.vtable.add(new_var)
                    if node.has_children():
                        for child in node.node_contents:
                            self.generate_vtable_recursive(child)
            elif node.node_class == NT_ASSIGN:
                if node.node_contents[0].node_contents == 'output':
                    # PRINT function
                    pass
                elif node.node_contents[0].node_type == NT_USERDEFINEDNAME:
                    # variable assignment
                    table_entry = self.ftable.find_function(node.node_contents[0].node_contents)
                    if table_entry is not None:
                        table_entry.variable_value = node.node_contents[2].node_contents
                        self.generate_vtable_recursive(child)
                    else:
                        print('Some weirdness beyond my comprehension is happening with the vtable -'
                              ' looking for nonexistent entry, probably possible to reach here')
                        quit()
            if node.has_children():
                for child in node.node_contents:
                    self.generate_vtable_recursive(child)
            else:
                return

    def generate_ftable(self):
        self.generate_ftable_recursive(self.parent_node)

    FT_UNOP_NOT = 'ft_unop_not'
    FT_UNOP_INPUT = 'ft_unop_input'

    FT_BINOP_PLUS = 'ft_binop_+'
    FT_BINOP_MINUS = 'ft_binop_-'
    FT_BINOP_TIMES = 'ft_binop_*'
    FT_BINOP_AND = 'ft_binop-&'
    FT_BINOP_OR = 'ft_binop-|'
    FT_BINOP_EQ = 'ft_binop-=='
    FT_BINOP_LARGER = 'ft_binop->'

    FT_LOOP_DO = 'loop_do'
    FT_LOOP_WHILE = 'loop_while'
    FT_BRANCH = 'branch'

    def generate_ftable_recursive(self, parent_node):
        for child_node in parent_node.node_contents:
            new_function = Ftable_node()
            if child_node.node_type == NT_BRANCH:
                pass
            if child_node.node_type == NT_ALGORITHM:
                if child_node.node_contents[0].node_type == NT_LOOP:
                    if child_node.node_contents[1].node_contents == 'while' or child_node.node_contents[1].node_contents == 'do':
                        new_function.function_type = self.FT_LOOP_WHILE
                        new_function.performs(self.generate_ftable_recursive(child_node))
                    elif child_node.node_contents[1].node_contents == 'if':
                        new_function.function_type = self.FT_BRANCH
                        new_function.performs(self.generate_ftable_recursive(child_node))

                arg_var_1 = self.vtable.find_variable(child_node.node_contents[3].node_contents[0].node_contents)
                arg_var_2 = self.vtable.find_variable(child_node.node_contents[3].node_contents[0].node_contents)
                new_function.function_arg1 = arg_var_1
                new_function.function_arg2 = arg_var_2

            elif child_node.node_type == NT_UNOP:
                if child_node.node_contents[0].node_contents == 'input':
                    new_function.type = self.FT_UNOP_INPUT
                elif child_node.node_contents[0].node_contents == 'not':
                    new_function.type = self.FT_UNOP_NOT

                # add argument
                arg_var = self.vtable.find_variable(child_node.node_contents[1].node_contents[0])
                new_function.function_arg1 = arg_var
            elif child_node.node_type == NT_BINOP:
                if child_node.node_contents[0].node_contents == 'add':
                    new_function.type = self.FT_BINOP_PLUS
                elif child_node.node_contents[0].node_contents == 'sub':
                    new_function.type = self.FT_BINOP_MINUS
                elif child_node.node_contents[0].node_contents == 'mult':
                    new_function.type = self.FT_BINOP_TIMES
                elif child_node.node_contents[0].node_contents == 'and':
                    new_function.type = self.FT_BINOP_AND
                elif child_node.node_contents[0].node_contents == 'or':
                    new_function.type = self.FT_BINOP_OR
                elif child_node.node_contents[0].node_contents == 'eq':
                    new_function.type = self.FT_BINOP_EQ
                elif child_node.node_contents[0].node_contents == 'larger':
                    new_function.type = self.FT_BINOP_LARGER

                # add arguments
                arg_var_1 = self.vtable.find_variable(child_node.node_contents[1].node_contents[0])
                arg_var_2 = self.vtable.find_variable(child_node.node_contents[2].node_contents[0])
                new_function.function_arg1 = arg_var_1
                new_function.function_arg2 = arg_var_2

            new_function.function_id = self.f_id
            self.f_id += 1
            new_function.function_name = f'FUNC-{new_function.function_id}/{new_function.function_type}'
            self.ftable.add_function(new_function)
            self.generate_ftable_recursive(child_node)
            return new_function

    def generate_code(self):
        print('VTABLE:')
        print(self.vtable)


        print('FTABLE:')
        print(self.ftable)


        basic_code = ''

        for variable in self.vtable.variable_list:
            if variable.var_type == 'S':
                basic_code += 'LET $' + variable.var_name + ' = ' + variable.var_value
            else:
                basic_code += 'LET ' + variable.var_name + ' = ' + variable.var_value

        for function in self.ftable.function_list:
            if function.function_type == self.FT_LOOP_WHILE:
                basic_code += f'if UNOP then GOSUB {function}'
            elif function.function_type == self.FT_BINOP_PLUS:
                basic_code += f'{function.function_arg1.variable_name} + {function.function_arg2.variable_name}\n'
            elif function.function_type == self.FT_BINOP_MINUS:
                basic_code += f'{function.function_arg1.variable_name} - {function.function_arg2.variable_name}\n'
            elif function.function_type == self.FT_BINOP_TIMES:
                basic_code += f'{function.function_arg1.variable_name} * {function.function_arg2.variable_name}\n'
            elif function.function_type == self.FT_BINOP_LARGER:
                basic_code += f'{function.function_arg1.variable_name} > {function.function_arg2.variable_name}\n'
            elif function.function_type == self.FT_BINOP_EQ:
                basic_code += f'{function.function_arg1.variable_name} = {function.function_arg2.variable_name}\n'



        basic_code += 'END\n'
        basic_code += 'STOP'

        text_file = open('data.txt', 'w')
        text_file.write(basic_code)
        text_file.close()

        os.startfile('data.txt')


    def convert_types(self, type, content):
        if type == TT_NUMBER:
            if content.contains('-'):
                return 'N'
            else:
                return 'NN'
        if type == 'boolean':
            if content == 'true':
                return 'BT'
            else:
                return 'BF'
        if type == TT_SHORTSTRING:
            return 'S'

# File reading functionality implementation
class FileReader:
    def __init__(self, filename):
        try:
            self.file = open(filename, "r")
        except:
            print('File error! Check that you provided the correct filename!')
            quit()

    def close_file(self):
        self.file.close()

    def get_lines_list(self):
        # Returns a list of lines
        return self.file.readlines()

    def get_all_text(self):
        # Returns full text
        text_list = self.file.readlines()
        full_text = ''.join(text_list)
        return full_text


class Runner:
    def __init__(self):
        self.file_reader = FileReader(sys.argv[1])
        self.lexer = None
        self.parser = None

    def run_lexer(self):
        self.lexer = Lexer(self.file_reader.get_all_text())
        self.lexer.run_lexer()
        print('\n LEXER COMPLETED')

    def run_parser_and_lexer(self):
        self.lexer = Lexer(self.file_reader.get_all_text())
        tokens = self.lexer.run_lexer()
        print('\n LEXER COMPLETED!')
        self.parser = Parser(tokens)
        self.parser.run_parser()
        print('\n PARSER COMPLETED')

    def run_parser_lexer_inital_scope(self):
        self.lexer = Lexer(self.file_reader.get_all_text())
        tokens = self.lexer.run_lexer()
        print('\n LEXER COMPLETED!')
        self.parser = Parser(tokens)
        node = self.parser.run_parser()
        print('\n PARSER COMPLETED')
        analyst = Analyst(node)
        scope_table = analyst.analyse_scope()
        print('\nINITIAL SCOPE CHECK COMPLETE')
