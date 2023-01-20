# Assembler. Транслятор и модель

- Данилов Павел Юрьевич, гр. P33121
- `asm | risc | harv | hw | instr | struct | trap | port | prob1`

## Язык программирования

``` ebnf
program ::= section_text | section_text section_data | section_data section_text

section_data ::= "section data\n" declaration_line*

section_text ::= "section text\n" instruction_line*

label ::= label_name ":" ?comment

comment ::= ; <any sequence>

declaration_line ::= label | declaration ?comment "\n"

declaration ::= ("word" number | char) | ("int" number number)

instruction_line ::= label | instruction  ?comment "\n"
            
instruction ::=  ((op_3_args " " wr_register " " register " " operand) |
            (op_2_args " " register " " operand) |
            (op_2_args_wr " " wr_register " " operand) |
            (op_1_args_reg " " wr_register) |
            (op_1_args_any " " operand) |
            (op_0_args))          

section_name ::= "text" | "data"

op_3_args ::= "add" | "sub" | "div" | "mod" | "cmp"

op_2_args ::= "je" | "jne" | "sv"

op_2_args_wr ::= "ld" 

op_1_args_reg ::= "in"

op_1_args_any ::= "jmp" | "out"

op_0_args ::= "exit" | "cli" | "sti" | "iret"

operand ::= register | value

register ::= wr_register | "r0"

wr_register ::= "r1" | "r2" | "r3" | "r4" | "sp"

value ::= label_name | number | char

label_name ::= [a-zA-Z]+
          
number ::= [-2^32; 2^32 - 1]

char ::= ' <any UTF-8 symbol> '
```

Декларации из **section data** выполняются последовательно. Операции:

- `word <num>` -- записать num в ячейку памяти номер %размер вектора прерываний + номер word%
- `int <addr> <addr>` -- записать num в ячейку памяти номер %размер вектора прерываний + номер word%

Поддерживаемые аргументы:
- для аргументов **num** число в диапазоне [-2^32; 2^32 - 1] или unicode-символ в одиночных кавычках
- для аргументов **addr** число в диапазоне [0; размер памяти данных]

Код из **section text** выполняется последовательно. Операции:

- `add <wreg1> <reg2> <val>` -- прибавить val к регистру reg2 и записать в регистр wreg1 
- `sub <wreg1> <reg2> <val>` -- вычесть val из регистра reg2 и записать в регистр wreg1
- `div <wreg1> <reg2> <val>` -- записать целую часть от деления регистра reg2 на val в регистр wreg1
- `mod <wreg1> <reg2> <val>` -- записать остаток от деления регистра reg2 на val в регистр wreg1
- `mul <wreg1> <reg2> <val>` -- записать произведение регистра reg1 и reg2 в регистр wreg1
- `cmp <wreg1> <reg2> <val>` -- записать результат сравнения регистра reg2 с val в регистр wreg1
- `je <reg1> <val>` -- если значение в reg1 равно нулю, перейти на значение val
- `jne <reg1> <val>` -- если значение в reg1 не равно нулю, перейти на значение val
- `jmp <val>` -- безусловный переход на значение val
- `out <val>` -- распечатать в поток вывода значение из val
- `in <wreg1>` -- прочитать в wreg1 значение из потока ввода
- `ld <wreg1> <val>` -- прочитать в arg1 значение из памяти данных по адресу из val
- `sv <reg1> <val>` -- записать reg1 в память данных по адресу из val
- `iret` -- выйти из прерывания
- `sti` -- разрешить прерывания
- `cli` -- запретить прерывания
- `halt` -- завершить выполнение программы

Поддерживаемые аргументы:
- для аргументов **wreg** регистры r1, r2, r3, r4, sp
- для аргументов **reg** регистры из wreg и r0
- для аргументов **num** название объявленной метки или число в диапазоне [-2^32; 2^32 - 1] или unicode-символ в одиночных кавычках
- для аргументов **val** регистры из reg и значения из num

Дополнительные конструкции:
- `; <any sequence not containing ';'>` - комментарий
- `section text` - объявление секции кода
- `section data` - объявление секции данных
- `<label>:` - метки для переходов / названия переменных

Примечания:
- Исполнение кода начинается с первой инструкции в section text

## Система команд

Особенности процессора:

