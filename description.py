
from TM import TM
from UCode import UCode
from RegSet import RegSet
from ISA import ISA

tm = TM()
memTape = tm.addTape(
    name="mem",
    alph={'0', '1'},
    blank='0',
    readOnly=True,
    size= 8 * 2**16)
regTape = tm.addTape(
    name="reg",
    alph={'0', '1', '$', ' '},
    blank=' ',
    readOnly=False,
    size=4096)
ustackTape = tm.addTape(
    name="stack",
    alph={'0', '1', '$', ' '},
    blank=' ',
    readOnly=False,
    size=4096)
ucodeTape = tm.addTape(
    name="ucode",
    alph={'0', '1', '$', ' '},
    blank=' ',
    readOnly=True)

ucode = UCode(tm, regTape, ustackTape, ucodeTape)

@ucode.newUopDecorator('gotoBeginning')
def uopGotoBeginning(uop):
    noDollar = uop.start('noDollar')
    foundDollar = uop.addState('foundDollar')

    noDollar.trans(foundDollar, regTape['$'], regTape.left)
    noDollar.default(noDollar, regTape.left)

    foundDollar.ret(regTape['$'], regTape.left)
    foundDollar.default(noDollar, regTape.left)

@ucode.newUopDecorator('gotoEnd')
def uopGotoEnd(uop):
    state = uop.start('state')

    state.ret(regTape[' '], regTape.left)
    state.default(state, regTape.right)

@ucode.newUopDecorator('nextDollarRight')
def uopNextDollarRight(uop):
    state = uop.start('state', regTape.right)

    state.ret(regTape['$'])
    state.default(state, regTape.right)

@ucode.newUopDecorator('nextDollarLeft')
def uopNextDollarLeft(uop):
    state = uop.start('state', regTape.left)

    state.ret(regTape['$'])
    state.default(state, regTape.left)

@ucode.newUopDecorator('append0')
def uopAppend0(uop):
    state = uop.start('state', regTape.right)
    state.ret(True, regTape.write('0'))

@ucode.newUopDecorator('append1')
def uopAppend1(uop):
    state = uop.start('state', regTape.right)
    state.ret(True, regTape.write('1'))

@ucode.newUopDecorator('appendDollar')
def uopAppendDollar(uop):
    state = uop.start('state', regTape.right)
    state.ret(True, regTape.write('$'))

@ucode.newUopDecorator('deleteMiddleSymbol')
def uopDeleteMiddleSymbol(uop):
    inBlank = uop.start('inBlank', regTape.write(' '))

    readSymbol = uop.addState('readSymbol')
    write0 = uop.addState('write0')
    write1 = uop.addState('write1')
    writeDollar = uop.addState('writeDollar')
    gotoEnd = uop.addState('gotoEnd')

    inBlank.trans(readSymbol, True, regTape.right)

    readSymbol.trans(write0, regTape['0'], regTape.write(' '), regTape.left)
    readSymbol.trans(write1, regTape['1'], regTape.write(' '), regTape.left)
    readSymbol.trans(writeDollar, regTape['$'], regTape.write(' '), regTape.left)
    readSymbol.trans(gotoEnd, regTape[' '], regTape.left)

    write0.trans(inBlank, True, regTape.write('0'), regTape.right)
    write1.trans(inBlank, True, regTape.write('1'), regTape.right)
    writeDollar.trans(inBlank, True, regTape.write('$'), regTape.right)

    gotoEnd.ret(True, regTape.left)

@ucode.newUopDecorator('copyToEnd')
def uopCopyToEnd(uop):
    readSym = uop.start('readSym', regTape.right)
    copy0 = uop.addState('copy0')
    copy1 = uop.addState('copy1')
    reverse0 = uop.addState('reverse0')
    reverse1 = uop.addState('reverse1')
    copyDollar = uop.addState('copyDollar')

    readSym.trans(copy0, regTape['0'], regTape.write(' '), regTape.right)
    readSym.trans(copy1, regTape['1'], regTape.write(' '), regTape.right)
    readSym.trans(copyDollar, regTape['$'], regTape.right)

    copy0.trans(reverse0, regTape[' '], regTape.write('0'), regTape.left)
    copy0.default(copy0, regTape.right)

    reverse0.trans(readSym, regTape[' '], regTape.write('0'), regTape.right)
    reverse0.default(reverse0, regTape.left)

    copy1.trans(reverse1, regTape[' '], regTape.write('1'), regTape.left)
    copy1.default(copy1, regTape.right)

    reverse1.trans(readSym, regTape[' '], regTape.write('1'), regTape.right)
    reverse1.default(reverse1, regTape.left)

    copyDollar.ret(regTape[' '], regTape.write('$'))
    copyDollar.default(copyDollar, regTape.right)

@ucode.newUopDecorator('copyPopFromEnd')
def uopCopyPopFromEnd(uop):
    clearWord = uop.start('clearWord', regTape.right)
    findEnd = uop.addState('findEnd')
    removeLastDollar = uop.addState('removeLastDollar')
    readSym = uop.addState('readSym')
    copy0 = uop.addState('copy0')
    copy1 = uop.addState('copy1')
    findNext = uop.addState('findNext')

    clearWord.trans(findEnd, regTape['$'], regTape.right)
    clearWord.default(clearWord, regTape.write(' '), regTape.right)

    findEnd.trans(removeLastDollar, regTape[' '], regTape.left)
    findEnd.default(findEnd, regTape.right)

    removeLastDollar.trans(readSym, True, regTape.write(' '), regTape.left)
    
    readSym.ret(regTape['$'])
    readSym.trans(copy0, regTape['0'], regTape.write(' '), regTape.left)
    readSym.trans(copy1, regTape['1'], regTape.write(' '), regTape.left)

    copy0.trans(findNext, regTape[' '], regTape.write('0'), regTape.right)
    copy0.default(copy0, regTape.left)

    copy1.trans(findNext, regTape[' '], regTape.write('1'), regTape.right)
    copy1.default(copy1, regTape.left)

    findNext.trans(readSym, regTape[' '], regTape.left)
    findNext.default(findNext, regTape.right)

@ucode.newUopDecorator('popFromEnd')
def uopPopFromEnd(uop):
    state = uop.start('state', regTape.write(' '), regTape.left)
    state.ret(regTape['$'])
    state.default(state, regTape.write(' '), regTape.left)

@ucode.newUopDecorator('deleteEndSymbol')
def uopDeleteEndSymbol(uop):
    state = uop.start('state')
    state.ret(True, regTape.write(' '), regTape.left)

@ucode.newUopDecorator('copyToUstackEnd')
def uopCopyToUstackEnd(uop):
    state = uop.start('state', regTape.right, ustackTape.write('$'), ustackTape.right)
    state.ret(regTape['$'])
    state.trans(state, regTape['0'], ustackTape.write('0'), regTape.right, ustackTape.right)
    state.trans(state, regTape['1'], ustackTape.write('1'), regTape.right, ustackTape.right)

# TODO -- this only handles 1 left per iter, not 8
@ucode.newUopDecorator('memHeadLeft')
def uopMemHeadLeft(uop):
    skipOnes = uop.start('skipOnes', regTape.left, memTape.left)
    rewind = uop.addState('rewind')
    
    skipOnes.ret(regTape['$'])
    skipOnes.trans(skipOnes, regTape['1'], regTape.left)
    skipOnes.trans(rewind, regTape['0'], regTape.write('1'), regTape.right)

    rewind.trans(skipOnes, regTape['$'], regTape.left, memTape.left)
    rewind.default(rewind, regTape.write('0'), regTape.right)

