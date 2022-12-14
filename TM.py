
import os
import json

class TM:
    class Tape:
        class TransitionCondition:
            def __init__(self, tapesym=None, not_=None, and_=None, or_=None):
                if tapesym is not None:
                    self.type = 'tapesym'
                    self.value = tapesym
                elif not_ is not None:
                    self.type = 'not'
                    self.value = not_
                elif and_ is not None:
                    self.type = 'and'
                    self.value = and_
                elif or_ is not None:
                    self.type = 'or'
                    self.value = or_
                else:
                    assert(False)

            def __and__(self, rhs):
                assert(isinstance(rhs, TM.Tape.TransitionCondition))
                return TM.Tape.TransitionCondition(and_=(self, rhs))
            
            def __or__(self, rhs):
                assert(isinstance(rhs, TM.Tape.TransitionCondition))
                return TM.Tape.TransitionCondition(or_=(self, rhs))

            def __neg__(self):
                return TM.Tape.TransitionCondition(not_=self)

            def as_c_condition(self):
                if self.type == 'tapesym':
                    tape, sym = self.value
                    return f"(state->{tape.name}_tape[state->{tape.name}_head]==\'{sym}\')"
                if self.type == 'not':
                    return f"(!{self.value.as_c_condition()})"
                if self.type == 'and':
                    return f"({self.value[0].as_c_condition()}&&{self.value[1].as_c_condition()})"
                if self.type == 'or':
                    return f"({self.value[0].as_c_condition()}||{self.value[1].as_c_condition()})"

            def as_js_condition(self):
                if self.type == 'tapesym':
                    tape, sym = self.value
                    if sym == ' ':
                        sym = '_'
                    return f"({tape.name}_tape[{tape.name}_tape_head]==\'{sym}\')"
                if self.type == 'not':
                    return f"(!{self.value.as_js_condition()})"
                if self.type == 'and':
                    return f"({self.value[0].as_js_condition()}&&{self.value[1].as_js_condition()})"
                if self.type == 'or':
                    return f"({self.value[0].as_js_condition()}||{self.value[1].as_js_condition()})"

            def as_description(self):
                if self.type == 'tapesym':
                    tape, sym = self.value
                    return f"{tape.name}[{sym}]"
                elif self.type == 'not':
                    return f"(NOT {self.value.as_description()})"
                elif self.type == 'and':
                    return f"(AND {self.value[0].as_description()} {self.value[1].as_description()})"
                elif self.type == 'or':
                    return f"(OR {self.value[0].as_description()} {self.value[1].as_description()})"
                else:
                    assert(False)

            def evaluate(self, inputs):
                if self.type == 'tapesym':
                    return inputs[self.value[0].tmIndex] == self.value[1]
                elif self.type == 'not':
                    return not self.value.evaluate(inputs)
                elif self.type == 'and':
                    return self.value[0].evaluate(inputs) and self.value[1].evaluate(inputs)
                elif self.type == 'or':
                    return self.value[0].evaluate(inputs) or self.value[1].evaluate(inputs)
                else:
                    assert(False)

        class TransitionAction:
            def __init__(self, tape, writeSym=None, headMove=None):
                self.tape = tape
                
                if writeSym is not None:
                    self.type = 'write'
                    self.writeSym = writeSym
                elif headMove is not None:
                    self.type = 'move'
                    self.headMove = headMove
                else:
                    assert(False)
            
            def as_description(self):
                if self.type == 'write':
                    return f'{self.tape.name}[{self.writeSym}]'
                elif self.type == 'move':
                    if self.headMove == 'L':
                        return f'{self.tape.name}.left'
                    if self.headMove == 'R':
                        return f'{self.tape.name}.right'

        def __init__(self, tm, tmIndex, name, alph, blank=' ', readOnly=False, size=-1):
            self.tm = tm
            self.tmIndex = tmIndex
            self.name = name
            self.alph = alph
            self.blank = blank
            self.readOnly = readOnly
            self.size = size

            self.left = TM.Tape.TransitionAction(self, headMove='L')
            self.right = TM.Tape.TransitionAction(self, headMove='R')
            self.initial = [blank]

        def __getitem__(self, rhs):
            sym = rhs
            assert(sym in self.alph)
            return TM.Tape.TransitionCondition(tapesym=(self, sym))

        def write(self, rhs):
            sym = rhs
            assert(sym in self.alph)
            return TM.Tape.TransitionAction(self, writeSym=sym)

        def setInitial(self, initial):
            if isinstance(initial, str):
                initial = [i for i in initial]
            
            assert(isinstance(initial, list))
            for i in initial:
                assert(i in self.alph)
            
            self.initial = initial

        def setInitialByte(self, addr, val):
            assert('0' in self.alph and '1' in self.alph)

            while len(self.initial) < (8 * (addr + 1)):
                self.initial.append(self.blank)

            for i in range(8):
                if ((val >> i) & 1) != 0:
                    self.initial[8*addr + 7 - i] = '1'
                else:
                    self.initial[8*addr + 7 - i] = '0'

    class State:
        def __init__(self, tm, name):
            self.tm = tm
            self.name = name
            self.transitions = []

        def trans(self, nextState, condition, actions):
            self.tm.addTransition(self, nextState, condition, actions)
            self.transitions.append((nextState, condition, actions))

        def __repr__(self):
            return self.name

    class Simulation:
        def __init__(self, tm):
            self.tm = tm

            assert(tm.initialState is not None)
            self.state = tm.initialState

            self.n_steps = 0
            self.heads = []
            self.tapes = []
            self.blank = []
            for tape in tm.orderedTapes:
                self.heads.append(0)
                self.tapes.append([i for i in tape.initial])
                self.blank.append(tape.blank)

        def step(self):
            heads = tuple([self.tapes[i][h] for i, h in enumerate(self.heads)])

            if heads not in self.tm.transitions[self.state]:
                return False

            next_state, new_heads, moves = self.tm.transitions[self.state][heads]
            self.state = next_state

            for i, h in enumerate(new_heads):
                self.tapes[i][self.heads[i]] = h

                move = moves[i]
                if move == 'R':
                    self.heads[i] += 1
                    if self.heads[i] == len(self.tapes[i]):
                        self.tapes[i].append(self.blank[i])
                elif move == 'L':
                    if self.heads[i] > 0:
                        self.heads[i] -= 1

            self.n_steps += 1
            return True

        def display(self):
            width = os.get_terminal_size().columns
            hwidth = (width - 9) // 2

            print("\033[2J\033[H",end='')

            heads = tuple([self.tapes[i][h] for i, h in enumerate(self.heads)])
            if heads in self.tm.transitions[self.state]:
                next_state, new_heads, moves = self.tm.transitions[self.state][heads]
                next_state = next_state.name
                new_heads = ' '.join('\'' + h + '\'' for h in new_heads)
                moves = ' '.join(' ' + h + ' ' for h in moves)
            else:
                next_state, new_heads, moves = '-', '-', '-'
            
            heads = ' '.join('\'' + h + '\'' for h in heads)

            print("STEPS    " + str(self.n_steps))
            print()
            print("STATE:   " + self.state.name)
            print("READ:    " + heads)
            print()
            print("NEXT_ST: " + next_state)
            print("WRITE:   " + new_heads)
            print("MOVE:    " + moves)
            print()

            for i, h in enumerate(self.heads):
                print("TAPE", self.tm.orderedTapes[i].name, f"({h})")
                tapeh = self.tapes[i][h]
                if tapeh == ' ':
                    tapeh = '_'

                if h < hwidth:
                    tapel = ''.join(self.tapes[i][:h]).replace(' ', '_').rjust(hwidth, ' ')
                else:
                    tapel = ''.join(self.tapes[i][h-hwidth:h]).replace(' ', '_')
                
                if len(self.tapes[i]) - h - 1 < hwidth:
                    taper = ''.join(self.tapes[i][h+1:]).ljust(hwidth, self.blank[i]).replace(' ', '_')
                else:
                    taper = ''.join(self.tapes[i][h+1:h + 1 + hwidth]).replace(' ', '_')
                
                print('    ', tapel, tapeh, taper, sep='')
                print(' ' * (hwidth + 4) + '^')

    def __init__(self):
        self.tapes = set()
        self.orderedTapes = []
        self.states = set()
        self.initialState = None

        self.possibleInputs = [()]

        self.transitions = {}   # state -> (symbol for each tape) -> (state, dir for each tape)
        self.c_transitions = {}

    def addTape(self, name, alph, blank=' ', readOnly=False, size=-1):
        tape = TM.Tape(self, len(self.tapes), name, alph, blank, readOnly, size)
        self.tapes.add(tape)
        self.orderedTapes.append(tape)

        newPis = []
        for pi in self.possibleInputs:
            for sym in alph:
                newPi = pi + (sym,)
                newPis.append(newPi)
        
        self.possibleInputs = newPis

        return tape
    
    def addState(self, name):
        state = TM.State(self, name)
        self.states.add(state)

        self.transitions[state] = {}
        self.c_transitions[state] = []

        return state

    def addTransition(self, state, nextState, condition, actions):

        self.c_transitions[state].append((nextState, condition, actions))

        stateTransitions = self.transitions[state]
        for pi in self.possibleInputs:
            if condition == True:
                satisfied = True
            elif condition == 'else':
                satisfied = pi not in stateTransitions
            else:
                satisfied = condition.evaluate(pi)

            if satisfied:
                assert(pi not in stateTransitions)

                writeVals = [i for i in pi]
                moveDirs = ['S' for _ in pi]

                for action in actions:
                    if action.type == 'write':
                        writeVals[action.tape.tmIndex] = action.writeSym
                    elif action.type == 'move':
                        moveDirs[action.tape.tmIndex] = action.headMove
                    else:
                        assert(False)
                
                writeVals = tuple(writeVals)
                moveDirs = tuple(moveDirs)

                stateTransitions[pi] = (nextState, writeVals, moveDirs)
    
    def setInitialState(self, state):
        self.initialState = state

    def newSim(self):
        return TM.Simulation(self)

    def genCCode(self, outputFile):
        lines = []

        lines.append('#include "stdlib.h"')
        lines.append('#include "string.h"')
        lines.append('#include "stdio.h"')
        lines.append('')

        for i, state in enumerate(self.states):
            lines.append(f'#define TM_STATE_{state.name} ({i})')

        lines.append('')
        for tape in self.orderedTapes:
            initialSize = len(tape.initial)
            size = max(tape.size, initialSize)
            lines.append(f'#define TAPE_SIZE_{tape.name} ({size})')

        lines.append('')
        lines.append('const char * tm_state_names[] = {')
        for state in self.states:
            lines.append(f'    "{state.name}",')
        lines.append('};')

        lines.append('')
        lines.append('typedef struct TM_State TM_State;')
        lines.append('struct TM_State {')
        lines.append('    int state;')
        for tape in self.orderedTapes:
            lines.append(f'    int {tape.name}_head;')
            lines.append(f'    unsigned char * {tape.name}_tape;')
        lines.append('};')

        lines.append('')
        for tape in self.orderedTapes:
            lines.append(f'const unsigned char {tape.name}_tape_init[] =')
            i = 0
            init_tape = ''
            while i < len(tape.initial):
                if len(init_tape) == 72:
                    lines.append('    \"' + init_tape + '\"')
                    init_tape = ''
                init_tape += tape.initial[i]
                i += 1

            lines.append('    \"' + init_tape + '\";')

        lines.append('')
        lines.append('TM_State * tm_init() {')
        lines.append(f'    TM_State * state = malloc(sizeof(TM_State));')
        lines.append(f'    state -> state = TM_STATE_{self.initialState.name};')
        for tape in self.orderedTapes:
            lines.append(f'    state -> {tape.name}_head = 0;')
            initialSize = len(tape.initial)
            size = max(tape.size, initialSize)
            lines.append(f'    state -> {tape.name}_tape = malloc(sizeof(unsigned char) * {size});')
            lines.append(f'    memcpy(state -> {tape.name}_tape, {tape.name}_tape_init, {initialSize});')
            lines.append(f'    memset(state -> {tape.name}_tape + {initialSize}, \'{tape.blank}\', {size - initialSize});')

        lines.append('    return state;')
        lines.append('}')

        lines.append('')
        lines.append('int tm_step(TM_State * state) {')
        lines.append('    switch (state -> state) {')
        for state in self.states:
            lines.append(f'        case TM_STATE_{state.name}:')
            for nextState, condition, actions in self.c_transitions[state]:
                if condition == True:
                    lines.append('            if (1) {')
                elif condition == 'else':
                    lines.append('            else {')
                else:
                    lines.append(f'            if {condition.as_c_condition()} {{')
                
                for action in actions:
                    tape = action.tape
                    if action.type == 'write':
                        sym = action.writeSym
                        lines.append(' '*16 +
                            f"state->{tape.name}_tape[state->{tape.name}_head]=\'{sym}\';")
                    elif action.type == 'move':
                        if action.headMove == 'L':
                            lines.append(f'                if (state->{tape.name}_head>0) {{')
                            lines.append(' '* 20 + f"state->{tape.name}_head--;")
                            lines.append('                }')
                        elif action.headMove == 'R':
                            lines.append(' '* 16 + f"state->{tape.name}_head++;")
                
                lines.append(f'                state->state=TM_STATE_{nextState.name};')
                lines.append('                return 0;')
                lines.append('            }')
            
            lines.append('            return 1;')
        lines.append('    }')
        lines.append('}')

        with open(outputFile, 'w') as fp:
            fp.write("\n".join(lines))

    def genJSCode(self, outputFile):
        lines = []

        for state in self.states:
            lines.append(f'const TM_STATE_{state.name} = state_description.states.indexOf(\'{state.name}\');')

        lines.append('')
        lines.append('const tm_step = () => {')
        lines.append('    switch (curr_state) {')
        for _state_idx, state in enumerate(self.states):
            lines.append(f'        case TM_STATE_{state.name}:')
            for nextState, condition, actions in self.c_transitions[state]:
                if condition == True:
                    lines.append('            if (1) {')
                elif condition == 'else':
                    lines.append('            else {')
                else:
                    lines.append(f'            if {condition.as_js_condition()} {{')
                
                for action in actions:
                    tape = action.tape
                    if action.type == 'write':
                        sym = action.writeSym
                        if sym == ' ':
                            sym = '_'
                        lines.append(' '*16 +
                            f"{tape.name}_tape[{tape.name}_tape_head]=\'{sym}\';")
                    elif action.type == 'move':
                        if action.headMove == 'L':
                            lines.append(f'                if ({tape.name}_tape_head>0) {{')
                            lines.append(' '* 20 + f"{tape.name}_tape_head--;")
                            lines.append('                }')
                        elif action.headMove == 'R':
                            lines.append(' '* 16 + f"{tape.name}_tape_head++;")
                
                lines.append(f'                curr_state=TM_STATE_{nextState.name};')
                lines.append('                return 0;')
                lines.append('            }')
            
            lines.append('            return 1;')
        lines.append('    }')
        lines.append('}')

        with open(outputFile, 'w') as fp:
            fp.write("\n".join(lines))

    def genJSTransitionTable(self, outputFile):
        lines = ['var tm_transitions = {};']


        for state, deltas in self.transitions.items():
            lines.append(f'tm_transitions[TM_STATE_{state.name}] = {{}};')

            for reads, effects in deltas.items():
                nextState, writes, actions = effects

                reads = ''.join(reads)
                nextState = 'TM_STATE_' + nextState.name
                writes = ''.join(writes)
                actions = ''.join(actions)

                reads = reads.replace(' ', '_')
                writes = writes.replace(' ', '_')

                lines.append(f'tm_transitions[TM_STATE_{state.name}][\'{reads}\'] = [{nextState}, \'{writes}\', \'{actions}\'];')
        lines.append('')

        with open(outputFile, 'w') as fp:
            fp.write('\n'.join(lines))
    
    def genDescriptionTextFile(self, outputFile):
        state_name_len = 0

        text = ''
        curr_line = 'Q = {'
        for state in self.states:
            curr_line += state.name + ", "
            if len(curr_line) > 150:
                text += curr_line + "\n"
                curr_line = '    '
            
            state_name_len = max(len(state.name), state_name_len)
        if len(curr_line) > 4:
            text += curr_line
        
        text = text[:-2]
        text += '\n}\n\n'

        for tape in self.orderedTapes:
            alph = ",".join(tape.alph).replace(' ', '_').replace(',', ', ')
            text += "Σ_" + tape.name + " = {" + alph + "}\n"

        text += '\n'
        for tape in self.orderedTapes:
            alph = ",".join(tape.alph).replace(' ', '_').replace(',', ', ')
            text += "Γ_" + tape.name + " = {" + alph + "}\n"
            
        text += '\nq0 = ' + self.initialState.name + '\n'

        text += '\nq_accept = {'
        for state in self.states:
            if len(self.transitions[state]) == 0:
                text += state.name
        text += '}\n\nq_reject = {}\n\n'

        text += ' ' * 40 + " TRANSITION FUNCTION " + ' ' * 40 + '\n\n'
        text += 'Current State'.ljust(state_name_len) + ' '
        text += 'Read'.ljust(2*len(self.tapes)) + '-> '
        text += 'Next State'.ljust(state_name_len) + ' '
        text += 'Write'.ljust(2*len(self.tapes))
        text += 'Move'.ljust(2*len(self.tapes)) + '\n'

        tape_abbrev = ' '.join([t.name[0].upper() for t in self.orderedTapes])
        text += ' ' * state_name_len + ' ' + tape_abbrev
        text += ' ' * (state_name_len + 4) + ' ' + tape_abbrev + ' ' + tape_abbrev
        text += '\n'

        text += '-' * (2 * state_name_len + 6 * len(self.tapes) + 4) + '\n'

        for state, transition in self.transitions.items():
            for read, actions in transition.items():
                next_state, write, move = actions

                read = ' '.join(''.join(read).replace(' ', '_'))
                write = ' '.join(''.join(write).replace(' ', '_'))
                move = ' '.join(''.join(move).replace(' ', '_'))

                s = state.name.ljust(state_name_len)
                n = next_state.name.ljust(state_name_len)

                text += (s + ' ' + read + ' -> ' + n + ' ' + write + ' ' + move + '\n')

        with open(outputFile, 'w') as fp:
            fp.write(text)




