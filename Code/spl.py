# Imports
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

# Token convenience constants
WHITESPACES = ' \t\n'
KEYWORDS = ['arr', 'sub', 'mult', 'add', 'larger', 'eq', 'or', 'and', 'not',
            'input', 'true', 'false', 'if', 'then', 'else', 'proc', 'main',
            'return', 'halt', 'num', 'bool', 'string']
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

    def run_lexer(self):
        split_text = self.text.split()
        for x in range(len(split_text)):
            if not self.break_up(split_text[x]):
                return False
        print(self.tokens)
        return True


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
        return f'{self.node_id}:{self.node_class}:{self.node_contents}'


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.token_index = -1
        self.current_token = None
        self.advance()
        self.num_nodes = 0

    def advance(self):
        self.token_index += 1
        if self.token_index < len(self.tokens):
            self.current_token = self.tokens[self.token_index]

    # TODO: contemplate making all leaf nodes into one switch-case function

    def Keyword(self):
        # Leaf node
        token = self.current_token
        if token.type == TT_KEYWORD:
            self.advance()
            self.num_nodes += 1
            return Node(self.num_nodes, NT_KEYWORD, token)
        else:
            self.parser_error()

    def TYP(self):
        # Leaf node
        token = self.current_token
        if token.type == TT_KEYWORD and token.contents in TYP_WORDS:
            self.advance()
            self.num_nodes += 1
            return Node(self.num_nodes, NT_TYP, token)

    def Var(self):
        # Leaf node
        token = self.current_token
        if token.type == TT_USERDEFINEDNAME:
            self.advance()
            self.num_nodes += 1
            return Node(self.num_nodes, NT_VAR, token)

    def Const(self):
        # Leaf node
        token = self.current_token
        if token.type in (TT_NUMBER, TT_SHORTSTRING) or (token.type == TT_KEYWORD and token.contents in BOOLEAN_WORDS):
            self.advance()
            self.num_nodes += 1
            return Node(self.num_nodes, NT_TYP, token)

    # TODO: make sure that all leaves (including KEYWORDS!) are added to the parsing tree in declarations
    def Dec(self):
        # Compound node

        # Branching based on two possible Dec types:
        # 1 - arr $TYP[$Const] $Var
        # 2 - $TYP $Var

        # Children structure: TODO note children structure

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
                    self.num_nodes += 1
                    return Node(self.num_nodes, NT_DEC, children)
                else:
                    self.parser_error()
            else:
                self.parser_error()
        elif self.current_token.type == TT_KEYWORD and self.current_token.contents in TYP_WORDS:
            children.append(self.TYP())
            children.append(self.Var())
        else:
            self.parser_error()

    def VarDecl(self):
        # Compound node

        # Branching because nullable
        # 1 - Dec ; VarDecl
        # 2 - nothing

        # Children structure:
        # [1] - Declaration
        # [2] - Variable Declaration

        children = []
        dec = self.Dec()
        if dec is not None:
            children.append(dec)
            if self.current_token.type == TT_SEMICOLON:
                self.advance()
                vardecl = self.VarDecl()
                if vardecl is not None:
                    if vardecl == 0:
                        self.num_nodes += 1
                        return Node(self.num_nodes, NT_VARDECL, children)
                    else:
                        children.append(vardecl)
                        # Have to keep recurring until a zero is given indicating the end of the variable declarations
                        #
                        # Will result in children[] having nested VarDecl nodes -
                        # acceptable for our purposes thus far though
                        self.VarDecl()
                else:
                    self.parser_error()
                    return None
            else:
                self.parser_error()
                return None
        else:
            # Sign that something else is here - thus have to pass
            # TODO - look at this logic again when less tired
            return 0

    def BinOp(self):
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
                    else:
                        self.parser_error()
                        return None
                else:
                    self.parser_error()
                    return None
            else:
                self.parser_error()
                return None
        else:
            self.parser_error()
            return None

        pass

    def UnOp(self):
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
            # TODO: not sure about user defined name implementation here
            children.append(Node(self.num_nodes, NT_USERDEFINEDNAME, self.current_token))
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
        # TODO: requires testing

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
        field = self.Field()
        var = self.Var()
        children = []
        if token.type == TT_KEYWORD and token.contents == 'output':
            self.num_nodes += 1
            self.advance()
            return Node(self.num_nodes, NT_LHS, token)
        elif field is not None:
            self.num_nodes += 1
            return Node(self.num_nodes, NT_LHS, children)
        elif var is not None:
            self.num_nodes += 1
            return Node(self.num_nodes, NT_LHS, children)
        else:
            self.parser_error()
            return None

    def Loop(self):
        # TODO

        # TODO 2: electric boogaloo
        # make self.advance() count where we are in token list for error detail purposes -
        # so we can print out where error occurred in self.parser_error()

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

    def Alternat(self):
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
        # Compound node

        # No branching

        # Children:
        # LHS Expr

        children = []

        lhs = self.LHS()
        if lhs is not None:
            children.append(lhs)
            # TODO add assignment operator to lexer and then utilise here


        pass

    def Instr(self):
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

        if self.current_token.type == TT_USERDEFINEDNAME or (self.current_token.type == TT_KEYWORD and self.current_token.contents == 'output'):
            children.append(self.Assign())
            self.num_nodes += 1
            return Node(self.num_nodes, NT_INSTR, children)
        elif self.current_token.type == TT_KEYWORD and self.current_token.contents == 'if':
            children.append(self.Branch())
            self.num_nodes += 1
            return Node(self.num_nodes, NT_INSTR, children)
        elif self.current_token.type == TT_KEYWORD and self.current_token.contents in ('do', 'loop'):
            children.append(self.Loop())
            self.num_nodes += 1
            return Node(self.num_nodes, NT_INSTR, children)
        elif self.current_token.type == TT_KEYWORD and self.current_token.contents == 'call':
            children.append(self.PCall())
            self.num_nodes += 1
            return Node(self.num_nodes, NT_INSTR, children)

        self.parser_error()

    def Algorithm(self):
        # Compound

        # Branching based on nullable

        # Children:
        # Instr Algorithm

        children = []

        # TODO

        pass

    def PD(self):
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
                    children.append(self.ProcDefs())
                    children.append(self.Algorithm())
                    if self.current_token.type == TT_KEYWORD and self.current_token.contents == 'return':
                        children.append(self.Keyword())
                        if self.current_token.type == TT_SEMICOLON:
                            self.advance()
                            children.append(self.VarDecl())
                            if self.current_token.type == TT_RBRACE:
                                return Node(self.num_nodes, NT_PD, children)

        # TODO - why parser error not working here?


    def ProcDefs(self):
        # Compound

        # Branching on nullable

        # Children:
        # PD ProcDefs

        tokens_copy = self.get_fresh_token_list_copy()
        current_token_copy = tokens_copy[self.token_index]
        if current_token_copy.type != TT_KEYWORD or current_token_copy.contents != 'proc':
            pass

        children = []

        children.append(self.PD())
        if self.current_token.type == TT_COMMA:
            self.advance()
            children.append(self.ProcDefs())
            self.num_nodes += 1
            return Node(self.num_nodes, NT_PROCDEFS, children)

        self.parser_error()

    def SPLProgr(self):
        # Compound

        # No branching - only:
        # ProcDefs main { Algorithm halt ; VarDecl }

        # Children:
        # ProcDefs Keyword Algorithm Keyword VarDecl
        # TODO
        pass

    def run_parser(self):
        # TODO
        pass

    def parser_error(self):
        print('Parser Error!')
        # TODO: fill out with descriptive error message

    def get_fresh_token_list_copy(self):
        deep_copy = copy.deepcopy(self.tokens)
        return deep_copy


class Error:
    def __init__(self, error_name, details):
        self.error_name = error_name
        self.details = details

    def as_string(self):
        result = f'{self.error_name}: {self.details}'
        return result


# File reading functionality implementation
class File_Reader:
    def __init__(self, filename):
        self.file = open(filename, "r")

    def close_file(self):
        self.file.close()

    def get_lines_list(self):
        # Returns a list of lines
        return self.file.readlines()

    def get_all_text(self):
        # Returns full text
        list = self.file.readlines()
        full_text = ''.join(list)
        return full_text


class Runner:
    def __init__(self):
        self.file_reader = File_Reader(sys.argv[1])
        self.lexer = None
        self.parser = None

    def run_lexer(self):
        self.lexer = Lexer(self.file_reader.get_all_text())
        self.lexer.run_lexer()
        print('/n LEXER COMPLETED')

    def run_parser_and_lexer(self):
        self.lexer = Lexer(self.file_reader.get_all_text())
        tokens = self.lexer.run_lexer()
        print('/n LEXER COMPLETED!')
        self.parser = Parser(tokens)
        self.parser.run_parser()
        print('/n PARSER COMPLETED')