# TODO -- this only handles 1 right per iter, not 8
@ucode.newUopDecorator('memHeadRight')
def uopMemHeadRight(uop):
    skipZeros = uop.start('skipZeros', regTape.left)
    rewind = uop.addState('rewind')
    
    skipZeros.ret(regTape['$'])
    skipZeros.trans(skipZeros, regTape['0'], regTape.left)
    skipZeros.trans(rewind, regTape['1'], regTape.write('0'), regTape.right)

    rewind.trans(skipZeros, regTape['$'], regTape.left, memTape.right)
    rewind.default(rewind, regTape.write('1'), regTape.right)

@ucode.newUopDecorator('overwriteWithMemLoad')
def uopOverwriteWithMemLoad(uop):
    copy = uop.start('copy', regTape.right)
    rewind = uop.addState('rewind')

    copy.trans(rewind, regTape['$'], regTape.left)
    copy.trans(copy, -regTape['$'] & memTape['0'], regTape.write('0'),
        regTape.right, memTape.right)
    copy.trans(copy, -regTape['$'] & memTape['1'], regTape.write('1'),
        regTape.right, memTape.right)
    
    rewind.ret(regTape['$'])
    rewind.default(rewind, regTape.left, memTape.left)

@ucode.newUopDecorator('writeToMem')
def uopWriteToMem(uop):
    copy = uop.start('copy', regTape.right)
    rewind = uop.addState('rewind')

    copy.trans(rewind, regTape['$'], regTape.left)
    copy.trans(copy, regTape['0'], memTape.write('0'), regTape.right, memTape.right)
    copy.trans(copy, regTape['1'], memTape.write('1'), regTape.right, memTape.right)

    rewind.ret(regTape['$'])
    rewind.default(rewind, regTape.left, memTape.left)

# start on end, consume carry & rightmost, results in 2nd from right
@ucode.newUopDecorator('addWithCarry')
def uopAddWithCarry(uop):
    readCarry = uop.start('readCarry', regTape.write(' '), regTape.left)
    carry0Left0 = uop.addState('carry0Left')
    carry1Left0 = uop.addState('carry1Left')
    carry0Left1 = uop.addState('carry0Left1')
    carry1Left1 = uop.addState('carry1Left1')
    carry0 = uop.addState('carry0')
    carry1 = uop.addState('carry1')
    halfAdd0_0 = uop.addState('halfAdd0_0')
    halfAdd1_0 = uop.addState('halfAdd1_0')
    halfAdd2_0 = uop.addState('halfAdd2_0')
    halfAdd0_1 = uop.addState('halfAdd0_1')
    halfAdd1_1 = uop.addState('halfAdd1_1')
    halfAdd2_1 = uop.addState('halfAdd2_1')
    fullAdd0 = uop.addState('fullAdd0')
    fullAdd1 = uop.addState('fullAdd1')
    fullAdd2 = uop.addState('fullAdd2')
    fullAdd3 = uop.addState('fullAdd3')
    carry0Right0 = uop.addState('carry0Right0')
    carry0Right1 = uop.addState('carry0Right1')
    carry1Right0 = uop.addState('carry1Right0')
    carry1Right1 = uop.addState('carry1Right1')
    writeDollar = uop.addState('writeDollar')

    readCarry.trans(carry0Left0, regTape['0'], regTape.write(' '), regTape.left)
    readCarry.trans(carry1Left0, regTape['1'], regTape.write(' '), regTape.left)
    
    carry0Left0.trans(carry0Left1, True, regTape.write(' '), regTape.left)
    carry1Left0.trans(carry1Left1, True, regTape.write(' '), regTape.left)

    carry0Left1.trans(carry0, regTape['$'], regTape.left)
    carry0Left1.default(carry0Left1, regTape.left)

    carry1Left1.trans(carry1, regTape['$'], regTape.left)
    carry1Left1.default(carry1Left1, regTape.left)

    carry0.trans(halfAdd0_0, regTape['0'], regTape.write(' '), regTape.right)
    carry0.trans(halfAdd1_0, regTape['1'], regTape.write(' '), regTape.right)
    carry0.trans(carry0Right0, regTape['$'], regTape.right)

    carry1.trans(halfAdd1_0, regTape['0'], regTape.write(' '), regTape.right)
    carry1.trans(halfAdd2_0, regTape['1'], regTape.write(' '), regTape.right)
    carry1.trans(carry1Right0, regTape['$'], regTape.right)

    halfAdd0_0.trans(halfAdd0_1, regTape[' '], regTape.left)
    halfAdd0_0.default(halfAdd0_0, regTape.right)

    halfAdd1_0.trans(halfAdd1_1, regTape[' '], regTape.left)
    halfAdd1_0.default(halfAdd1_0, regTape.right)

    halfAdd2_0.trans(halfAdd2_1, regTape[' '], regTape.left)
    halfAdd2_0.default(halfAdd2_0, regTape.right)

    halfAdd0_1.trans(fullAdd0, regTape['0'], regTape.write(' '), regTape.left)
    halfAdd0_1.trans(fullAdd1, regTape['1'], regTape.write(' '), regTape.left)
    halfAdd1_1.trans(fullAdd1, regTape['0'], regTape.write(' '), regTape.left)
    halfAdd1_1.trans(fullAdd2, regTape['1'], regTape.write(' '), regTape.left)
    halfAdd2_1.trans(fullAdd2, regTape['0'], regTape.write(' '), regTape.left)
    halfAdd2_1.trans(fullAdd3, regTape['1'], regTape.write(' '), regTape.left)

    fullAdd0.trans(carry0, regTape[' '], regTape.write('0'), regTape.left)
    fullAdd0.default(fullAdd0, regTape.left)

    fullAdd1.trans(carry0, regTape[' '], regTape.write('1'), regTape.left)
    fullAdd1.default(fullAdd1, regTape.left)

    fullAdd2.trans(carry1, regTape[' '], regTape.write('0'), regTape.left)
    fullAdd2.default(fullAdd2, regTape.left)

    fullAdd3.trans(carry1, regTape[' '], regTape.write('1'), regTape.left)
    fullAdd3.default(fullAdd3, regTape.left)

    carry0Right0.trans(carry0Right1, regTape['$'], regTape.right)
    carry0Right0.default(carry0Right0, regTape.right)

    carry1Right0.trans(carry1Right1, regTape['$'], regTape.right)
    carry1Right0.default(carry1Right0, regTape.right)

    carry0Right1.trans(writeDollar, True, regTape.write('0'), regTape.right)
    carry1Right1.trans(writeDollar, True, regTape.write('1'), regTape.right)

    writeDollar.ret(True, regTape.write('$'))

# start on end, consume rightmost, results in 2nd from right
@ucode.newUopDecorator('and')
def uopAnd(uop):
    scanLeft = uop.start('scanLeft', regTape.write(' '), regTape.left)
    readVal = uop.addState('readVal')

    read0_0 = uop.addState('read0_0')
    read1_0 = uop.addState('read1_0')

    read0_1 = uop.addState('read0_1')
    read1_1 = uop.addState('read1_1')

    write0 = uop.addState('write0')
    write1 = uop.addState('write1')

    scanLeft.trans(readVal, regTape['$'], regTape.left)
    scanLeft.default(scanLeft, regTape.left)

    readVal.trans(read0_0, regTape['0'], regTape.write(' '), regTape.right)
    readVal.trans(read1_0, regTape['1'], regTape.write(' '), regTape.right)
    readVal.ret(regTape['$'])

    read0_0.trans(read0_1, regTape[' '], regTape.left)
    read0_0.default(read0_0, regTape.right)

    read1_0.trans(read1_1, regTape[' '], regTape.left)
    read1_0.default(read1_0, regTape.right)

    read0_1.trans(write0, True, regTape.write(' '), regTape.left)

    read1_1.trans(write0, regTape['0'], regTape.write(' '), regTape.left)
    read1_1.trans(write1, regTape['1'], regTape.write(' '), regTape.left)

    write0.trans(readVal, regTape[' '], regTape.write('0'), regTape.left)
    write0.default(write0, regTape.left)

    write1.trans(readVal, regTape[' '], regTape.write('1'), regTape.left)
    write1.default(write1, regTape.left)

