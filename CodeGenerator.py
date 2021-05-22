import types
from collections import defaultdict

from Parser import build_tree, getTable


class Block:
    def __init__(self):
        self.head = []
        self.instructions = []
        self.return_type = None
        self.params = []

    def append(self, instruction):
        self.instructions.append(instruction)

    def inithead(self, head):
        self.head = head

    def isblock(self):
        return True


bool_ops = {
    '>', '<', '==', '!=', '>=', '<=', 'and', 'or'
}
binary_ops = {
    '+': 'add',
    '-': 'sub',
    '*': 'mul',
    '/': 'div',
    '<': 'lt',
    '<=': 'le',
    '>': 'gt',
    '>=': 'ge',
    '=': 'eq',
    '!=': 'ne',
    'and': 'and',
    'or': 'or'
}

unary_ops = {
    '+': 'uadd',
    '-': 'usub',
    'Not': 'not'
}
typeconv = {'integer': 'int', 'real': 'float', 'boolean': 'bool'}
defalt = {'integer': 0, 'real': 0.0}

versions = defaultdict(int)


def new_temp(typeobj):
    '''
    Create a new temporary variable of a given type.
    '''
    name = "__%s_%d" % (typeobj, versions[typeobj])
    versions[typeobj] += 1
    return name


def GenerateCode(parentblock, tree, scope, IsMain):
    for part in tree.parts:
        if type(part) != str and part:
            if part.type == 'Var':
                if scope == 'global':
                    new = Block()
                    new.inithead('__init')
                    new.return_type = 'void'
                    parentblock.append(new)
                else:
                    new = Block()
                    new.inithead(part.type)
                    parentblock.append(new)
                if scope != 'global' and not (scope.startswith(' ')):
                    new.append(('alloc_' + typeconv[table[scope].get(scope)[0]], scope))
                for i in range(0, len(part.parts), 2):
                    for g in range(len(part.parts[i].parts)):
                        if scope != 'global':
                            tradr = 'alloc_' + typeconv[part.parts[i + 1].parts[0]]
                        else:
                            tradr = 'global_' + typeconv[part.parts[i + 1].parts[0]]
                        id = part.parts[i].parts[g]

                        new.append((tradr, id))
                        newtmpe = new_temp(typeconv[part.parts[i + 1].parts[0]])
                        new.append(('literal_' + typeconv[part.parts[i + 1].parts[0]],
                                    defalt[part.parts[i + 1].parts[0]], newtmpe))
                        new.append(('store_' + typeconv[part.parts[i + 1].parts[0]], newtmpe, id))
                if scope == 'global':
                    new.append(('return_void ',))
                GenerateCode(new, part, scope, IsMain)
            if part.type == 'Arguments':
                new = Block()
                new.inithead('Var2')
                parentblock.append(new)
                index = 0
                for i in range(0, len(part.parts), 2):

                    for g in range(len(part.parts[i].parts)):
                        tradr = 'parm_' + typeconv[part.parts[i + 1].parts[0]]
                        parentblock.params.append(typeconv[part.parts[i + 1].parts[0]])
                        id = part.parts[i].parts[g]
                        new.append((tradr, id, index))
                        index = index + 1

                GenerateCode(new, part, scope, IsMain)
            if part.type == 'SubDeclaration':
                scope = part.parts[0].type[9:]
                new = Block()
                new.inithead(part.parts[0].type)
                if part.parts[0].type.startswith('function'):
                    new.return_type = typeconv[part.parts[0].parts[1].parts[0]]
                if part.parts[0].type.startswith('procedure'):
                    new.return_type = 'void'
                parentblock.append(new)
                GenerateCode(new, part, scope, IsMain)
                for ins in new.instructions:  # если встречаем блоки var1 и var 2 (то есть аргументы и вары функции , то мерджим два блока )
                    for ins2 in new.instructions:  # естесственно через зад
                        if ins.head == 'Var' and ins2.head == 'Var2':
                            for a in range(len(ins.instructions)):
                                ins2.append(ins.instructions[a])
                            ins2.inithead('Var')
                            i = (new.instructions.index(ins))
                            new.instructions.pop(i)
                if part.parts[0].type.startswith('function'):
                    retrrn = new_temp(typeconv[part.parts[0].parts[1].parts[0]])
                    ex = ('load_' + typeconv[part.parts[0].parts[1].parts[0]], part.parts[0].type[9:], retrrn)
                    new.append(ex)
                    ex = ('return_' + typeconv[part.parts[0].parts[1].parts[0]], retrrn)
                    new.append(ex)
                scope = 'global'
            elif part.type == 'Compound statement':
                if parentblock.head != 'WHILEbody_Block' and scope == 'global' and (not IsMain):
                    new = Block()
                    new.inithead('main')
                    new.return_type = 'void'
                    IsMain = True
                    parentblock.append(new)
                    GenerateCode(new, part, scope, IsMain)
                elif parentblock.head != 'WHILEbody_Block':
                    new = Block()
                    new.inithead('default')
                    parentblock.append(new)
                    GenerateCode(new, part, scope, IsMain)
                else:
                    GenerateCode(parentblock, part, scope, IsMain)
                # print(2)
            elif part.type == 'If clause':
                ifBlock = Block()
                ifBlock.inithead('IfBlock')
                parentblock.append(ifBlock)
                condition = Block()
                condition.inithead('IFcondition')
                body = Block()
                body.inithead('IFbody')
                ifBlock.append(condition)
                ifBlock.append(body)
                GenerateCode(condition, part.parts[0], scope, IsMain)
                GenerateCode(body, part.parts[1], scope, IsMain)
            elif part.type == 'While clause':
                whileBlock = Block()
                whileBlock.inithead('WhileBlock')
                parentblock.append(whileBlock)
                condition = Block()
                condition.inithead('WHILEcondition')
                wbody = Block()
                wbody.inithead('WHILEbody')
                whileBlock.append(condition)
                whileBlock.append(wbody)
                GenerateCode(condition, part.parts[0], scope, IsMain)
                GenerateCode(wbody, part.parts[1], scope, IsMain)

            elif part.type == 'write':
                print('ТУУУУУУт')

                if type(part.parts[0]) is str:
                    typer = table[scope].get(part.parts[0])[0]
                    tmp1 = new_temp(typeconv[typer])
                    parentblock.append(('load_' + typeconv[typer], part.parts[0], tmp1))
                    parentblock.append(('print_' + typeconv[typer], tmp1))
                else:
                    tmp = new_temp('str')
                    parentblock.append(('literal_string', part.parts[0].parts[0], tmp))
                    parentblock.append(('print_string', tmp))


            elif part.type == 'Assign':
                exp = []
                # print(part)
                name = GenerateForExres(part.parts[1], scope, exp)
                print(name)
                if type(part.parts) is not str :
                    if part.parts[1].parts[0].type == 'Function':
                        if type(part.parts[1].parts[0].parts) is not str:
                            for a in exp:
                                parentblock.append(a)
                            vap = []
                            vap.append('call_func')
                            vap.append(part.parts[1].parts[0].parts[0])
                            for g in range(len(name)):
                                # print(name)
                                vap.append(name[g])
                            print(vap)
                            tmp1 = new_temp(
                                typeconv[table[part.parts[1].parts[0].parts[0]].get(part.parts[0].parts[0])[0]])
                            vap.append(tmp1)
                            parentblock.append(tuple(vap))
                            parentblock.append(('store_' + typeconv[
                                table[part.parts[1].parts[0].parts[0]].get(part.parts[0].parts[0])[0]], tmp1,
                                                part.parts[0].parts[0]))
                    else:
                        nameType = name[2:5]
                        for a in exp:
                            parentblock.append(a)
                        parentblock.append(('store_' + nameType, name, part.parts[0].parts[0]))
                    # print(2)
            elif part.type == 'Expression in parentheses':
                a = []
                exp = []
                GenerateForExres(part, scope, exp)
                # print(exp)
                for a in exp:
                    parentblock.append(a)
                # print('_____')
                # parentblock.append()
            elif part.type == 'BR':
                a = ['break']
                parentblock.append(tuple(a))
            elif part.type == 'Expression':
                a = []
                exp = []
                GenerateForExres(part, scope, exp)
                for a in exp:
                    parentblock.append(a)
                # print('_____')
                # parentblock.append()
            else:
                GenerateCode(parentblock, part, scope, IsMain)

    return parentblock


