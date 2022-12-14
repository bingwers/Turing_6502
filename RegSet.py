
import json

class RegSet:
    class Reg:
        def __init__(self, name, regSet, index, bits, gotoUinst, gotoUopSeq, default=0):
            self.name = name
            self.regSet = regSet
            self.bits = bits
            self.index = index
            self.gotoUinst = gotoUinst
            self.gotoUopSeq = gotoUopSeq
            self.default = default
        
        def defaultToBin(self):
            bits = ''
            for i in range(self.bits):
                bits = ('1' if (((self.default >> i) & 1) == 1) else '0') + bits
            
            return bits

    def __init__(self, tape, ucode, uopGotoBeginning, uopGoRight):
        self.tape = tape
        self.regs = []
        self.regsByName = {}

        self.ucode = ucode
        self.uopGotoBeginning = uopGotoBeginning
        self.uopGoRight = uopGoRight
    
    def addReg(self, name, bits, default=0):
        gotoUopSeq = [self.uopGotoBeginning] + [self.uopGoRight] * len(self.regs)
        gotoUinst = None #self.ucode.newUinst('goto_reg_' + name, gotoUopSeq)

        reg = RegSet.Reg(name, self, len(self.regs), bits, gotoUinst,
            gotoUopSeq, default)
        self.regs.append(reg)
        self.regsByName[name] = reg

        regTapeInit = '$'
        for reg in self.regs:
            regTapeInit += reg.defaultToBin() + '$'

        self.tape.setInitial(regTapeInit)

        return reg
    
    def genJsonDescription(self):
        obj = {
            'regs' : [],
            'initial_tape' : self.tape.initial
        }

        offset = 1
        for reg in self.regs:

            obj['regs'].append({
                'name' : reg.name,
                'bits' : reg.bits,
                'start' : offset
            })

            offset += reg.bits + 1
        
        return json.dumps(obj)
