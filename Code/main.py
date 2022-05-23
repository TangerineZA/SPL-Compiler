# Main script

import spl

lexer = None
parser = None
filereader = None

if __name__ == '__main__':
    print('SPL Compiler - David Walker - COS341 2022')
    filename = input('Please input the name of the file you wish to examine:')

    filereader = spl.FileReader(filename)
    file_text = filereader.get_all_text()

    lexer = spl.Lexer(file_text)
    token_list = lexer.run_lexer()
    print('\nLEXER COMPLETED - OUTPUT ABOVE\n')

    parser = spl.Parser(token_list)
    program_node = parser.run_parser()
    print('\nPARSER COMPLETED - OUTPUT ABOVE\n')

    analyst = spl.Analyst(program_node)
    scope_table = analyst.analyse_scope()
    print('\nINITIAL SCOPE CHECK COMPLETE - OUTPUT ABOVE\n')

    print('End of Practical A scope!')