# start on end, consume rightmost, results in 2nd from right
@ucode.newUopDecorator('or')
def uopOr(uop):
    scanLeft = uop.start('scanLeft', regTape.write(' '), regTape.left)
    readVal = uop.addState('readVal')

    read0_0 = uop.addState('read0_0')
    read1_0 = uop.addState('read1_0')

    read0_1 = uop.addState('read0_1')
    read1_1 = uop.addState('read1_1')

    write0 = uop.addState('write0')
    write1 = uop.addState('write1')

    scanLeft.trans(readVal, regTape['$'], regTape.left)
    scanLeft.default(scanLeft, regTape.left)

    readVal.trans(read0_0, regTape['0'], regTape.write(' '), regTape.right)
    readVal.trans(read1_0, regTape['1'], regTape.write(' '), regTape.right)
    readVal.ret(regTape['$'])

    read0_0.trans(read0_1, regTape[' '], regTape.left)
    read0_0.default(read0_0, regTape.right)

    read1_0.trans(read1_1, regTape[' '], regTape.left)
    read1_0.default(read1_0, regTape.right)

    read0_1.trans(write0, regTape['0'], regTape.write(' '), regTape.left)
    read0_1.trans(write1, regTape['1'], regTape.write(' '), regTape.left)

    read1_1.trans(write1, True, regTape.write(' '), regTape.left)

    write0.trans(readVal, regTape[' '], regTape.write('0'), regTape.left)
    write0.default(write0, regTape.left)

    write1.trans(readVal, regTape[' '], regTape.write('1'), regTape.left)
    write1.default(write1, regTape.left)

@ucode.newUopDecorator('not')
def uopNot(uop):
    state = uop.start('state', regTape.left)

    state.trans(state, regTape['0'], regTape.write('1'), regTape.left)
    state.trans(state, regTape['1'], regTape.write('0'), regTape.left)
    state.ret(regTape['$'])

@ucode.newUopDecorator('iszero')
def uopIsZero(uop):
    scan = uop.start('scan', regTape.right)
    write0 = uop.addState('write0')
    write1 = uop.addState('write1')

    scan.trans(write0, regTape['1'], regTape.right)
    scan.trans(write1, regTape['$'], regTape.right)
    scan.trans(scan, regTape['0'], regTape.right)

    write0.ret(regTape[' '], regTape.write('0'))
    write0.default(write0, regTape.right)

    write1.ret(regTape[' '], regTape.write('1'))
    write1.default(write1, regTape.right)

@ucode.newUopDecorator('copyMsb')
def uopCopyMsb(uop):
    readBit = uop.start('readBit', regTape.right)
    write0 = uop.addState('write0')
    write1 = uop.addState('write1')

    readBit.trans(write0, regTape['0'], regTape.right)
    readBit.trans(write1, regTape['1'], regTape.right)

    write0.ret(regTape[' '], regTape.write('0'))
    write0.default(write0, regTape.right)

    write1.ret(regTape[' '], regTape.write('1'))
    write1.default(write1, regTape.right)

@ucode.newUopDecorator('copyLsb')
def uopCopyLsb(uop):
    readBit = uop.start('readBit', regTape.left)
    write0 = uop.addState('write0')
    write1 = uop.addState('write1')

    readBit.trans(write0, regTape['0'], regTape.right)
    readBit.trans(write1, regTape['1'], regTape.right)

    write0.ret(regTape[' '], regTape.write('0'))
    write0.default(write0, regTape.right)

    write1.ret(regTape[' '], regTape.write('1'))
    write1.default(write1, regTape.right)


regSet = RegSet(regTape, ucode, uopGotoBeginning, uopNextDollarRight)
reg_MAR = regSet.addReg('MAR', 16, default=0)
reg_PC = regSet.addReg('PC', 16, default=0)
reg_A = regSet.addReg('A', 8, default=0)
reg_X = regSet.addReg('X', 8, default=0)
reg_Y = regSet.addReg('Y', 8, default=0)
reg_SP = regSet.addReg('SP', 8, default=0xFF)
reg_N = regSet.addReg('N', 1, default=0)
reg_V = regSet.addReg('V', 1, default=0)
reg_Z = regSet.addReg('Z', 1, default=1)
reg_C = regSet.addReg('C', 1, default=0)

uinstSetMemHead_left = ucode.newUinst('setMemHead_left', [
    uopPopFromEnd,
    uopDeleteEndSymbol,
    uopAppend0,
    uopAppend0,
    uopAppend0,
    uopAppendDollar,
    uopMemHeadLeft
])

uinstSetMemHead_right = ucode.newUinst('setMemHead_right', [
    uopPopFromEnd,
    uopDeleteEndSymbol,
    uopAppend0,
    uopAppend0,
    uopAppend0,
    uopAppendDollar,
    uopMemHeadRight
])

uinstSetMemHead_finish = ucode.newUinst('setMemHead_finish', [
    uopGotoEnd,
    uopPopFromEnd,
    *reg_MAR.gotoUopSeq,
    uopCopyPopFromEnd
])

uinstSetMemHead = ucode.newUinst('setMemHead', [
    uopNextDollarLeft,
    uopCopyToEnd,
    *reg_MAR.gotoUopSeq,
    uopCopyToEnd,
    uopGotoEnd,
    uopAppend1,
    uopAppendDollar,
    uopNextDollarLeft,
    uopNot,
    uopGotoEnd,
    uopAddWithCarry,
    (uinstSetMemHead_right, uinstSetMemHead_left),
    uinstSetMemHead_finish
])

uinstSetMemHeadToSP = ucode.newUinst('setMemHeadToSP', [
    *(uopAppend0 for _ in range(7)),
    uopAppend1,
    *reg_SP.gotoUopSeq,
    uopCopyToEnd,
    uinstSetMemHead,
])

uinstIncrementEnd = ucode.newUinst('incrementEnd', [
    uopGotoEnd,
    uopNextDollarLeft,
    uopCopyToEnd,
    uopNextDollarLeft,
    uopCopyToEnd,
    uopNot,
    uopGotoEnd,
    uopAnd,
    uopGotoEnd,
    uopAppend1,
    uopAppendDollar,
    uopAddWithCarry,
    uopPopFromEnd,
])

# leaves carry bit on the end
uinstDecrementEnd = ucode.newUinst('decrementEnd', [
    uopGotoEnd,
    uopNextDollarLeft,
    uopCopyToEnd,
    uopNextDollarLeft,
    uopCopyToEnd,
    uopNot,
    uopGotoEnd,
    uopOr,
    uopGotoEnd,
    uopAppend0,
    uopAppendDollar,
    uopAddWithCarry,
    uopPopFromEnd,
])


uinstSetAddrModeImmd = ucode.newUinst('setAddrModeImmd', [
    *reg_PC.gotoUopSeq,
    uopCopyToEnd,
    uopNextDollarLeft,
    uopCopyToEnd,

    uinstIncrementEnd,
    ucode.newUinst('setAddrModeImmd_saveIncPC', [
        *reg_PC.gotoUopSeq,
        uopCopyPopFromEnd
    ]),

    uinstSetMemHead
])

