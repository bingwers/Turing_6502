from description import tm, ucode, regSet, isa, uinstDoNextInstruction

sim = tm.newSim()

n = 0
stopTape = ['$', *(c for c in ucode.uinstsByObj[uinstDoNextInstruction]), ' ']
while True:
    sim.display()

    print('Commands:')
    print('    u: execute one Uop')
    print('    i: execute one Uinst')
    print('    U: execute one Uinst + it\'s children calls')
    print('    I: execute one instruction fetch or ISA instruction')
    print('    p: execute whole program')
    print('    j <steps>: execute specified number of steps')
    print('    <other>: execute one step')
    print('    q: quit')
    print()

    i = input('Enter Command: ')

    if i == 'i':
        while sim.state.name.startswith('doUInst'):
            if not sim.step():
                break
        while not sim.state.name.startswith('doUInst'):
            if not sim.step():
                break

    elif i == 'I':
        sim.step()
        while (sim.state.name != 'doUInst_rewindStackHead' or
                sim.heads[2] != 0 or
                len(sim.tapes[2]) < len(stopTape) or
                sim.tapes[2][0:len(stopTape)] != stopTape
        ):
            if not sim.step():
                break

    elif i == 'U':
        loc = sim.heads[2]
        while sim.tapes[2][loc] != '$' and loc >= 0:
            loc -= 1

        if loc == 0:
            sim.step()
            while (sim.heads[2] != 0 or sim.tapes[2][0] != ' '):
                if not sim.step():
                    break

            while (sim.state.name != 'doUInst_rewindStackHead'):
                if not sim.step():
                    break

        else:
            sim.step()
            while sim.state.name != 'doUInst_rewindUcodeHead' or sim.heads[2] != loc:
                if not sim.step():
                    break
        
    elif i == 'u':
        sim.step()
        while sim.state.name != 'uop_root':
            if not sim.step():
                break
    
    elif i == 'p':
        while (sim.state.name != 'doUInst_rewindUcodeHead' or
            sim.heads[2] != 0 or sim.tapes[2][0] != ' '):
            if not sim.step():
                break

    elif i == 'q':
        break

    elif i[0] == 'j':
        try:
            steps = int(i[1:])
            for i in range(steps):
                if not sim.step():
                    break
        except ValueError:
            sim.step()

    else:
        sim.step()