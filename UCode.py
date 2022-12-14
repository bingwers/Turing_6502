
import json

class UCode:

    @staticmethod
    def numToBinStr(num, len):
        s = ''
        for i in range(len):
            if ((num>>i) & 1) == 1:
                s = '1' + s
            else:
                s = '0' + s
        
        return s

    class Uop:
        class State:
            def __init__(self, uop, name):
                self.uop = uop
                self.name = name
                self.tmState = self.uop.ucode.tm.addState(uop.name + '_' + name)

            def trans(self, nextState, condition, *actions):
                self.tmState.trans(nextState.tmState, condition, actions)

            def default(self, nextState, *actions):
                self.tmState.trans(nextState.tmState, 'else', actions)

            def ret(self, condition, *actions):
                self.tmState.trans(self.uop.ucode.rootState, condition, actions)

        def __init__(self, ucode, name):
            self.ucode = ucode
            self.name = name
            self.states = set()
            self.startState = None
            self.startActions = None

            assert(name not in self.ucode.uops)
            self.ucode.uops[name] = self

        def start(self, name, *actions):
            state = self.addState(name, start=True)
            self.startActions = actions

            return state

        def addState(self, name, start=False):
            state = UCode.Uop.State(self, name)
            self.states.add(state)
            if start:
                assert(self.startState is None)
                self.startState = state

            return state
        
        def __repr__(self):
            return f"Uop({self.name})"

    class UInst:
        def __init__(self, name, ucode, ops, code=None):
            self.ucode = ucode
            self.name = name
            self.uops = []
            self.cond_one = []
            self.cond_zero = []
            self.uinsts = []

            assert(name not in self.ucode.uinsts)
            self.ucode.uinsts[name] = self

            if code is not None:
                assert (code not in self.ucode.uinstsByCode)
                self.ucode.uinstsByCode[code] = self
                self.ucode.uinstsByObj[self] = code           

            i = 0
            while i < len(ops) and isinstance(ops[i], UCode.Uop):
                self.uops.append(ops[i])
                i += 1

            if i < len(ops) and isinstance(ops[i], tuple):
                assert(len(ops[i]) == 2)

                if isinstance(ops[i][0], UCode.UInst):
                    self.cond_one.append(ops[i][0])
                else:
                    assert(isinstance(ops[i][0], list))
                    for op in ops[i][0]:
                        assert(isinstance(op, UCode.UInst))
                        self.cond_one.append(op)

                if isinstance(ops[i][1], UCode.UInst):
                    self.cond_zero.append(ops[i][1])
                else:
                    assert(isinstance(ops[i][1], list))
                    for op in ops[i][1]:
                        assert(isinstance(op, UCode.UInst))
                        self.cond_zero.append(op)

                i += 1
            
            while i < len(ops) and isinstance(ops[i], UCode.UInst):
                self.uinsts.append(ops[i])
                i += 1
            
            assert(i == len(ops))
        
        def __repr__(self):
            return f"UInst({self.name})"

    def build(self, initialUinstStack):
        uinstFreq = {}
        for uinst in self.uinsts.values():
            uinstFreq[uinst] = 0

        for uinst in self.uinsts.values():
            for sub_uinst in uinst.cond_one:
                uinstFreq[sub_uinst] += 1
            for sub_uinst in uinst.cond_zero:
                uinstFreq[sub_uinst] += 1
            for sub_uinst in uinst.uinsts:
                uinstFreq[sub_uinst] += 1

        uinst_assign_order = list(self.uinsts.values())
        uinst_assign_order.sort(key=(lambda u: uinstFreq[u]))
        uinst_assign_order.reverse()

        nextAssignUcode = 0
        nextAssignUcodeLen = 1

        def getNextUinstCode():
            nonlocal nextAssignUcode
            nonlocal nextAssignUcodeLen

            while True:
                if nextAssignUcode >= (2 ** nextAssignUcodeLen):
                    nextAssignUcode = 0
                    nextAssignUcodeLen += 1
                    continue
                
                code = UCode.numToBinStr(nextAssignUcode, nextAssignUcodeLen)
                nextAssignUcode += 1

                if code not in self.uinstsByCode:
                    return code

        for uinst in uinst_assign_order:
            if uinst in self.uinstsByObj:
                continue

            code = getNextUinstCode()
            self.uinstsByObj[uinst] = code
            self.uinstsByCode[code] = uinst

        uinstUopSeqs = {}

        for uinst in uinst_assign_order:
            uop_seq = []
            for uop in uinst.uops:
                uop_seq.append(uop)
            
            for sub_uinst in reversed(uinst.uinsts):
                uop_seq.append(self.stackAppendUops['$'])
                for i in self.uinstsByObj[sub_uinst]:
                    if i == '0':
                        uop_seq.append(self.stackAppendUops['0'])
                    elif i == '1':
                        uop_seq.append(self.stackAppendUops['1'])
                    else:
                        assert(False)

            for sub_uinst in reversed(uinst.cond_one):
                uop_seq.append(self.stackConditionalAppendUops['$'])
                for i in self.uinstsByObj[sub_uinst]:
                    if i == '0':
                        uop_seq.append(self.stackConditionalAppendUops['0'])
                    elif i == '1':
                        uop_seq.append(self.stackConditionalAppendUops['1'])
                    else:
                        assert(False)

            for sub_uinst in reversed(uinst.cond_zero):
                uop_seq.append(self.stackInvConditionalAppendUops['$'])
                for i in self.uinstsByObj[sub_uinst]:
                    if i == '0':
                        uop_seq.append(self.stackInvConditionalAppendUops['0'])
                    elif i == '1':
                        uop_seq.append(self.stackInvConditionalAppendUops['1'])
                    else:
                        assert(False)
            
            uinstUopSeqs[uinst] = uop_seq

        uopFreq = {}
        for uop in self.uops.values():
            uopFreq[uop] = 0
        
        for uop_seq in uinstUopSeqs.values():
            for uop in uop_seq:
                uopFreq[uop] += 1

        uopPriorityQueue = [(uopFreq[u], u) for u in self.uops.values()]
        uopPriorityQueue.sort(key=(lambda x:x[0]))
        
        while len(uopPriorityQueue) > 1:
            first = uopPriorityQueue.pop(0)
            second = uopPriorityQueue.pop(0)

            freq = first[0] + second[0]
            newNode = (freq, (first[1], second[1]))

            i = 0
            while i < len(uopPriorityQueue) and uopPriorityQueue[i][0] < freq:
                i += 1
            
            uopPriorityQueue.insert(i, newNode)
        
        uopsByObj = {}
        uopsByPath = {}

        def buildTransitions(node, state, path):
            left,right = node

            if isinstance(left, UCode.Uop):
                state.trans(left.startState.tmState, self.ucodeTape['0'],
                    (self.ucodeTape.right,) + left.startActions)
                uopsByObj[left] = path + '0'
                uopsByPath[path + '0'] = left
            else:
                newPath = path + '0'
                newState = self.tm.addState('uop_decode_' + newPath)
                state.trans(newState, self.ucodeTape['0'], [self.ucodeTape.right])
                buildTransitions(left, newState, newPath)

            if isinstance(right, UCode.Uop):
                state.trans(right.startState.tmState, self.ucodeTape['1'],
                    (self.ucodeTape.right,) + right.startActions)
                uopsByObj[right] = path + '1'
                uopsByPath[path + '1'] = right
            else:
                newPath = path + '1'
                newState = self.tm.addState('uop_decode_' + newPath)
                state.trans(newState, self.ucodeTape['1'], [self.ucodeTape.right])
                buildTransitions(right, newState, newPath)

        self.rootState.trans(self.uopDoUinst.startState.tmState, self.ucodeTape['$'],
            self.uopDoUinst.startActions)
        buildTransitions(uopPriorityQueue[0][1], self.rootState, '')
    
        ucodeTapeInit = ' '
        for uinst in uinst_assign_order:
            ucodeTapeInit += self.uinstsByObj[uinst] + '$'

            for uop in uinstUopSeqs[uinst]:
                ucodeTapeInit += uopsByObj[uop]

            ucodeTapeInit += '$'

        self.ucodeTape.setInitial(ucodeTapeInit)        
        self.ustackTape.setInitial('$' + self.uinstsByObj[initialUinstStack])
        self.tm.setInitialState(self.uopDoUinst.startState.tmState)

        self.uinstUopSeqs = uinstUopSeqs
        self.uinstOrder = uinst_assign_order
        self.uopsByObj = uopsByObj
        self.uopByPath = uopsByPath

    def __init__(self, tm, regTape, ustackTape, ucodeTape):
        self.tm = tm
        self.ustackTape = ustackTape
        self.ucodeTape = ucodeTape
        self.uops = {}
        self.uinsts = {}
        self.uinstsByCode = {}
        self.uinstsByObj = {}

        self.rootState = self.tm.addState('uop_root')

        # builtin uops
        @self.newUopDecorator('stackAppend0')
        def uopStackAppend0(uop):
            state = uop.start('state')
            state.ret(True, ustackTape.write('0'), ustackTape.right)

        @self.newUopDecorator('stackAppend1')
        def uopStackAppend1(uop):
            state = uop.start('state')
            state.ret(True, ustackTape.write('1'), ustackTape.right)

        @self.newUopDecorator('stackAppendDollar')
        def uopStackAppendDollar(uop):
            state = uop.start('state')
            state.ret(True, ustackTape.write('$'), ustackTape.right)

        @self.newUopDecorator('stackConditionalAppend0')
        def uopStackConditionalAppend0(uop):
            state = uop.start('state', regTape.left)
            state.ret(regTape['1'], ustackTape.write('0'), regTape.right, ustackTape.right)
            state.ret(regTape['0'], regTape.right)

        @self.newUopDecorator('stackConditionalAppend1')
        def uopStackConditionalAppend1(uop):
            state = uop.start('state', regTape.left)
            state.ret(regTape['1'], ustackTape.write('1'), regTape.right, ustackTape.right)
            state.ret(regTape['0'], regTape.right)

        @self.newUopDecorator('stackConditionalAppendDollar')
        def uopStackConditionalAppendDollar(uop):
            state = uop.start('state', regTape.left)
            state.ret(regTape['1'], ustackTape.write('$'), regTape.right, ustackTape.right)
            state.ret(regTape['0'], regTape.right)

        @self.newUopDecorator('stackInvConditionalAppend0')
        def uopStackInvConditionalAppend0(uop):
            state = uop.start('state', regTape.left)
            state.ret(regTape['0'], ustackTape.write('0'), regTape.right, ustackTape.right)
            state.ret(regTape['1'], regTape.right)

        @self.newUopDecorator('stackInvConditionalAppend1')
        def uopStackInvConditionalAppend1(uop):
            state = uop.start('state', regTape.left)
            state.ret(regTape['0'], ustackTape.write('1'), regTape.right, ustackTape.right)
            state.ret(regTape['1'], regTape.right)

        @self.newUopDecorator('stackInvConditionalAppendDollar')
        def uopStackInvConditionalAppendDollar(uop):
            state = uop.start('state', regTape.left)
            state.ret(regTape['0'], ustackTape.write('$'), regTape.right, ustackTape.right)
            state.ret(regTape['1'], regTape.right)

        # sentinel blank at front of ucode tape
        # $ separates ucode entries
        @self.newUopDecorator('doUInst')
        def uopDoUinst(uop):
            rewindUcodeHead = uop.start('rewindUcodeHead', ucodeTape.left)
            rewindStackHead = uop.addState('rewindStackHead')
            compareInst = uop.addState('compareInst')
            findNextInst0 = uop.addState('findNextInst0')
            findNextInst1 = uop.addState('findNextInst1')
            popStack = uop.addState('popStack')
            illegalInst = uop.addState('illegalInst')

            rewindUcodeHead.trans(rewindStackHead, ucodeTape[' '], ucodeTape.right)
            rewindUcodeHead.default(rewindUcodeHead, ucodeTape.left)

            rewindStackHead.trans(compareInst, ustackTape['$'], ustackTape.right)
            rewindStackHead.default(rewindStackHead, ustackTape.left)

            compareInst.trans(popStack, ucodeTape['$'] & ustackTape[' '],
                ustackTape.left, ucodeTape.right)
            compareInst.trans(compareInst,
                (ucodeTape['0'] & ustackTape['0']) | (ucodeTape['1'] & ustackTape['1']),
                ustackTape.right, ucodeTape.right)
            compareInst.trans(findNextInst0, ustackTape[' '] & -ucodeTape['$'],
                ustackTape.left, ucodeTape.right)
            compareInst.trans(findNextInst1, -ustackTape[' '] & ucodeTape['$'],
                ustackTape.left, ucodeTape.right)
            compareInst.trans(illegalInst, ucodeTape[' '] & -ustackTape[' '])
            compareInst.default(findNextInst0, ustackTape.left, ucodeTape.right)

            findNextInst0.trans(findNextInst1, ucodeTape['$'], ucodeTape.right)
            findNextInst0.trans(illegalInst, ucodeTape[' '])
            findNextInst0.default(findNextInst0, ucodeTape.right)

            findNextInst1.trans(rewindStackHead, ucodeTape['$'], ucodeTape.right)
            findNextInst1.trans(illegalInst, ucodeTape[' '])
            findNextInst1.default(findNextInst1, ucodeTape.right)

            popStack.ret(ustackTape['$'], ustackTape.write(' '))
            popStack.default(popStack, ustackTape.write(' '), ustackTape.left)

        self.stackAppendUops = {
            '0' : uopStackAppend0,
            '1' : uopStackAppend1,
            '$' : uopStackAppendDollar,
        }

        self.stackConditionalAppendUops = {
            '0' : uopStackConditionalAppend0,
            '1' : uopStackConditionalAppend1,
            '$' : uopStackConditionalAppendDollar,
        }

        self.stackInvConditionalAppendUops = {
            '0' : uopStackInvConditionalAppend0,
            '1' : uopStackInvConditionalAppend1,
            '$' : uopStackInvConditionalAppendDollar,
        }

        self.uopDoUinst = uopDoUinst

    def newUopDecorator(self, name):
        def handler(func):
            uop = UCode.Uop(self, name)
            func(uop)
            return uop
        return handler
    
    def newUinst(self, name, ops, code=None):
        return UCode.UInst(name, self, ops, code)

    def genCCode(self, outputFile):
        lines = []

        lines.append(f"#define NUM_UINSTS ({len(self.uinsts)})")

        uinsts = list(self.uinstsByObj.keys())
        lines.append('')
        lines.append('const char * uinst_names[] = {')
        for uinst in uinsts:
            lines.append(f'    "{uinst.name}",')
        lines.append('};')

        lines.append('')
        lines.append('const char * uinst_codes[] = {')
        for uinst in uinsts:
            lines.append(f'    "{self.uinstsByObj[uinst]}",')
        lines.append('};')

        with open(outputFile, 'w') as fp:
            fp.write("\n".join(lines))

    def genJsonDescription(self, regSet, outputFile):
        text = '\nconst reg_description = JSON.parse(`\n'
        text += regSet.genJsonDescription()
        text += '\n`);\n\nconst state_description = JSON.parse(`\n'
        text += self.genStateGraph()
        text += '\n`);\n\nconst ucode_description = JSON.parse(`\n'
        text += self.genMainDescription()
        text += '\n`);\n\n'
        text += 'const ucode_tape = \n`'
        text += ''.join(self.ucodeTape.initial).replace(' ', '_')
        text += '_`;\n'

        with open(outputFile, 'w') as fp:
            fp.write(text)

    def genMainDescription(self):
        
        obj = {
            'uops' : {},
            'uopsByCode' : {},
            'uinsts' : {},
            'uinstsByCode' : {},
            'tapeSegments' : [],
            'initial_stack' : self.ustackTape.initial
        }

        for uop, code in self.uopsByObj.items():
            obj['uops'][uop.name] = {
                'code' : code
            }

            obj['uopsByCode'][code] = uop.name

        tapeOffset = 1
        for uinst in self.uinstOrder:
            obj['uinsts'][uinst.name] = {
                'code' : self.uinstsByObj[uinst],
                'rawUops' : [i.name for i in self.uinstUopSeqs[uinst]],
                'uops' : [i.name for i in uinst.uops],
                'cond_one' : [i.name for i in uinst.cond_one],
                'cond_zero' : [i.name for i in uinst.cond_zero],
                'uinsts' : [i.name for i in uinst.uinsts]
            }
            obj['uinstsByCode'][self.uinstsByObj[uinst]] = uinst.name

            segmentChars = self.uinstsByObj[uinst] + '$' + "".join(
                self.uopsByObj[u] for u in self.uinstUopSeqs[uinst]) + '$'
            
            obj['tapeSegments'].append({
                'start' : tapeOffset,
                'end' : tapeOffset + len(segmentChars),
                'chars' : segmentChars,
                'uinst' : uinst.name,
            })
            
            tapeOffset += len(segmentChars)
        
        return json.dumps(obj)

    def genStateGraph(self):

        SPACING = 20

        states = [i for i in self.tm.states]

        connections = []
        for state in states:
            conn = []
            for nextState, _, _ in state.transitions:
                conn.append(states.index(nextState))
            
            connections.append(conn)

        decode_states = [s for s in self.tm.states if s.name.startswith('uop_decode')]

        pos = {}
        def set_pos(state, x, y):
            pos[states.index(state)] = ((x+1) * 32, (y+1) * 20)

        codes = list(self.uopByPath.keys())
        codes.sort()
        uops = [self.uopByPath[code] for code in codes]
        max_len = max(len(i) for i in codes)
        
        for x, uop in enumerate(uops):
            y = max_len

            unAddedStates = set(s.tmState for s in uop.states)
            returnStates = []
            stateOrder = []

            for s in unAddedStates:
                for nextState, _, _ in s.transitions:
                    if nextState.name == 'uop_root':
                        returnStates.append(s)
                        break
            
            for s in returnStates:
                unAddedStates.remove(s)

            currState = uop.startState.tmState
            stateOrder.append(currState)
            if currState in returnStates:
                returnStates.remove(currState)
            else:
                unAddedStates.remove(currState)

            while len(unAddedStates) > 0:
                for s, _, _ in currState.transitions:
                    if s in unAddedStates:
                        currState = s
                        unAddedStates.remove(s)
                        break
                else:
                    currState = unAddedStates.pop()
                
                stateOrder.append(currState)

            stateOrder.extend(returnStates)
            
            for s in stateOrder:
                set_pos(s,x,y)
                y += 1
        
        for s in decode_states:
            code = s.name[len('uop_decode_'):]
            y = len(code)

            while code not in codes:
                code = code + '0'
            
            x = codes.index(code)
            set_pos(s,x,y)
        
        for s in states:
            if s.name == 'uop_root':
                set_pos(s, 0, 0)
        
        return json.dumps({
            'states' : [s.name for s in states],
            'conn' : connections,
            'pos' : pos
        })
        