uinstLoadMemByte = ucode.newUinst('loadMemByte', [
    *reg_A.gotoUopSeq,
    uopCopyToEnd,
    uopNextDollarLeft,
    uopOverwriteWithMemLoad,
    uopGotoEnd,
])

uinstStoreMemByte = ucode.newUinst('storeMemByte', [
    uopGotoEnd,
    uopNextDollarLeft,
    uopWriteToMem,
    uopGotoEnd,
    uopPopFromEnd,
])

uinstLoadMem16_cleanup = ucode.newUinst('loadMem16_cleanup', [
    uopGotoEnd,
    uopDeleteEndSymbol,
    uopNextDollarLeft,
    uopNextDollarLeft,
    uopCopyToEnd,
    uopNextDollarLeft,
    uopNextDollarLeft,
    uopNextDollarLeft,
    uopCopyPopFromEnd,
    uopGotoEnd,
    uopPopFromEnd
])

uinstLoadMem16 = ucode.newUinst('loadMem16', [
    *reg_MAR.gotoUopSeq,
    uopCopyToEnd,
    uinstLoadMemByte,
    ucode.newUinst('loadMem16_incMAR', [
        *reg_MAR.gotoUopSeq,
        uopCopyToEnd,
        uinstIncrementEnd,
    ]),
    uinstSetMemHead,
    uinstLoadMemByte,
    uinstLoadMem16_cleanup,
])

uinstLoadImm16 = ucode.newUinst('loadImm16', [
    *reg_MAR.gotoUopSeq,
    uopCopyToEnd,
    uinstSetAddrModeImmd,
    uinstLoadMemByte,
    uinstSetAddrModeImmd,
    uinstLoadMemByte,
    uinstLoadMem16_cleanup,
])

uinstLoadPC = ucode.newUinst('loadPC', [
    *reg_PC.gotoUopSeq,
    uopCopyToEnd,
])

uinstLoadA = ucode.newUinst('loadA', [
    *reg_A.gotoUopSeq,
    uopCopyToEnd,
])

uinstLoadX = ucode.newUinst('loadX', [
    *reg_X.gotoUopSeq,
    uopCopyToEnd,
])

uinstLoadY = ucode.newUinst('loadY', [
    *reg_Y.gotoUopSeq,
    uopCopyToEnd,
])

uinstLoadSP = ucode.newUinst('loadSP', [
    *reg_SP.gotoUopSeq,
    uopCopyToEnd,
])

uinstStorePC = ucode.newUinst('storePC', [
    *reg_PC.gotoUopSeq,
    uopCopyPopFromEnd,
])

uinstStoreA = ucode.newUinst('storeA', [
    *reg_A.gotoUopSeq,
    uopCopyPopFromEnd,
])

uinstStoreX = ucode.newUinst('storeX', [
    *reg_X.gotoUopSeq,
    uopCopyPopFromEnd,
])

uinstStoreY = ucode.newUinst('storeY', [
    *reg_Y.gotoUopSeq,
    uopCopyPopFromEnd,
])

uinstStoreSP = ucode.newUinst('storeSP', [
    *reg_SP.gotoUopSeq,
    uopCopyPopFromEnd,
])

uinstStoreNull = ucode.newUinst('storeNull', [
    uopGotoEnd,
    uopPopFromEnd
])

uinstSetAddrModeZeroPage_setup = ucode.newUinst('setAddrModeZeroPage_setup', [
    uopGotoEnd,
    *(uopAppend0 for _ in range(8)),
    uopAppendDollar,
    uinstSetAddrModeImmd,
    uinstLoadMemByte,
])

uinstSetAddrModeZeroPage = ucode.newUinst('setAddrModeZeroPage', [
    uinstSetAddrModeZeroPage_setup,
    ucode.newUinst('setAddrModeZeroPage_finish', [
        uopGotoEnd,
        uopNextDollarLeft,
        uopDeleteMiddleSymbol,
        uinstSetMemHead,
    ])
])

uinstSetAddrModeZeroPageX = ucode.newUinst('setAddrModeZeroPageX', [
    uinstSetAddrModeZeroPage_setup,
    ucode.newUinst('setAddrModeZeroPageX_finish', [
        *reg_X.gotoUopSeq,
        uopCopyToEnd,
        uopAppend0,
        uopAppendDollar,
        uopAddWithCarry,
        uopPopFromEnd,
        uopNextDollarLeft,
        uopDeleteMiddleSymbol,
        uinstSetMemHead,
    ])
])

uinstSetAddrModeZeroPageY = ucode.newUinst('setAddrModeZeroPageY', [
    uinstSetAddrModeZeroPage_setup,
    ucode.newUinst('setAddrModeZeroPageY_finish', [
        *reg_Y.gotoUopSeq,
        uopCopyToEnd,
        uopAppend0,
        uopAppendDollar,
        uopAddWithCarry,
        uopPopFromEnd,
        uopNextDollarLeft,
        uopDeleteMiddleSymbol,
        uinstSetMemHead,
    ])
])

uinstSetAddrModeAbsolute = ucode.newUinst('setAddrModeAbsolute', [
    uinstLoadImm16,
    uinstSetMemHead,
])

uinstSetAddrModeAbsoluteX = ucode.newUinst('setAddrModeAbsoluteX', [
    uinstLoadImm16,
    ucode.newUinst('setAddrModeAbsoluteX_addX', [
        *(uopAppend0 for _ in range(8)),
        *reg_X.gotoUopSeq,
        uopCopyToEnd,
        uopAppend0,
        uopAppendDollar,
        uopAddWithCarry,
        uopPopFromEnd,
    ]),
    uinstSetMemHead,
])

uinstAddYZext16 = ucode.newUinst('addYZext16', [
    *(uopAppend0 for _ in range(8)),
    *reg_Y.gotoUopSeq,
    uopCopyToEnd,
    uopAppend0,
    uopAppendDollar,
    uopAddWithCarry,
    uopPopFromEnd,
])

uinstSetAddrModeAbsoluteY = ucode.newUinst('setAddrModeAbsoluteY', [
    uinstLoadImm16,
    uinstAddYZext16,
    uinstSetMemHead,
])

uinstSetAddrModeIndirectX = ucode.newUinst('setAddrmodeIndirectX', [
    uinstSetAddrModeZeroPageX,
    uinstLoadMem16,
    uinstSetMemHead
])

uinstSetAddrModeIndirectY = ucode.newUinst('setAddrmodeIndirectY', [
    uinstSetAddrModeZeroPage,
    uinstLoadMem16,
    uinstAddYZext16,
    uinstSetMemHead,
])

uinstDoNextInstruction = ucode.newUinst('doNextInstruction', [
    uinstSetAddrModeImmd,
    uinstLoadMemByte,
    ucode.newUinst('doNextInstruction_copyInstToUstack', [
        uopNextDollarLeft,
        uopCopyToUstackEnd,
        uopPopFromEnd
    ])
])

uinstSetZNFlags = ucode.newUinst('setZNflags', [
    uopGotoEnd,
    uopNextDollarLeft,
    uopIsZero,
    uopAppendDollar,
    *reg_Z.gotoUopSeq,
    uopCopyPopFromEnd,
    uopGotoEnd,
    uopNextDollarLeft,
    uopCopyMsb,
    uopAppendDollar,
    *reg_N.gotoUopSeq,
    uopCopyPopFromEnd,
])

uinstComputeOR = ucode.newUinst('computeOR', [
    uopOr,
    uinstSetZNFlags
])

uinstComputeAND = ucode.newUinst('computeAND', [
    uopAnd,
    uinstSetZNFlags
])

