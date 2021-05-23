import ply.lex as lex
from ply.lex import TOKEN
import re

reserved = {
    'if': 'IF',
    'then': 'THEN',
    'while': 'WHILE',
    'begin': 'BEGIN',
    'end': 'END',
    'var': 'VAR',
    'do': 'DO',
    'continue': 'CONTINUE',
    'break': 'BREAK',
    'integer': 'INT',
    'real': 'REAL',
    'and': 'AND',
    'or': 'OR',
    'not': 'NOT',
    'div': 'DIV',
    'mod': 'MOD',
    'write': 'WRITE',
    'read': 'READ',
    'string': 'STRI',
    'program': 'PROGRAM',
    'function': 'FUNCTION',
    'procedure': 'PROCEDURE'
}
states = (
    ('string', 'exclusive'),
)

# без этой штуки ничего не съинтерпретируется, потому что этот массив шарится между лексером и парсером и кроме того используется внутренне библиотекой
tokens = [
             'ASSIGN', 'EQUAL',
             'STRING', 'COLON', 'COMA',
             'OPEN', 'CLOSE', 'NUM', 'PLUSMINUS',
             'MULTIPLE', 'STR', 'SEMICOLON', 'ID', 'COMPARE', 'DOT', 'REALNUM', 'DIVIDE'
         ] + list(reserved.values())

# определим регулярку для абстрактного идетификатора
ident = r'[a-z]\w*'

# для каждого токена из массива мы должны написать его определение вида t_ИМЯТОКЕНА = регулярка
t_DIVIDE = r'\/'
t_DOT = r'\.'
t_EQUAL = r'\='
t_COLON = r'\:'
t_ASSIGN = r'\:='
t_SEMICOLON = r';'
t_COMA = r','
t_OPEN = r'\('
t_CLOSE = r'\)'
t_NUM = r'\d+'
t_PLUSMINUS = r'\+|\-'
t_MULTIPLE = r'\*'
t_COMPARE = r'\>|\<|\>=|\<=|\<>'
t_REALNUM = r'\d+\.\d+'


def t_ID(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = reserved.get(t.value, 'ID')  # Check for reserved words
    return t


# игнорируем комментарии
def t_comment(t):
    r'(\{(.|\n)*?\})|(//.*)'
    pass


# изменили токен PHPSTRING и сделали из него функцию, добавили его во все состояния
def t_ANY_STRING(t):  # нужен в обоих состояниях, потому что двойные кавычки матчатся и там и там.
    r'"'
    if t.lexer.current_state() == 'string':
        t.lexer.begin('INITIAL')  # переходим в начальное состояние
    else:
        t.lexer.begin('string')  # парсим строку
    return t


t_string_STR = r'(\\.|[^$"])+'  # парсим пока не дойдем до переменной или до кавычки, попутно игнорируем экранки

# говорим что ничего не будем игнорировать
t_string_ignore = ''  # это кстати обязательная переменная, без неё нельзя создать новый state


# ну и куда же мы без обработки ошибок
def t_string_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)


# здесь мы игнорируем незначащие символы. Нам ведь все равно, написано $var=$value или $var   =  $value
t_ignore = ' \r\t\f'


def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)


# а здесь мы обрабатываем ошибки. Кстати заметьте формат названия функции
def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)


lexer = lex.lex(reflags=re.UNICODE | re.DOTALL | re.IGNORECASE)

if __name__ == "__main__":
    data = '''
program Hello;
var a,b,c : integer
var h : real

procedure Tafa (a: integer); 
   begin
    write("fdsfsd")
   end;
function rrree(a:integer ; b : real): integer; 

begin
write("Function");
rrree := 10
end;

begin

    b := 1;
    a := rrree(10 , 20.0);
    c := (10 div 3);
    write(a);
    Tafa(10+10);
    while (c < 12) do begin
        c := c + 1;
        a := c * a;
        write(a)
        end
    

end.
    '''

    lexer.input(data)

    while True:
        tok = lexer.token()  
        if not tok: break  
        print(tok)
