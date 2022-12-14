var mem_tape_head = 0;
var mem_tape = [];

var reg_tape_head = 0;
var reg_tape = [];

var stack_tape_head = 0;
var stack_tape = [];

var ucode_tape_head = 0;

var curr_state = 0;
var next_state = 38;

var curr_uop;
var curr_uinst;
var curr_stack;
var curr_inst;
var curr_regs = {};
var num_steps = 0;

const set_mem_byte = (addr, val) => {
    for (var i = 0; i < 8; i++) {
        mem_tape[8*addr + i] = ((val >> (7-i)) & 1) ? '1' : '0';
    }
};

const get_mem_byte = (addr) => {
    var val = 0;
    for (var i = 0; i < 8; i++) {
        val <<= 1;
        if (mem_tape[8*addr + i] == '1') {
            val |= 1;
        }
    }

    return val;
}

const sim_init = (program) => {
    curr_state = TM_STATE_doUInst_rewindUcodeHead;

    mem_tape_head = 0;
    mem_tape = [];
    num_steps = 0;
    for (var i = 0; i < (2**19); i++) {
        mem_tape.push('0');
    }

    reg_tape_head = 0;
    reg_tape = [];
    for (let c of reg_description.initial_tape) {reg_tape.push(c);}
    for (var i = 0; i < 1000; i++) {reg_tape.push('_');}

    state_tape_head = 0;
    stack_tape = [];
    for (let c of ucode_description.initial_stack) {stack_tape.push(c);}
    for (var i = 0; i < 1000; i++) {stack_tape.push('_');}

    ucode_tape_head = 0;
    curr_uop = 'doUInst';
    curr_uinst = 'doNextInstruction';
    curr_stack = [];

    for (var i = 0; i < program.length; i++) {
        set_mem_byte(i, program[i]);
    }

    sim_determine_regs();
    var inst = get_mem_byte(curr_regs['PC']);
    curr_inst = '0x' + ('00' + inst.toString(16)).substr(-2);
    get_mem_byte();
};

const determine_stack = () => {
    curr_stack = [];

    var code = '';
    var i = 0;
    while (stack_tape[i] != '_') {
        i += 1;
        if (stack_tape[i] == '$' || stack_tape[i] == '_') {
            if (ucode_description.uinstsByCode[code] !== undefined) {
                curr_stack.push(ucode_description.uinstsByCode[code]);
            }
            code = '';
        }
        else {
            code += stack_tape[i];
        }
    }
};

const sim_determine_regs = () => {
    for (let reg of reg_description.regs) {
        var val = 0;
        for (var i = 0; i < reg.bits; i++) {
            if (reg_tape[reg.start + i] == '0') {
                val <<= 1;
            }
            else if (reg_tape[reg.start + i] == '1') {
                val <<= 1; val += 1;
            }
            else {
                val = '??';
                break;
            }
        }

        curr_regs[reg.name] = val;
    }
}

const sim_step = () => {
    var ret_val = tm_step();

    if (ret_val == 0) {
        num_steps++;
    }

    if (curr_state == TM_STATE_uop_root) {
        if (ucode_tape[ucode_tape_head] == '$') {
            curr_uop = 'doUInst'
        }
        else {
            curr_uop = '??'
            var code = ''
            for (var i = 0; i < 20; i++) {
                code += ucode_tape[ucode_tape_head + i];
                if (ucode_description.uopsByCode[code] !== undefined) {
                    curr_uop = ucode_description.uopsByCode[code];
                    break;
                }
            }
        }

        ret_val |= 2;
    }

    else if (ucode_tape_head == 0) {
        determine_stack();
        curr_uinst = curr_stack.pop();
        ret_val |= 4;

        if (curr_uinst == 'doNextInstruction') {
            sim_determine_regs();
            var inst = get_mem_byte(curr_regs['PC']);
            curr_inst = '0x' + ('00' + inst.toString(16)).substr(-2);
            get_mem_byte();

            ret_val |= 8;
        }
    }

    return ret_val;
};

const sim_calc_next_state = () => {
    const tape_reads = mem_tape[mem_tape_head] + reg_tape[reg_tape_head] +
                stack_tape[stack_tape_head] + ucode_tape[ucode_tape_head];
    
    const transition = tm_transitions[curr_state][tape_reads];
    if (transition === undefined) {
        next_state = -1;
    }
    else {
        next_state = transition[0];
    }
};



/*sim_init([
    0xE0, 10,           // loop:    CPX 10
    0xF0, 8,            //          BEQ end
    0xE8,               //          INX
    0x86, 0xFF,         //          STX $0xFF
    0x65, 0xFF,         //          ADC $0xFF
    0x4C, 0x00, 0x00,   //          JMP loop
    0x00                // end:     <illegal instruction>
]);*/

sim_init([
    0xA9, 0,            // LDA 0
    0xA2, 0,            // LDX 0
    0x95, 100,          // clear:   STA $100,X
    0xE8,               //          INX
    0xE0, 100,          //          CPX 100
    0x30, 0xF9,         //          BMI clear
    0xA9, 2,            // LDA 2
    0x85, 99,           // STA $99
    0x18,               // mark:    CLC
    0x65, 99,           //          ADC $99
    0xAA,               //          inner:  TAX
    0x95, 100,          //                  STA $100, X
    0x65, 99,           //                  ADC $99
    0xE0, 100,          //                  CPX 100
    0x30, 0xF7,         //                  BMI inner
    0xE6, 99,           //          INC $99
    0xA5, 99,           //          LDA $99
    0xC9, 11,           //          CMP 11
    0x30, 0xEC,         //          BMI mark
    0xA0, 0,            // LDY 0
    0xA2, 2,            // LDX 2
    0xB5, 100,          // count:   LDA $100, X
    0xD0, 1,            //          BNE skip
    0xC8,               //          INY
    0xE8,               //   skip:  INX
    0xE0, 100,          //          CPX 100
    0x30, 0xF6,         //          BMI count
    0x98,               // TYA
    0x00                // <illegal instruction>
]);

/*
0000: A9 00 A2 00 95 64 E8 E0  ;········
0008: 64 30 F9 A9 02 85 63 18  ;········
0010: 65 63 AA 95 64 65 63 E0  ;········
0018: 64 30 F7 E6 63 A5 63 C9  ;········
0020: 0B 30 EC A0 00 A2 02 B5  ;········
0028: 64 D0 01 C8 E8 E0 64 30  ;········
0030: F6 98 00 00 00 00 00 00  ;········
*/



sim_calc_next_state();