uinstComputeEOR = ucode.newUinst('computeEOR', [
    uopNextDollarLeft,
    uopNextDollarLeft,
    uopCopyToEnd,
    uopNextDollarLeft,
    uopNextDollarLeft,
    uopCopyToEnd,
    uopNot,
    uopNextDollarLeft,
    uopCopyToEnd,
    uopAnd,
    uopNot,
    uopNextDollarLeft,
    uopNextDollarLeft,
    uopCopyPopFromEnd,
    uopAnd,
    uopGotoEnd,
    uopOr,
    uinstSetZNFlags
])

uinstComputeASL = ucode.newUinst('computeASL', [
    uopDeleteEndSymbol,
    uopAppend0,
    uopAppendDollar,
    uopNextDollarLeft,
    uopCopyMsb,
    uopAppendDollar,
    *reg_C.gotoUopSeq,
    uopCopyPopFromEnd,
    uopNextDollarLeft,
    uopAppendDollar,
    uopDeleteMiddleSymbol,
    uinstSetZNFlags
])

uinstComputeROL = ucode.newUinst('computeROL', [
    uopDeleteEndSymbol,
    *reg_C.gotoUopSeq,
    uopCopyToEnd,
    uopNextDollarLeft,
    uopCopyMsb,
    uopAppendDollar,
    *reg_C.gotoUopSeq,
    uopCopyPopFromEnd,
    uopNextDollarLeft,
    uopAppendDollar,
    uopDeleteMiddleSymbol,
    uinstSetZNFlags
])

uinstComputeLSR = ucode.newUinst('computeLSR', [
    uopAppend0,
    uopNextDollarLeft,
    uopNextDollarLeft,
    uopCopyToEnd,
    uopCopyLsb,
    uopAppendDollar,
    *reg_C.gotoUopSeq,
    uopCopyPopFromEnd,
    uopDeleteEndSymbol,
    uopDeleteEndSymbol,
    uopAppendDollar,
    uopNextDollarLeft,
    uopNextDollarLeft,
    uopCopyPopFromEnd,
    uinstSetZNFlags
])

uinstComputeROR = ucode.newUinst('computeROR', [
    *reg_C.gotoUopSeq,
    uopCopyMsb,
    uopNextDollarLeft,
    uopNextDollarLeft,
    uopCopyToEnd,
    uopCopyLsb,
    uopAppendDollar,
    *reg_C.gotoUopSeq,
    uopCopyPopFromEnd,
    uopDeleteEndSymbol,
    uopDeleteEndSymbol,
    uopAppendDollar,
    uopNextDollarLeft,
    uopNextDollarLeft,
    uopCopyPopFromEnd,
    uinstSetZNFlags
])

uinstComputeADC = ucode.newUinst('computeADC', [
    uopNextDollarLeft,
    uopNextDollarLeft,
    uopCopyToEnd,
    uopNextDollarLeft,
    uopNextDollarLeft,
    uopCopyToEnd,
    *reg_C.gotoUopSeq,
    uopCopyToEnd,
    uopAddWithCarry,
    *reg_C.gotoUopSeq,
    uopCopyPopFromEnd,

    uopNextDollarLeft,
    uopNextDollarLeft,
    uopNextDollarLeft,
    uopCopyMsb,
    uopAppendDollar,
    uopNextDollarLeft,
    uopNextDollarLeft,
    uopNextDollarLeft,
    uopCopyMsb,
    uopAppendDollar,
    uopAppend0,
    uopAppendDollar,
    uopAddWithCarry,
    uopNextDollarLeft,
    uopNot,
    uopNextDollarLeft,
    uopCopyMsb,
    uopAppendDollar,
    uopAppend0,
    uopAppendDollar,
    uopAddWithCarry,
    uopPopFromEnd,
    uopAnd,
    *reg_V.gotoUopSeq,

    uopCopyPopFromEnd,
    uopNextDollarLeft,
    uopNextDollarLeft,
    uopNextDollarLeft,
    uopCopyPopFromEnd,
    uopPopFromEnd,

    uinstSetZNFlags
])

uinstComputeSBC = ucode.newUinst('computeSBC', [
    uopNot,
    uopGotoEnd,
    uinstComputeADC
])

uinstComputeCMP = ucode.newUinst('computeCMP', [
    uopNot,
    uopGotoEnd,
    uopAppend1,
    uopAppendDollar,
    uopAddWithCarry,
    *reg_C.gotoUopSeq,
    uopCopyPopFromEnd,
    uinstSetZNFlags
])

uinstComputeINC = ucode.newUinst('computeINC', [
    uinstIncrementEnd,
    uinstSetZNFlags
])

uinstComputeDEC = ucode.newUinst('computeDEC', [
    uinstIncrementEnd,
    uinstSetZNFlags
])

uinstComputeBIT = ucode.newUinst('computeBIT', [
    uopNextDollarLeft,
    uopCopyToEnd,
    uopNextDollarLeft,
    uopCopyMsb,
    uopAppendDollar,
    *reg_N.gotoUopSeq,
    uopCopyPopFromEnd,
    uopNextDollarLeft,
    uopAppendDollar,
    uopCopyMsb,
    uopAppendDollar,
    uopNextDollarLeft,
    uopNextDollarLeft,
    uopNextDollarLeft,
    uopAppend0,
    *reg_V.gotoUopSeq,
    uopCopyPopFromEnd,
    uopPopFromEnd,
    uopAnd,
    uopIsZero,
    uopAppendDollar,
    *reg_Z.gotoUopSeq,
    uopCopyPopFromEnd,
])

uinstSignExtAdd16 = ucode.newUinst('signExtAdd16', [
    uopGotoEnd,
    uopNextDollarLeft,
    uopCopyToEnd,
    uopNextDollarLeft,
    uopNextDollarLeft,
    *(uopAppend0 for _ in range(8)),

    uopNextDollarRight,
    uopCopyMsb,
    uopAppendDollar,

    (ucode.newUinst('signExtAdd16_isnegative', [
        uopNot,
        uopNextDollarLeft,
        uopNot,
        uopGotoEnd
    ]),[]),

    ucode.newUinst('signExtAdd16_finish', [
        uopNextDollarLeft,
        uopNextDollarLeft,
        uopDeleteMiddleSymbol,
        uopAddWithCarry,
        uopPopFromEnd
    ])
])

uinstBranchNotTaken = ucode.newUinst('branchNotTaken', [
    uopGotoEnd,
    uopPopFromEnd
])

uinstComputeBPL = ucode.newUinst('computeBPL', [
    *(reg_N.gotoUopSeq),
    uopNextDollarRight,
    (uinstBranchNotTaken, uinstSignExtAdd16)
])

uinstComputeBMI = ucode.newUinst('computeBMI', [
    *(reg_N.gotoUopSeq),
    uopNextDollarRight,
    (uinstSignExtAdd16, uinstBranchNotTaken)
])

uinstComputeBVC = ucode.newUinst('computeBVC', [
    *(reg_V.gotoUopSeq),
    uopNextDollarRight,
    (uinstBranchNotTaken, uinstSignExtAdd16)
])

uinstComputeBVS = ucode.newUinst('computeBVS', [
    *(reg_V.gotoUopSeq),
    uopNextDollarRight,
    (uinstSignExtAdd16, uinstBranchNotTaken)
])

uinstComputeBCC = ucode.newUinst('computeBCC', [
    *(reg_C.gotoUopSeq),
    uopNextDollarRight,
    (uinstBranchNotTaken, uinstSignExtAdd16)
])

uinstComputeBCS = ucode.newUinst('computeBCS', [
    *(reg_C.gotoUopSeq),
    uopNextDollarRight,
    (uinstSignExtAdd16, uinstBranchNotTaken)
])