- Машинное слово -- 32 бита, знаковое.
- Память данных:
    - доступ к памяти данных только через команды ld и sv;
    - на шину данных для записи подается регистр, соединенный с правым входом АЛУ;
    - шина адреса соединена с выходом АЛУ;
    - содержит таблицу векторов прерываний в первых n ячейках (по 1 ячейке на каждое устройство);
- АЛУ:
    - на правый вход АЛУ вместо регистра может быть подана константа из инструкции;
    - АЛУ поддерживает операции: INC, DEC, ADD, SUB, MUL, DIV, MOD, CMP, NOP, выводы левого или правого входов;
- Регистры:
    - управляются RegFile, на вход которого подаются сигналы для выбора операндов и регистра для записи;
    - четыре регистра общего назначения (R1, R2, R3, R4);
    - есть регистр с указателем на вершину стека SP;
    - есть регистр R0, который всегда содержит значение 0;
    - регистр PC инкрементируется после каждой инструкции или перезаписывается при инструкции перехода;
- Ввод-вывод:
    - port-mapped через систему прерываний, символьный.
    - для упрощения существует только одно устройство ввода-вывода.
- program_counter -- счётчик команд:
    - инкрементируется после каждой инструкции или перезаписывается инструкцией перехода.
    
### Набор инструкций

Набор инструкций совпадает с инструкциями ASM в силу RISC'овости процессора. 
Описания команд можно прочитать в пункте **Язык программирования**

- `add <wreg1> <reg2> <val>` -- 1 такт
- `sub <wreg1> <reg2> <val>` -- 1 такт
- `div <wreg1> <reg2> <val>` -- 1 такт
- `mod <wreg1> <reg2> <val>` -- 1 такт
- `mul <wreg1> <reg2> <val>` -- 1 такт
- `cmp <wreg1> <reg2> <val>` -- 1 такт
- `je <reg1> <val>` -- 2 такта: такт на сравнение значения регистра с R0 и такт на переход
- `jne <reg1> <val>` -- 2 такта: такт на сравнение значения регистра с R0 и такт на переход
- `jmp <val>` -- 1 такт
- `out <val>` -- 1 такт
- `in <wreg1>` -- 1 такт
- `ld <wreg1> <val>` -- 1 такт
- `sv <reg1> <val>` -- 1 такт
- `iret` -- 2 такта: такт на инкремент и чтение по SP и такт на запись в регистр 
- `sti` -- 1 такт
- `cli` -- 1 такт
- `halt` -- 1 такт




### Кодирование инструкций

- Код ассемблера сериализуется в инструкции из памяти команд и данные из памяти данных, которые записаны в словарь JSON
```{
    "code": [
        {
            "opcode": "add",
            "arg1": "r0",
            "arg2": "999",
            "arg2_type": "const",
            "out": "r1"
        },
        {
            "opcode": "add",
            "arg1": "r0",
            "arg2": "r0",
            "arg2_type": "reg",
            "out": "r3"
        },
        ...
        ]
    "data": [
        "1",
        "104",
        "101",
        "108",
        "108",
        "111",
        "32",
        "119",
        ...
    ]
}
```

где:

- opcode -- строка с кодом операции;
- arg1 (optional) -- первый аргумент команды;
- arg2 (optional) -- второй аргумент команды;
- arg2_type (optional) -- тип первого аргумента (регистр/константа);
- out (optional) -- регистр для записи результата команды;

Типы данных в модуле isa, где:
- Opcode -- перечисление кодов операций;
- OperandType -- перечисление кодов операций;
- Register -- перечисление регистров процессора;

## Транслятор

Интерфейс командной строки: `translator.py <input_file.asm> <target_file.bin>"`

Реализовано в модуле: [translation](./translation.py)

Этапы трансляции (функция `translate`):

1. Трансформирование текста в последовательность значимых термов.
2. Индексация всех меток в программе (меток данных и команд) и генерация переменных из word
3. Первичная проверка корректности термов.
4. Подстановка адресов вместо меток.
5. Подстановка кодов символов вместо символов (char).
6. Проверка корректности использования регистров и констант в командах.
7. Заполнение вектора прерываний по инструкции int
8. Генерация машинного кода.

Правила генерации машинного кода:

- одна инструкция процессора -- одна инструкция в коде;
- для команд, однозначно соответствующих инструкциям -- прямое отображение;
- команды из **section data** используются для заполнения памяти данных;
- запись в память команд происходит начиная с первой команды из **section text**;
- первые n ячеек памяти данных отведены под векторы прерываний;

