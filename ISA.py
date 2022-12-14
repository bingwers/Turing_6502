
from UCode import UCode

class ISA:

    class Instruction:

        def __init__(self, isa, name, opcode, addrMode, load, compute, store):
            self.isa = isa
            self.name = name
            self.opcode = opcode
            self.addrMode = addrMode
            self.load = load
            self.compute = compute
            self.store = store

            self.uinsts = []
            if self.addrMode is not None:
                self.uinsts.append(self.isa.addrModes[self.addrMode])
            
            if self.load is not None:
                if isinstance(self.load, tuple):
                    self.uinsts.extend(self.isa.loads[i] for i in self.load)
                
                else:
                    self.uinsts.append(self.isa.loads[self.load])
            
            if self.compute is not None:
                self.uinsts.append(self.isa.computes[self.compute])
            
            if self.store is not None:
                self.uinsts.append(self.isa.stores[self.store])

            self.uinsts.append(self.isa.uinstNextInst)
            
            # TODO -- make instruction name better
            self.uinst = self.isa.ucode.newUinst('inst_' + hex(opcode), self.uinsts,
                UCode.numToBinStr(opcode, 8))


    def __init__(self, ucode, addrModes, loads, computes, stores, uinstNextInst):
        self.ucode = ucode
        self.addrModes = addrModes
        self.loads = loads
        self.computes = computes
        self.stores = stores
        self.uinstNextInst = uinstNextInst

        self.instsByOpcode = {}
    
    def newInst(self, name, opcode, addrMode=None, load=None, compute=None, store=None):

        if addrMode is not None:
            assert(addrMode in self.addrModes)
        
        if load is not None:
            if isinstance(load, str):
                load = (load,)
            
            for l in load:
                assert(l in self.loads)
        
        if compute is not None:
            assert(compute in self.computes)
        
        if store is not None:
            assert(store in self.stores)

        assert(isinstance(opcode, int) and opcode >= 0 and opcode < 256)
        assert(opcode not in self.instsByOpcode)
        
        self.instsByOpcode[opcode] = ISA.Instruction(self, name, opcode,
            addrMode, load, compute, store)