uinstComputeBNE = ucode.newUinst('computeBNE', [
    *(reg_Z.gotoUopSeq),
    uopNextDollarRight,
    (uinstBranchNotTaken, uinstSignExtAdd16)
])

uinstComputeBEQ = ucode.newUinst('computeBEQ', [
    *(reg_Z.gotoUopSeq),
    uopNextDollarRight,
    (uinstSignExtAdd16, uinstBranchNotTaken)
])

uinstComputeCLC = ucode.newUinst('computeCLC', [
    *(reg_C.gotoUopSeq),
    uopAppend0,
    uopGotoEnd
])

uinstComputeSEC = ucode.newUinst('computeSEC', [
    *(reg_C.gotoUopSeq),
    uopAppend1,
    uopGotoEnd
])

uinstComputeCLV = ucode.newUinst('computeCLV', [
    *(reg_V.gotoUopSeq),
    uopAppend0,
    uopGotoEnd
])

uinstSetAddrModePush = ucode.newUinst('setAddrModePush', [
    uinstSetMemHeadToSP,
    ucode.newUinst('setAddrModePush_decSP', [
        *(reg_SP.gotoUopSeq),
        uopCopyToEnd,
        uinstDecrementEnd,
        ucode.newUinst('setAddrModePush_decSP_finish', [
            *(reg_SP.gotoUopSeq),
            uopCopyPopFromEnd,
        ])
    ])
])

uinstSetAddrModePull = ucode.newUinst('setAddrModePull', [
    *(reg_SP.gotoUopSeq),
    uopCopyToEnd,
    uinstIncrementEnd,
    ucode.newUinst('setAddrModePull_incSP_finish', [
        *(reg_SP.gotoUopSeq),
        uopCopyPopFromEnd,
    ]),
    uinstSetMemHeadToSP,
])

# have to wrap with loading and storing PC
uinstComputeJSR = ucode.newUinst('uinstComputeJSR', [
    uinstSetAddrModeImmd,
    uinstSetAddrModePush,
    ucode.newUinst('doInstructionJSR_storeHiPI', [
        *(reg_PC.gotoUopSeq),
        uopCopyToEnd,
        *(uopDeleteEndSymbol for _ in range(9)),
        uopAppendDollar,
        uinstStoreMemByte
    ]),
    uinstSetAddrModePush,
    ucode.newUinst('doInstructionJSR_storeLoPC', [
        uopAppend0,
        *(reg_PC.gotoUopSeq),
        uopCopyToEnd,
        uopNextDollarLeft,
        *(uopAppend0 for _ in range(8)),
        uopAppendDollar,
        uopNextDollarLeft,
        uopCopyPopFromEnd,
        uinstStoreMemByte
    ]),
    uinstSetMemHead,
    uinstLoadMem16,
])

uinstComputeRTS = ucode.newUinst('uinstComputeRTS', [
    uinstSetAddrModePull,
    uinstLoadMemByte,
    uinstLoadMemByte,
    uinstSetAddrModePull,
    uinstLoadMemByte,
    ucode.newUinst('uinstComputeRTS_cleanup', [
        uopNextDollarLeft,
        uopNextDollarLeft,
        uopNextDollarLeft,
        uopCopyPopFromEnd,
        uopNextDollarLeft,
        uopDeleteMiddleSymbol,
    ])
])

uinstLoadFlagsByte = ucode.newUinst('uinstLoadFlagsByte', [
    *(reg_N.gotoUopSeq),
    uopCopyMsb,
    *(reg_V.gotoUopSeq),
    uopCopyMsb,
    uopAppend1,
    uopAppend1,
    uopAppend0,
    uopAppend1,
    *(reg_Z.gotoUopSeq),
    uopCopyMsb,
    *(reg_C.gotoUopSeq),
    uopCopyMsb,
    uopAppendDollar
])

uinstStoreFlagsByte = ucode.newUinst('uinstStoreFlagsByte', [
    uopCopyLsb,
    uopAppendDollar,
    *(reg_C.gotoUopSeq),
    uopCopyPopFromEnd,

    uopDeleteEndSymbol,
    uopDeleteEndSymbol,
    uopAppendDollar,
    uopCopyLsb,
    uopAppendDollar,
    *(reg_Z.gotoUopSeq),
    uopCopyPopFromEnd,

    uopDeleteEndSymbol,
    uopDeleteEndSymbol,
    uopDeleteEndSymbol,
    uopDeleteEndSymbol,
    uopDeleteEndSymbol,
    uopDeleteEndSymbol,
    uopAppendDollar,
    uopCopyLsb,
    uopAppendDollar,
    *(reg_V.gotoUopSeq),
    uopCopyPopFromEnd,

    uopDeleteEndSymbol,
    uopDeleteEndSymbol,
    uopAppendDollar,
    *(reg_N.gotoUopSeq),
    uopCopyPopFromEnd,
])

################################################################################

isa = ISA(
    ucode = ucode,
    addrModes = {
        'immd'      : uinstSetAddrModeImmd,
        'zro'       : uinstSetAddrModeZeroPage,
        'zroX'      : uinstSetAddrModeZeroPageX,
        'zroY'      : uinstSetAddrModeZeroPageY,
        'abs'       : uinstSetAddrModeAbsolute,
        'absX'      : uinstSetAddrModeAbsoluteX,
        'absY'      : uinstSetAddrModeAbsoluteY,
        'indX'      : uinstSetAddrModeIndirectX,
        'indY'      : uinstSetAddrModeIndirectY,
        'push'      : uinstSetAddrModePush,
        'pull'      : uinstSetAddrModePull,
    },
    loads = {
        'flags'     : uinstLoadFlagsByte,
        'mem'       : uinstLoadMemByte,
        'mem16'     : uinstLoadMem16,
        'PC'        : uinstLoadPC,
        'A'         : uinstLoadA,
        'X'         : uinstLoadX,
        'Y'         : uinstLoadY,
        'SP'        : uinstLoadSP,
    },
    computes = {
        'OR'        : uinstComputeOR,
        'AND'       : uinstComputeAND,
        'EOR'       : uinstComputeEOR,
        'ASL'       : uinstComputeASL,
        'ROL'       : uinstComputeROL,
        'LSR'       : uinstComputeLSR,
        'ROR'       : uinstComputeROR,
        'ADC'       : uinstComputeADC,
        'SBC'       : uinstComputeSBC,
        'CMP'       : uinstComputeCMP,
        'INC'       : uinstComputeINC,
        'DEC'       : uinstComputeDEC,
        'BIT'       : uinstComputeBIT,
        'BPL'       : uinstComputeBPL,
        'BMI'       : uinstComputeBMI,
        'BVC'       : uinstComputeBVC,
        'BVS'       : uinstComputeBVS,
        'BCC'       : uinstComputeBCC,
        'BCS'       : uinstComputeBCS,
        'BNE'       : uinstComputeBNE,
        'BEQ'       : uinstComputeBEQ,
        'CLC'       : uinstComputeCLC,
        'SEC'       : uinstComputeSEC,
        'CLV'       : uinstComputeCLV,
        'JSR'       : uinstComputeJSR,
        'RTS'       : uinstComputeRTS,
        'ZN'        : uinstSetZNFlags,
    },
    stores = {
        'flags'     : uinstStoreFlagsByte,
        'mem'       : uinstStoreMemByte,
        'PC'        : uinstStorePC,
        'A'         : uinstStoreA,
        'X'         : uinstStoreX,
        'Y'         : uinstStoreY,
        'SP'        : uinstStoreSP,
        'null'      : uinstStoreNull,
    },
    uinstNextInst = uinstDoNextInstruction,
)

isa.newInst('DEY', 0x88, load='Y', compute='DEC', store='Y')