## Модель процессора

Реализовано в модуле: [processor](./processor.py).

### Схема DataPath и ControlUnit

![https://drive.google.com/file/d/1u5QV3I4ZIRaMM69XOMc-7nwkFQh0S4KO/view?usp=sharing](/images/image.png "Схема DataPath и ControlUnit") 

## DataPath

Реализован в классе `DataPath`.

- `data_memory` -- однопортовая, поэтому либо читаем, либо пишем.
- `input` -- вызовет остановку процесса моделирования, если буфер входных значений закончился.
- `reg_file` -- устройство управления регистрами. Получает на вход сигналы с операндами и регистром для записи.
- - `reg_file.operand1` -- регистр, данные из которого будут поданы на левый вход АЛУ
- - `reg_file.operand2` -- регистр, данные из которого будут поданы на правый вход АЛУ
- - `reg_file.output` -- регистр, в который будут считаны данные с `output_bus` (при подаче сигнала)
- `alu` -- АЛУ, выполняющее арифметические операции.
- - `alu.left` -- данные с левого входа АЛУ
- - `alu.right` -- данные с правого входа АЛУ
- - `alu.zero_flag` -- zero флаг АЛУ, передается на CU по сигналу, используется для условных переходов
- `alu_bus` -- шина, выходящая из АЛУ.
- `output_bus` -- шина, соединяющая выход с АЛУ и регистр out (выбранный в RegFile).
- `data_bus` -- шина, соединяющая op2 (который идет на правый вход АЛУ) и память данных. Содержит данные для записи 
- `data_bus` -- шина, соединяющая op2 (который идет на правый вход АЛУ) и память данных. Содержит данные для записи 
- `input_buffer` -- буфер с входными данными от внешнего устройства
- `input_pointer` -- вспомогательная переменная для эмуляции чтения из буфера
- `output_buffer` -- буфер с данными для записи на внешнее устройство

Сигналы:

- `latch_registers` -- подать сигнал RegFile с данными о регистрах 
- `latch_alu (const_operand)` -- защелкнуть входы АЛУ. При подаче const_operand помещается на правый вход (sig const).
- `execute_alu` -- рассчитать выходное значение АЛУ, подав на него сигнал с операцией.
- `read` -- считать значение из памяти и поместить его на шину, идущую к `output_bus`.
- `write` -- записать значение op2 в память по адресу из `alu_bus`.
- `print` -- записать значение `alu_bus` на внешнее устройство.
- `input` -- считать значение с внешнего устройства на `output_bus`.
- `latch_output` -- подать сигнал output на мультиплексоры для вывода данных с шины `alu_bus` на `output_bus` и записи в регистр.

Флаги:

- `zero` -- отражает наличие нулевого значения на выходе АЛУ.

## ControlUnit
Реализован в классе `ControlUnit`.

- Hardwired (реализовано полностью на python).
- Моделирование на уровне инструкций.
- Трансляция инструкции в последовательность сигналов: `decode_and_execute_instruction`.

Сигнал:

- `latch_program_couter` -- сигнал для обновления счётчика команд в ControlUnit.

Особенности работы модели:

- Для журнала состояний процессора используется стандартный модуль logging.
- Количество инструкций для моделирования ограничено hardcoded константой.
- Остановка моделирования осуществляется при помощи исключений:
    - `EOFError` -- если нет данных для чтения из порта ввода-вывода;
    - `StopIteration` -- если выполнена инструкция `exit`.
- Управление симуляцией реализовано в функции `simulate`.

## Апробация

В качестве тестов использовано два алгоритма:

1. [hello world](tests/hello.asm).
2. [cat](tests/cat.asm) -- программа `cat`, повторяем ввод на выводе.
3. [prob1](tests/prob1.asm) -- рассчитать сумму делителей 3 или 5, меньших 1000

Юнит-тесты реализованы тут: 
[processor_test](tests/processor_test.py)
[translator_test](tests/translator_test.py)

CL:
```yaml
lab3-example:
  stage: test
  image:
    name: python-tools
    entrypoint: [""]
  script:
    - python3-coverage run -m pytest --verbose
    - find . -type f -name "*.py" | xargs -t python3-coverage report
    - find . -type f -name "*.py" | xargs -t pep8 --ignore=E501
    - find . -type f -name "*.py" | xargs -t pylint --disable=C0301,R0903,C0200,C0201,R1715,R0912,R0915,R0902,C0116
    # R0903: Too few public methods (0/2) (too-few-public-methods)
    # C0301: Line too long (111/100) (line-too-long)
    # C0200: Consider using enumerate instead of iterating with range and len (consider-using-enumerate)
    # C0201: Consider iterating the dictionary directly instead of calling .keys() (consider-iterating-dictionary)
    # R1715: Consider using dict.get for getting values from a dict if a key is present or a default if not (consider-using-get)
    # R0912: Too many branches (74/12) (too-many-branches)
    # R0915: Too many statements (155/50) (too-many-statements)
    # C0116: Missing function or method docstring (missing-function-docstring)
```
где:

- `python3-coverage` -- формирование отчёта об уровне покрытия исходного кода.
- `pytest` -- утилита для запуска тестов.
- `pep8` -- утилита для проверки форматирования кода. `E501` (длина строк) отключено.
- `pylint` -- утилита для проверки качества кода. Некоторые правила отключены в отдельных модулях с целью упрощения кода.
- Docker image `python-tools` включает в себя все перечисленные утилиты. Его конфигурация: [Dockerfile](./Dockerfile).

Пример использования и журнал работы процессора на примере `cat`:

``` commandline
hello world
instr_counter:  56 ticks: 100
DEBUG:root:{INSTR: 0, TICK: 0, PC: 0, R0: 0, R1: 0, R2: 0, R3: 0, R4: 0, SP: 10000, MEM[SP]: 0, OP1: r0, OP2: r0, OUT: r1, INT: False}
DEBUG:root:{INSTR: 1, TICK: 1, PC: 1, R0: 0, R1: 0, R2: 0, R3: 0, R4: 0, SP: 10000, MEM[SP]: 0, OP1: r0, OP2: r0, OUT: r1, INT: False} sti   
DEBUG:root:{INSTR: 2, TICK: 5, PC: 3, R0: 0, R1: 0, R2: 0, R3: 0, R4: 0, SP: 9999, MEM[SP]: 0, OP1: sp, OP2: r1, OUT: r1, INT: True} sv  r1 sp
DEBUG:root:{INSTR: 3, TICK: 6, PC: 4, R0: 0, R1: 104, R2: 0, R3: 0, R4: 0, SP: 9999, MEM[SP]: 0, OP1: r0, OP2: r0, OUT: r1, INT: True} in   r1
DEBUG:root:{INSTR: 4, TICK: 7, PC: 5, R0: 0, R1: 104, R2: 0, R3: 0, R4: 0, SP: 9999, MEM[SP]: 0, OP1: r0, OP2: r1, OUT: r1, INT: True} out   r1
DEBUG:root:{INSTR: 5, TICK: 8, PC: 6, R0: 0, R1: 2, R2: 0, R3: 0, R4: 0, SP: 9999, MEM[SP]: 0, OP1: sp, OP2: r0, OUT: r1, INT: True} ld r1  sp
DEBUG:root:{INSTR: 6, TICK: 10, PC: 1, R0: 0, R1: 2, R2: 0, R3: 0, R4: 0, SP: 10000, MEM[SP]: 1, OP1: sp, OP2: r0, OUT: pc, INT: False} iret   
DEBUG:root:{INSTR: 7, TICK: 14, PC: 3, R0: 0, R1: 2, R2: 0, R3: 0, R4: 0, SP: 9999, MEM[SP]: 2, OP1: sp, OP2: r1, OUT: r1, INT: True} sv  r1 sp
DEBUG:root:{INSTR: 8, TICK: 15, PC: 4, R0: 0, R1: 101, R2: 0, R3: 0, R4: 0, SP: 9999, MEM[SP]: 2, OP1: r0, OP2: r0, OUT: r1, INT: True} in   r1
DEBUG:root:{INSTR: 9, TICK: 16, PC: 5, R0: 0, R1: 101, R2: 0, R3: 0, R4: 0, SP: 9999, MEM[SP]: 2, OP1: r0, OP2: r1, OUT: r1, INT: True} out   r1
DEBUG:root:{INSTR: 10, TICK: 17, PC: 6, R0: 0, R1: 2, R2: 0, R3: 0, R4: 0, SP: 9999, MEM[SP]: 2, OP1: sp, OP2: r0, OUT: r1, INT: True} ld r1  sp
DEBUG:root:{INSTR: 11, TICK: 19, PC: 1, R0: 0, R1: 2, R2: 0, R3: 0, R4: 0, SP: 10000, MEM[SP]: 1, OP1: sp, OP2: r0, OUT: pc, INT: False} iret   
DEBUG:root:{INSTR: 12, TICK: 23, PC: 3, R0: 0, R1: 2, R2: 0, R3: 0, R4: 0, SP: 9999, MEM[SP]: 2, OP1: sp, OP2: r1, OUT: r1, INT: True} sv  r1 sp
DEBUG:root:{INSTR: 13, TICK: 24, PC: 4, R0: 0, R1: 108, R2: 0, R3: 0, R4: 0, SP: 9999, MEM[SP]: 2, OP1: r0, OP2: r0, OUT: r1, INT: True} in   r1
DEBUG:root:{INSTR: 14, TICK: 25, PC: 5, R0: 0, R1: 108, R2: 0, R3: 0, R4: 0, SP: 9999, MEM[SP]: 2, OP1: r0, OP2: r1, OUT: r1, INT: True} out   r1
DEBUG:root:{INSTR: 15, TICK: 26, PC: 6, R0: 0, R1: 2, R2: 0, R3: 0, R4: 0, SP: 9999, MEM[SP]: 2, OP1: sp, OP2: r0, OUT: r1, INT: True} ld r1  sp
DEBUG:root:{INSTR: 16, TICK: 28, PC: 1, R0: 0, R1: 2, R2: 0, R3: 0, R4: 0, SP: 10000, MEM[SP]: 1, OP1: sp, OP2: r0, OUT: pc, INT: False} iret   
DEBUG:root:{INSTR: 17, TICK: 32, PC: 3, R0: 0, R1: 2, R2: 0, R3: 0, R4: 0, SP: 9999, MEM[SP]: 2, OP1: sp, OP2: r1, OUT: r1, INT: True} sv  r1 sp
DEBUG:root:{INSTR: 18, TICK: 33, PC: 4, R0: 0, R1: 108, R2: 0, R3: 0, R4: 0, SP: 9999, MEM[SP]: 2, OP1: r0, OP2: r0, OUT: r1, INT: True} in   r1
DEBUG:root:{INSTR: 19, TICK: 34, PC: 5, R0: 0, R1: 108, R2: 0, R3: 0, R4: 0, SP: 9999, MEM[SP]: 2, OP1: r0, OP2: r1, OUT: r1, INT: True} out   r1
DEBUG:root:{INSTR: 20, TICK: 35, PC: 6, R0: 0, R1: 2, R2: 0, R3: 0, R4: 0, SP: 9999, MEM[SP]: 2, OP1: sp, OP2: r0, OUT: r1, INT: True} ld r1  sp
DEBUG:root:{INSTR: 21, TICK: 37, PC: 1, R0: 0, R1: 2, R2: 0, R3: 0, R4: 0, SP: 10000, MEM[SP]: 1, OP1: sp, OP2: r0, OUT: pc, INT: False} iret   
DEBUG:root:{INSTR: 22, TICK: 41, PC: 3, R0: 0, R1: 2, R2: 0, R3: 0, R4: 0, SP: 9999, MEM[SP]: 2, OP1: sp, OP2: r1, OUT: r1, INT: True} sv  r1 sp
DEBUG:root:{INSTR: 23, TICK: 42, PC: 4, R0: 0, R1: 111, R2: 0, R3: 0, R4: 0, SP: 9999, MEM[SP]: 2, OP1: r0, OP2: r0, OUT: r1, INT: True} in   r1
DEBUG:root:{INSTR: 24, TICK: 43, PC: 5, R0: 0, R1: 111, R2: 0, R3: 0, R4: 0, SP: 9999, MEM[SP]: 2, OP1: r0, OP2: r1, OUT: r1, INT: True} out   r1
DEBUG:root:{INSTR: 25, TICK: 44, PC: 6, R0: 0, R1: 2, R2: 0, R3: 0, R4: 0, SP: 9999, MEM[SP]: 2, OP1: sp, OP2: r0, OUT: r1, INT: True} ld r1  sp
DEBUG:root:{INSTR: 26, TICK: 46, PC: 1, R0: 0, R1: 2, R2: 0, R3: 0, R4: 0, SP: 10000, MEM[SP]: 1, OP1: sp, OP2: r0, OUT: pc, INT: False} iret   
DEBUG:root:{INSTR: 27, TICK: 50, PC: 3, R0: 0, R1: 2, R2: 0, R3: 0, R4: 0, SP: 9999, MEM[SP]: 2, OP1: sp, OP2: r1, OUT: r1, INT: True} sv  r1 sp
DEBUG:root:{INSTR: 28, TICK: 51, PC: 4, R0: 0, R1: 32, R2: 0, R3: 0, R4: 0, SP: 9999, MEM[SP]: 2, OP1: r0, OP2: r0, OUT: r1, INT: True} in   r1
DEBUG:root:{INSTR: 29, TICK: 52, PC: 5, R0: 0, R1: 32, R2: 0, R3: 0, R4: 0, SP: 9999, MEM[SP]: 2, OP1: r0, OP2: r1, OUT: r1, INT: True} out   r1
DEBUG:root:{INSTR: 30, TICK: 53, PC: 6, R0: 0, R1: 2, R2: 0, R3: 0, R4: 0, SP: 9999, MEM[SP]: 2, OP1: sp, OP2: r0, OUT: r1, INT: True} ld r1  sp
DEBUG:root:{INSTR: 31, TICK: 55, PC: 1, R0: 0, R1: 2, R2: 0, R3: 0, R4: 0, SP: 10000, MEM[SP]: 1, OP1: sp, OP2: r0, OUT: pc, INT: False} iret   
DEBUG:root:{INSTR: 32, TICK: 59, PC: 3, R0: 0, R1: 2, R2: 0, R3: 0, R4: 0, SP: 9999, MEM[SP]: 2, OP1: sp, OP2: r1, OUT: r1, INT: True} sv  r1 sp
DEBUG:root:{INSTR: 33, TICK: 60, PC: 4, R0: 0, R1: 119, R2: 0, R3: 0, R4: 0, SP: 9999, MEM[SP]: 2, OP1: r0, OP2: r0, OUT: r1, INT: True} in   r1
DEBUG:root:{INSTR: 34, TICK: 61, PC: 5, R0: 0, R1: 119, R2: 0, R3: 0, R4: 0, SP: 9999, MEM[SP]: 2, OP1: r0, OP2: r1, OUT: r1, INT: True} out   r1
DEBUG:root:{INSTR: 35, TICK: 62, PC: 6, R0: 0, R1: 2, R2: 0, R3: 0, R4: 0, SP: 9999, MEM[SP]: 2, OP1: sp, OP2: r0, OUT: r1, INT: True} ld r1  sp
DEBUG:root:{INSTR: 36, TICK: 64, PC: 1, R0: 0, R1: 2, R2: 0, R3: 0, R4: 0, SP: 10000, MEM[SP]: 1, OP1: sp, OP2: r0, OUT: pc, INT: False} iret   
DEBUG:root:{INSTR: 37, TICK: 68, PC: 3, R0: 0, R1: 2, R2: 0, R3: 0, R4: 0, SP: 9999, MEM[SP]: 2, OP1: sp, OP2: r1, OUT: r1, INT: True} sv  r1 sp
DEBUG:root:{INSTR: 38, TICK: 69, PC: 4, R0: 0, R1: 111, R2: 0, R3: 0, R4: 0, SP: 9999, MEM[SP]: 2, OP1: r0, OP2: r0, OUT: r1, INT: True} in   r1
DEBUG:root:{INSTR: 39, TICK: 70, PC: 5, R0: 0, R1: 111, R2: 0, R3: 0, R4: 0, SP: 9999, MEM[SP]: 2, OP1: r0, OP2: r1, OUT: r1, INT: True} out   r1
DEBUG:root:{INSTR: 40, TICK: 71, PC: 6, R0: 0, R1: 2, R2: 0, R3: 0, R4: 0, SP: 9999, MEM[SP]: 2, OP1: sp, OP2: r0, OUT: r1, INT: True} ld r1  sp
DEBUG:root:{INSTR: 41, TICK: 73, PC: 1, R0: 0, R1: 2, R2: 0, R3: 0, R4: 0, SP: 10000, MEM[SP]: 1, OP1: sp, OP2: r0, OUT: pc, INT: False} iret   
DEBUG:root:{INSTR: 42, TICK: 77, PC: 3, R0: 0, R1: 2, R2: 0, R3: 0, R4: 0, SP: 9999, MEM[SP]: 2, OP1: sp, OP2: r1, OUT: r1, INT: True} sv  r1 sp
DEBUG:root:{INSTR: 43, TICK: 78, PC: 4, R0: 0, R1: 114, R2: 0, R3: 0, R4: 0, SP: 9999, MEM[SP]: 2, OP1: r0, OP2: r0, OUT: r1, INT: True} in   r1
DEBUG:root:{INSTR: 44, TICK: 79, PC: 5, R0: 0, R1: 114, R2: 0, R3: 0, R4: 0, SP: 9999, MEM[SP]: 2, OP1: r0, OP2: r1, OUT: r1, INT: True} out   r1
DEBUG:root:{INSTR: 45, TICK: 80, PC: 6, R0: 0, R1: 2, R2: 0, R3: 0, R4: 0, SP: 9999, MEM[SP]: 2, OP1: sp, OP2: r0, OUT: r1, INT: True} ld r1  sp
DEBUG:root:{INSTR: 46, TICK: 82, PC: 1, R0: 0, R1: 2, R2: 0, R3: 0, R4: 0, SP: 10000, MEM[SP]: 1, OP1: sp, OP2: r0, OUT: pc, INT: False} iret   
DEBUG:root:{INSTR: 47, TICK: 86, PC: 3, R0: 0, R1: 2, R2: 0, R3: 0, R4: 0, SP: 9999, MEM[SP]: 2, OP1: sp, OP2: r1, OUT: r1, INT: True} sv  r1 sp
DEBUG:root:{INSTR: 48, TICK: 87, PC: 4, R0: 0, R1: 108, R2: 0, R3: 0, R4: 0, SP: 9999, MEM[SP]: 2, OP1: r0, OP2: r0, OUT: r1, INT: True} in   r1
DEBUG:root:{INSTR: 49, TICK: 88, PC: 5, R0: 0, R1: 108, R2: 0, R3: 0, R4: 0, SP: 9999, MEM[SP]: 2, OP1: r0, OP2: r1, OUT: r1, INT: True} out   r1
DEBUG:root:{INSTR: 50, TICK: 89, PC: 6, R0: 0, R1: 2, R2: 0, R3: 0, R4: 0, SP: 9999, MEM[SP]: 2, OP1: sp, OP2: r0, OUT: r1, INT: True} ld r1  sp
DEBUG:root:{INSTR: 51, TICK: 91, PC: 1, R0: 0, R1: 2, R2: 0, R3: 0, R4: 0, SP: 10000, MEM[SP]: 1, OP1: sp, OP2: r0, OUT: pc, INT: False} iret   
DEBUG:root:{INSTR: 52, TICK: 95, PC: 3, R0: 0, R1: 2, R2: 0, R3: 0, R4: 0, SP: 9999, MEM[SP]: 2, OP1: sp, OP2: r1, OUT: r1, INT: True} sv  r1 sp
DEBUG:root:{INSTR: 53, TICK: 96, PC: 4, R0: 0, R1: 100, R2: 0, R3: 0, R4: 0, SP: 9999, MEM[SP]: 2, OP1: r0, OP2: r0, OUT: r1, INT: True} in   r1
DEBUG:root:{INSTR: 54, TICK: 97, PC: 5, R0: 0, R1: 100, R2: 0, R3: 0, R4: 0, SP: 9999, MEM[SP]: 2, OP1: r0, OP2: r1, OUT: r1, INT: True} out   r1
DEBUG:root:{INSTR: 55, TICK: 98, PC: 6, R0: 0, R1: 2, R2: 0, R3: 0, R4: 0, SP: 9999, MEM[SP]: 2, OP1: sp, OP2: r0, OUT: r1, INT: True} ld r1  sp
DEBUG:root:{INSTR: 56, TICK: 100, PC: 1, R0: 0, R1: 2, R2: 0, R3: 0, R4: 0, SP: 10000, MEM[SP]: 1, OP1: sp, OP2: r0, OUT: pc, INT: False} iret   
INFO:root:output_buffer: 'hello world'
```

| ФИО              | алг.  | LoC | code байт | code инстр. | инстр. | такт. | вариант |
|------------------|-------|-----|-----------|-------------|--------|-------|---------|
| Данилов П. Ю.    | hello | 12  | 1378      | 11          | 11     | 11    | -       |
| Данилов П. Ю.    | cat   | 11  | 770       | 8           | 56     | 100   | -       |
| Данилов П. Ю.    | prob1 | 18  | 2172      | 15          | 6795   | 7262  | -       |

