# CompilerLLVM
pip install ply
pip install llvmlite

python -m run Tests/Filename 

В результате выполнения программы создается файл с расширением .ll , который можно  
будет преобразовать в obj и запустить командами:

llc -filetype=obj -relocation-model=pic Code.ll
gcc Сode.o -o output
./Code

# Lexer.py
Лексический анализатор , реализованный при помощи библиотеки ply
# Parser.py
Синтаксический анализатор , реализованный при помощи библиотеки ply
# CodeGenerator
Генератор трехадресного кода 
# llvmGen
Генератор обьектного кода для llvm, реализованный при помощи библеотеки llvmlite
# run.py
Трансляция обьектного кода в ассемблер