isa.newInst('TAY', 0xA8, load='A', compute='ZN', store='Y')

isa.newInst('INY', 0xC8, load='Y', compute='INC', store='Y')

isa.newInst('INX', 0xE8, load='X', compute='INC', store='X')

isa.newInst('PHA', 0x48, addrMode='push', load='A', store='mem')

isa.newInst('PHP', 0x08, addrMode='push', load='flags', store='mem')

isa.newInst('PLA', 0x68, addrMode='pull', load='mem', store='A')

isa.newInst('PLP', 0x28, addrMode='pull', load='mem', store='flags')

isa.newInst('BPL', 0x10, addrMode='immd', load=('PC', 'mem'), compute='BPL', store='PC')
isa.newInst('BMI', 0x30, addrMode='immd', load=('PC', 'mem'), compute='BMI', store='PC')
isa.newInst('BVC', 0x50, addrMode='immd', load=('PC', 'mem'), compute='BVC', store='PC')
isa.newInst('BVS', 0x70, addrMode='immd', load=('PC', 'mem'), compute='BVS', store='PC')
isa.newInst('BCC', 0x90, addrMode='immd', load=('PC', 'mem'), compute='BCC', store='PC')
isa.newInst('BCS', 0xB0, addrMode='immd', load=('PC', 'mem'), compute='BCS', store='PC')
isa.newInst('BNE', 0xD0, addrMode='immd', load=('PC', 'mem'), compute='BNE', store='PC')
isa.newInst('BEQ', 0xF0, addrMode='immd', load=('PC', 'mem'), compute='BEQ', store='PC')

isa.newInst('CLC', 0x18, compute='CLC')
isa.newInst('SEC', 0x38, compute='SEC')
isa.newInst('CLV', 0xB8, compute='CLV')

isa.newInst('TYA', 0x98, load='Y', compute='ZN', store='A')

isa.newInst('TAX', 0xAA, load='A', compute='ZN', store='X')

isa.newInst('TSX', 0xBA, load='SP', compute='ZN', store='X')

isa.newInst('TXA', 0x8A, load='X', compute='ZN', store='A')

isa.newInst('TXS', 0x9A, load='X', store='SP')

isa.newInst('DEX', 0xCA, load='X', compute='DEC', store='X')

isa.newInst('NOP', 0xEA)

isa.newInst('JSR', 0x20, load='PC', compute='JSR', store='PC')

isa.newInst('RTS', 0x60, load='PC', compute='RTS', store='PC')

isa.newInst('JMP', 0x4C, addrMode='immd', load='mem16', store='PC')
isa.newInst('JMP', 0x6C, addrMode='abs',  load='mem16', store='PC')

isa.newInst('BIT', 0x24, addrMode='zro', load=('A', 'mem'), compute='BIT', store='null')
isa.newInst('BIT', 0x2C, addrMode='abs', load=('A', 'mem'), compute='BIT', store='null')

isa.newInst('STY', 0x84, addrMode='zro',  load='Y', store='mem')
isa.newInst('STY', 0x94, addrMode='zroX', load='Y', store='mem')
isa.newInst('STY', 0x8C, addrMode='abs',  load='Y', store='mem')

isa.newInst('LDY', 0xA0, addrMode='immd', load='mem', compute='ZN', store='Y')
isa.newInst('LDY', 0xA4, addrMode='zro',  load='mem', compute='ZN', store='Y')
isa.newInst('LDY', 0xB4, addrMode='zroX', load='mem', compute='ZN', store='Y')
isa.newInst('LDY', 0xAC, addrMode='abs',  load='mem', compute='ZN', store='Y')
isa.newInst('LDY', 0xBC, addrMode='absX', load='mem', compute='ZN', store='Y')

isa.newInst('CPY', 0xC0, addrMode='immd', load=('Y', 'mem'), compute='CMP', store='null')
isa.newInst('CPY', 0xC4, addrMode='zro',  load=('Y', 'mem'), compute='CMP', store='null')
isa.newInst('CPY', 0xCC, addrMode='abs',  load=('Y', 'mem'), compute='CMP', store='null')

isa.newInst('CPX', 0xE0, addrMode='immd', load=('X', 'mem'), compute='CMP', store='null')
isa.newInst('CPX', 0xE4, addrMode='zro',  load=('X', 'mem'), compute='CMP', store='null')
isa.newInst('CPX', 0xEC, addrMode='abs',  load=('X', 'mem'), compute='CMP', store='null')

isa.newInst('AND', 0x29, addrMode='immd', load=('A', 'mem'), compute='AND', store='A')
isa.newInst('AND', 0x25, addrMode='zro',  load=('A', 'mem'), compute='AND', store='A')
isa.newInst('AND', 0x35, addrMode='zroX', load=('A', 'mem'), compute='AND', store='A')
isa.newInst('AND', 0x2D, addrMode='abs',  load=('A', 'mem'), compute='AND', store='A')
isa.newInst('AND', 0x3D, addrMode='absX', load=('A', 'mem'), compute='AND', store='A')
isa.newInst('AND', 0x39, addrMode='absY', load=('A', 'mem'), compute='AND', store='A')
isa.newInst('AND', 0x21, addrMode='indX', load=('A', 'mem'), compute='AND', store='A')
isa.newInst('AND', 0x31, addrMode='indY', load=('A', 'mem'), compute='AND', store='A')

isa.newInst('ORA', 0x09, addrMode='immd', load=('A', 'mem'), compute='OR', store='A')
isa.newInst('ORA', 0x05, addrMode='zro',  load=('A', 'mem'), compute='OR', store='A')
isa.newInst('ORA', 0x15, addrMode='zroX', load=('A', 'mem'), compute='OR', store='A')
isa.newInst('ORA', 0x0D, addrMode='abs',  load=('A', 'mem'), compute='OR', store='A')
isa.newInst('ORA', 0x1D, addrMode='absX', load=('A', 'mem'), compute='OR', store='A')
isa.newInst('ORA', 0x19, addrMode='absY', load=('A', 'mem'), compute='OR', store='A')
isa.newInst('ORA', 0x01, addrMode='indX', load=('A', 'mem'), compute='OR', store='A')
isa.newInst('ORA', 0x11, addrMode='indY', load=('A', 'mem'), compute='OR', store='A')

isa.newInst('EOR', 0x49, addrMode='immd', load=('A', 'mem'), compute='EOR', store='A')
isa.newInst('EOR', 0x45, addrMode='zro',  load=('A', 'mem'), compute='EOR', store='A')
isa.newInst('EOR', 0x55, addrMode='zroX', load=('A', 'mem'), compute='EOR', store='A')
isa.newInst('EOR', 0x4D, addrMode='abs',  load=('A', 'mem'), compute='EOR', store='A')
isa.newInst('EOR', 0x5D, addrMode='absX', load=('A', 'mem'), compute='EOR', store='A')
isa.newInst('EOR', 0x59, addrMode='absY', load=('A', 'mem'), compute='EOR', store='A')
isa.newInst('EOR', 0x41, addrMode='indX', load=('A', 'mem'), compute='EOR', store='A')
isa.newInst('EOR', 0x51, addrMode='indY', load=('A', 'mem'), compute='EOR', store='A')