def GenerateForExres(tree, scope, exp):
    if type(tree) is not str:
        if tree.type == 'Function':
            # print('тута')
            p = []

            for g in range(len(tree.parts[1].parts)):
                # print(table[scope].get(tree.parts[1].parts[g].parts[0]))
                if table[scope].get(tree.parts[1].parts[g].parts[0]) != None:
                    # print('tttet')
                    # print(table[scope].get(tree.parts[1].parts[g].parts[0]))
                    typer = table[scope].get(tree.parts[1].parts[g].parts[0])[0]
                    tmp1 = new_temp(typeconv[typer])
                    exp.append(('load_' + typeconv[typer], tree.parts[1].parts[g].parts[0], tmp1))

                else:
                    # print('tteewww')
                    if tree.parts[1].parts[g].parts[0].find('.') != -1:
                        typer = 'real'
                        value = float(tree.parts[1].parts[g].parts[0])
                    else:
                        typer = 'integer'
                        value = int(tree.parts[1].parts[g].parts[0])
                    tmp1 = new_temp(typeconv[typer])
                    exp.append(('literal_' + typeconv[typer], value, tmp1))
                p.append(tmp1)
            # print(p)
            return p

        elif len(tree.parts) == 1 and type(tree.parts[0]) == str:
            if table[scope].get(tree.parts[0]) != None:
                typer = table[scope].get(tree.parts[0])[0]
                tmp1 = new_temp(typeconv[typer])
                exp.append(('load_' + typeconv[typer], tree.parts[0], tmp1))
            else:
                if tree.parts[0].find('.') != -1:
                    typer = 'real'
                    value = float(tree.parts[0])
                else:
                    typer = 'integer'
                    value = int(tree.parts[0])
                tmp1 = new_temp(typeconv[typer])
                exp.append(('literal_' + typeconv[typer], value, tmp1))
            return tmp1
        elif len(tree.parts) == 2 and type(tree.parts[0]) == str and type(
                tree.parts[1]) != str:  # если второй операнд сложное выражение
            if table[scope].get(tree.parts[0]) != None:
                typer = table[scope].get(tree.parts[0])[0]
                tmp1 = new_temp(typeconv[typer])
                exp.append(('load_' + typeconv[typer], tree.parts[0], tmp1))
            else:
                if tree.parts[0].find('.') != -1:
                    typer = 'real'
                    value = float(tree.parts[0])
                else:
                    typer = 'integer'
                    value = int(tree.parts[0])
                tmp1 = new_temp(typeconv[typer])
                exp.append(('literal_' + typeconv[typer], value, tmp1))
            name = GenerateForExres(tree.parts[1], scope, exp)
            if (tree.type in bool_ops):
                ended = new_temp('bool')
            else:
                ended = new_temp(typeconv[typer])
            exp.append((binary_ops[tree.type] + '_' + typeconv[typer], tmp1, name, ended))
            return ended

        elif len(tree.parts) == 2 and type(tree.parts[0]) != str and type(
                tree.parts[1]) != str:  # если оба являются сложными выражениями
            name = GenerateForExres(tree.parts[0], scope, exp)
            name2 = GenerateForExres(tree.parts[1], scope, exp)
            typer = name[2:5]
            if typer == 'boo':
                typer = 'boolean'
            if typer == 'flo':
                typer = 'real'
            print(typer)
            if (tree.type in bool_ops):
                ended = new_temp('bool')
            else:
                ended = new_temp(typeconv[typer])
            exp.append(((binary_ops[tree.type] + '_' + typeconv[typer]), name, name2, ended))
            return ended

        elif len(tree.parts) == 2 and type(tree.parts[0]) == str and type(
                tree.parts[1]) == str:  # если оба операнда оказались не составными
            if table[scope].get(tree.parts[0]) != None:
                typer = table[scope].get(tree.parts[0])[0]
                tmp1 = new_temp(typeconv[typer])
                exp.append(('load_' + typeconv[typer], tree.parts[0], tmp1))
            else:
                if tree.parts[0].find('.') != -1:
                    typer = 'real'
                    value = tree.parts[0]
                else:
                    typer = 'integer'
                    value = tree.parts[0]
                tmp1 = new_temp(typeconv[typer])
                exp.append(('literal_' + typeconv[typer], value, tmp1))
            if table[scope].get(tree.parts[1]) != None:
                typer = table[scope].get(tree.parts[0])[0]
                tmp2 = new_temp(typeconv[typer])
                exp.append(('load_' + typeconv[typer], tree.parts[0], tmp2))
            else:
                if tree.parts[1].find('.') != -1:
                    typer = 'real'
                    value = float(tree.parts[1])
                else:
                    typer = 'integer'
                    value = int(tree.parts[1])
                tmp2 = new_temp(typeconv[typer])
                exp.append(('literal_' + typeconv[typer], value, tmp2))
            if tree.type in bool_ops:
                ended = new_temp('bool')
            else:
                ended = new_temp(typeconv[typer])
            exp.append((binary_ops[tree.type] + '_' + typeconv[typer], tmp1, tmp2, ended))
            return ended
        else:
            for part in tree.parts:
                end = GenerateForExres(part, scope, exp)
    return end  # if type(part) is not str:
    # print(part.type)
    # else:

    # print(part)


data = '''
program Hello;
    var a,b,c,d : integer
    var h : real
      begin
      while ( a < 20 ) do begin
      a := a + 1;
      write(a)


      end
    end.
'''

Example = Block()
tree = build_tree(data)
table = getTable(tree)

bloc = Block()
bloc.inithead(':::::::::::::::::::::::::::::::::::::::::::::::::::::::')
bloc = GenerateCode(bloc, tree, 'global', False)
v = 1

print(bloc.head)


def prTr(Block, sink):
    for a in Block.instructions:

        if a.__class__ is not tuple:

            print(' ' * sink * 3 + a.head, end='')
            if a.return_type != None:
                print('   | ' + a.return_type, a.params, end='')
            print('\t')

            prTr(a, sink + 1)
        else:

            print(' ' * sink * 3, end='')
            print(a)