isa.newInst('ADC', 0x69, addrMode='immd', load=('A', 'mem'), compute='ADC', store='A')
isa.newInst('ADC', 0x65, addrMode='zro',  load=('A', 'mem'), compute='ADC', store='A')
isa.newInst('ADC', 0x75, addrMode='zroX', load=('A', 'mem'), compute='ADC', store='A')
isa.newInst('ADC', 0x6D, addrMode='abs',  load=('A', 'mem'), compute='ADC', store='A')
isa.newInst('ADC', 0x7D, addrMode='absX', load=('A', 'mem'), compute='ADC', store='A')
isa.newInst('ADC', 0x79, addrMode='absY', load=('A', 'mem'), compute='ADC', store='A')
isa.newInst('ADC', 0x61, addrMode='indX', load=('A', 'mem'), compute='ADC', store='A')
isa.newInst('ADC', 0x71, addrMode='indY', load=('A', 'mem'), compute='ADC', store='A')

isa.newInst('STA', 0x85, addrMode='zro',  load='A', store='mem')
isa.newInst('STA', 0x95, addrMode='zroX', load='A', store='mem')
isa.newInst('STA', 0x8D, addrMode='abs',  load='A', store='mem')
isa.newInst('STA', 0x9D, addrMode='absX', load='A', store='mem')
isa.newInst('STA', 0x99, addrMode='absY', load='A', store='mem')
isa.newInst('STA', 0x81, addrMode='indX', load='A', store='mem')
isa.newInst('STA', 0x91, addrMode='indY', load='A', store='mem')

isa.newInst('LDA', 0xA9, addrMode='immd', load='mem', compute='ZN', store='A')
isa.newInst('LDA', 0xA5, addrMode='zro',  load='mem', compute='ZN', store='A')
isa.newInst('LDA', 0xB5, addrMode='zroX', load='mem', compute='ZN', store='A')
isa.newInst('LDA', 0xAD, addrMode='abs',  load='mem', compute='ZN', store='A')
isa.newInst('LDA', 0xBD, addrMode='absX', load='mem', compute='ZN', store='A')
isa.newInst('LDA', 0xB9, addrMode='absY', load='mem', compute='ZN', store='A')
isa.newInst('LDA', 0xA1, addrMode='indX', load='mem', compute='ZN', store='A')
isa.newInst('LDA', 0xB1, addrMode='indY', load='mem', compute='ZN', store='A')

isa.newInst('CMP', 0xC9, addrMode='immd', load=('A', 'mem'), compute='CMP', store='null')
isa.newInst('CMP', 0xC5, addrMode='zro',  load=('A', 'mem'), compute='CMP', store='null')
isa.newInst('CMP', 0xD5, addrMode='zroX', load=('A', 'mem'), compute='CMP', store='null')
isa.newInst('CMP', 0xCD, addrMode='abs',  load=('A', 'mem'), compute='CMP', store='null')
isa.newInst('CMP', 0xDD, addrMode='absX', load=('A', 'mem'), compute='CMP', store='null')
isa.newInst('CMP', 0xD9, addrMode='absY', load=('A', 'mem'), compute='CMP', store='null')
isa.newInst('CMP', 0xC1, addrMode='indX', load=('A', 'mem'), compute='CMP', store='null')
isa.newInst('CMP', 0xD1, addrMode='indY', load=('A', 'mem'), compute='CMP', store='null')

isa.newInst('SBC', 0xE9, addrMode='immd', load=('A', 'mem'), compute='SBC', store='A')
isa.newInst('SBC', 0xE5, addrMode='zro',  load=('A', 'mem'), compute='SBC', store='A')
isa.newInst('SBC', 0xF5, addrMode='zroX', load=('A', 'mem'), compute='SBC', store='A')
isa.newInst('SBC', 0xED, addrMode='abs',  load=('A', 'mem'), compute='SBC', store='A')
isa.newInst('SBC', 0xFD, addrMode='absX', load=('A', 'mem'), compute='SBC', store='A')
isa.newInst('SBC', 0xF9, addrMode='absY', load=('A', 'mem'), compute='SBC', store='A')
isa.newInst('SBC', 0xE1, addrMode='indX', load=('A', 'mem'), compute='SBC', store='A')
isa.newInst('SBC', 0xF1, addrMode='indY', load=('A', 'mem'), compute='SBC', store='A')

isa.newInst('ASL', 0x0A, addrMode=None,   load='A',   compute='ASL', store='A')
isa.newInst('ASL', 0x06, addrMode='zro',  load='mem', compute='ASL', store='mem')
isa.newInst('ASL', 0x16, addrMode='zroX', load='mem', compute='ASL', store='mem')
isa.newInst('ASL', 0x0E, addrMode='abs',  load='mem', compute='ASL', store='mem')
isa.newInst('ASL', 0x1E, addrMode='absX', load='mem', compute='ASL', store='mem')

isa.newInst('ROL', 0x2A, addrMode=None,   load='A',   compute='ROL', store='A')
isa.newInst('ROL', 0x26, addrMode='zro',  load='mem', compute='ROL', store='mem')
isa.newInst('ROL', 0x36, addrMode='zroX', load='mem', compute='ROL', store='mem')
isa.newInst('ROL', 0x2E, addrMode='abs',  load='mem', compute='ROL', store='mem')
isa.newInst('ROL', 0x3E, addrMode='absX', load='mem', compute='ROL', store='mem')

isa.newInst('LSR', 0x4A, addrMode=None,   load='A',   compute='LSR', store='A')
isa.newInst('LSR', 0x46, addrMode='zro',  load='mem', compute='LSR', store='mem')
isa.newInst('LSR', 0x56, addrMode='zroX', load='mem', compute='LSR', store='mem')
isa.newInst('LSR', 0x4E, addrMode='abs',  load='mem', compute='LSR', store='mem')
isa.newInst('LSR', 0x5E, addrMode='absX', load='mem', compute='LSR', store='mem')

isa.newInst('ROR', 0x6A, addrMode=None,   load='A',   compute='ROR', store='A')
isa.newInst('ROR', 0x66, addrMode='zro',  load='mem', compute='ROR', store='mem')
isa.newInst('ROR', 0x76, addrMode='zroX', load='mem', compute='ROR', store='mem')
isa.newInst('ROR', 0x6E, addrMode='abs',  load='mem', compute='ROR', store='mem')
isa.newInst('ROR', 0x7E, addrMode='absX', load='mem', compute='ROR', store='mem')

isa.newInst('STX', 0x86, addrMode='zro',  load='X', store='mem')
isa.newInst('STX', 0x96, addrMode='zroY', load='X', store='mem')
isa.newInst('STX', 0x8E, addrMode='abs',  load='X', store='mem')

isa.newInst('LDX', 0xA2, addrMode='immd', load='mem', compute='ZN', store='X')
isa.newInst('LDX', 0xA6, addrMode='zro',  load='mem', compute='ZN', store='X')
isa.newInst('LDX', 0xB6, addrMode='zroX', load='mem', compute='ZN', store='X')
isa.newInst('LDX', 0xAE, addrMode='abs',  load='mem', compute='ZN', store='X')
isa.newInst('LDX', 0xBE, addrMode='absX', load='mem', compute='ZN', store='X')

isa.newInst('DEC', 0xC6, addrMode='zro',  load='mem', compute='DEC', store='mem')
isa.newInst('DEC', 0xD6, addrMode='zroX', load='mem', compute='DEC', store='mem')
isa.newInst('DEC', 0xCE, addrMode='abs',  load='mem', compute='DEC', store='mem')
isa.newInst('DEC', 0xDE, addrMode='absX', load='mem', compute='DEC', store='mem')

isa.newInst('INC', 0xE6, addrMode='zro',  load='mem', compute='INC', store='mem')
isa.newInst('INC', 0xF6, addrMode='zroX', load='mem', compute='INC', store='mem')
isa.newInst('INC', 0xEE, addrMode='abs',  load='mem', compute='INC', store='mem')
isa.newInst('INC', 0xFE, addrMode='absX', load='mem', compute='INC', store='mem')

ucode.build(uinstDoNextInstruction)
