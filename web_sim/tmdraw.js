
console.log(state_description);

var curr_tape_hover_box = null;
var tape_hover_boxes = [];
var hover_state = null;

const draw_mem_tape = () => {
    const canvas = document.getElementById('tapes_canvas');
    const ctx = canvas.getContext('2d');

    const canvas_width = canvas.width;
    const canvas_height = canvas.height
    const char_width = 20;

    ctx.font = '20px serif';

    const cvt_to_x = (ptr) => {
        return (ptr - mem_tape_head) * char_width + canvas_width / 2;
    };

    var start = (mem_tape_head - 1000);
    if (start < 0) {
        start = 0;
    }
    start &= 0xFFFF8;
    var end = (mem_tape_head + 1000);
    if (end > (2**19)) {
        end = (2**19);
    }
    end &= 0xFFFF8;

    ctx.fillStyle = '#B0B0B0';
    for (var i = start; i < end; i += 8) {
        const start_x = cvt_to_x(i);
        const end_x = cvt_to_x(i + 8);

        if (end_x < 0 || start_x > canvas_width) {
            continue;
        }

        tape_hover_boxes.push({
            type: 'mem',
            value: i >> 3,
            x1: start_x,
            y1: 60,
            x2: end_x,
            y2: 83
        });

        ctx.fillRect(start_x, 60, end_x - start_x, 23);
        ctx.strokeRect(start_x, 60, end_x - start_x, 23);
    }
    
    ctx.fillStyle = '#000000';
    ctx.fillText("Memory Tape (head position = " + mem_tape_head + "):", 10, 50);
    for (var i = start; i < end; i += 8) {
        const start_x = cvt_to_x(i);
        const end_x = cvt_to_x(i + 8);

        if (end_x < 0 || start_x > canvas_width) {
            continue;
        }

        for (var j = 0; j < 8; j++) {
            ctx.fillText(mem_tape[i + j], cvt_to_x(i+j) + 4, 80);
        }
    }

    ctx.moveTo(canvas_width / 2 + 10, 110);
    ctx.lineTo(canvas_width / 2 + 10, 88);
    ctx.stroke();
    ctx.moveTo(canvas_width / 2 + 10 + 8, 95);
    ctx.lineTo(canvas_width / 2 + 10, 88);
    ctx.stroke();
    ctx.moveTo(canvas_width / 2 + 10 - 8, 95);
    ctx.lineTo(canvas_width / 2 + 10, 88);
    ctx.stroke();
};

const draw_reg_tape = () => {
    const canvas = document.getElementById('tapes_canvas');
    const ctx = canvas.getContext('2d');

    const canvas_width = canvas.width;
    const canvas_height = canvas.height
    const char_width = 20;

    ctx.font = '20px serif';

    const cvt_to_x = (ptr) => {
        return (ptr - reg_tape_head) * char_width + canvas_width / 2;
    };

    ctx.fillStyle = '#A0FFA0';
    for (let reg of reg_description['regs']) {
        const x = cvt_to_x(reg.start);

        tape_hover_boxes.push({
            type: 'reg',
            value: reg.name,
            x1: x,
            y1: 130,
            x2: x + reg.bits * 20,
            y2: 153
        });

        ctx.fillRect(x, 130, reg.bits * 20, 23);
        ctx.strokeRect(x, 130, reg.bits * 20, 23);
    }

    ctx.fillStyle = '#000000';
    ctx.fillText("Reg Tape (head position = " + reg_tape_head + "):", 10, 120);
    for (var i = 0; i < reg_tape.length; i++) {
        const x = cvt_to_x(i);

        ctx.fillText(reg_tape[i], x + 4, 150);
    }

    ctx.moveTo(canvas_width / 2 + 10, 180);
    ctx.lineTo(canvas_width / 2 + 10, 158);
    ctx.stroke();
    ctx.moveTo(canvas_width / 2 + 10 + 8, 165);
    ctx.lineTo(canvas_width / 2 + 10, 158);
    ctx.stroke();
    ctx.moveTo(canvas_width / 2 + 10 - 8, 165);
    ctx.lineTo(canvas_width / 2 + 10, 158);
    ctx.stroke();
};

const draw_ustack_tape = () => {
    const canvas = document.getElementById('tapes_canvas');
    const ctx = canvas.getContext('2d');

    const canvas_width = canvas.width;
    const canvas_height = canvas.height
    const char_width = 20;

    ctx.font = '20px serif';

    const cvt_to_x = (ptr) => {
        return (ptr - stack_tape_head) * char_width + canvas_width / 2;
    };

    ctx.fillStyle = '#FFA0A0';
    var curr_uinst = '';
    var uinst_start = 1;
    for (var i = 1; i <= stack_tape.length; i++) {
        if (stack_tape[i] == '$' || stack_tape[i] == '_') {
            if (curr_uinst in ucode_description.uinstsByCode) {
                tape_hover_boxes.push({
                    type: 'uinst_code',
                    value: ucode_description.uinstsByCode[curr_uinst],
                    x1: cvt_to_x(uinst_start),
                    y1: 200,
                    x2: cvt_to_x(uinst_start) + curr_uinst.length * 20,
                    y2: 223
                });

                ctx.fillRect(cvt_to_x(uinst_start), 200, curr_uinst.length * 20, 23);
                ctx.strokeRect(cvt_to_x(uinst_start), 200, curr_uinst.length * 20, 23);
            }
            curr_uinst = '';
            uinst_start = i + 1;
        }
        else {
            curr_uinst = curr_uinst + stack_tape[i];
        }

        if (stack_tape[i] == '_') {
            break;
        }
    }

    ctx.fillStyle = '#000000';
    ctx.fillText("Stack Tape (head position = " + stack_tape_head + "):", 10, 190);
    for (var i = 0; i < stack_tape.length; i++) {
        const x = cvt_to_x(i);

        ctx.fillText(stack_tape[i], x + 4, 220);
    }

    ctx.moveTo(canvas_width / 2 + 10, 250);
    ctx.lineTo(canvas_width / 2 + 10, 228);
    ctx.stroke();
    ctx.moveTo(canvas_width / 2 + 10 + 8, 235);
    ctx.lineTo(canvas_width / 2 + 10, 228);
    ctx.stroke();
    ctx.moveTo(canvas_width / 2 + 10 - 8, 235);
    ctx.lineTo(canvas_width / 2 + 10, 228);
    ctx.stroke();
};

const draw_ucode_tape = () => {
    const canvas = document.getElementById('tapes_canvas');
    const ctx = canvas.getContext('2d');

    const canvas_width = canvas.width;
    const canvas_height = canvas.height
    const char_width = 20;

    ctx.font = '20px serif';

    const cvt_to_x = (ptr) => {
        return (ptr - ucode_tape_head) * char_width + canvas_width / 2;
    };

    const draw_segment = (segment) => {
        const start = segment.start;
        const end = segment.end;

        const start_x = cvt_to_x(start);
        const end_x = cvt_to_x(end);

        if (start_x > canvas_width || end_x < 0) {
            return;
        }

        const uinst = ucode_description.uinsts[segment.uinst];
        const code_length = uinst.code.length;

        ctx.fillStyle = '#FFFFA0';
        ctx.fillRect(start_x, 270, end_x - start_x, 33);
        ctx.strokeRect(start_x, 270, end_x - start_x, 33);

        tape_hover_boxes.push({
            type: 'uinst',
            value: segment.uinst,
            x1: start_x,
            y1: 270,
            x2: end_x,
            y2: 303
        });

        ctx.fillStyle = '#FFA0A0';
        ctx.fillRect(start_x, 280, code_length * 20, 23);
        ctx.strokeRect(start_x, 280, code_length * 20, 23);

        tape_hover_boxes.push({
            type: 'uinst_code',
            value: segment.uinst,
            x1: start_x,
            y1: 280,
            x2: start_x + code_length * 20,
            y2: 303
        });

        ctx.fillStyle = '#A0A0FF';
        var ucode_x = start_x + (code_length + 1) * 20;
        for (let uop_name of uinst.rawUops) {
            const uop = ucode_description.uops[uop_name];
            const width = uop.code.length * 20;

            tape_hover_boxes.push({
                type: 'uop_code',
                value: uop_name,
                x1: ucode_x,
                y1: 280,
                x2: ucode_x + width,
                y2: 303
            });

            ctx.fillRect(ucode_x, 280, width, 23);
            ctx.strokeRect(ucode_x, 280, width, 23);
            ucode_x += width;
        }
        

        ctx.fillStyle = '#000000';
        var x = start_x;
        var l = segment.chars.length;
        for (var i = 0; i < l; i++) {
            const c = segment.chars[i];

            ctx.fillText(c, x + 4, 300);

            x += 20;
        }
    };

    for (let seg of ucode_description.tapeSegments) {
        draw_segment(seg);
    }

    ctx.fillText("Ucode Tape (head position = " + ucode_tape_head + "):", 10, 260);

    ctx.moveTo(canvas_width / 2 + 10, 330);
    ctx.lineTo(canvas_width / 2 + 10, 308);
    ctx.stroke();
    ctx.moveTo(canvas_width / 2 + 10 + 8, 315);
    ctx.lineTo(canvas_width / 2 + 10, 308);
    ctx.stroke();
    ctx.moveTo(canvas_width / 2 + 10 - 8, 315);
    ctx.lineTo(canvas_width / 2 + 10, 308);
    ctx.stroke();
};

const draw_states = () => {
    const canvas = document.getElementById('states_canvas');
    const ctx = canvas.getContext('2d');
    const n_states = state_description.states.length;
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    const draw_transition = (x1, y1, x2, y2, draw_tail) => {
        if (y2 == 20) {
            ctx.beginPath();
            ctx.moveTo(x1, y1);
            ctx.bezierCurveTo(x1+30, y1+20, x1-20, 715, x1+10, 715);
            if (draw_tail) {
                ctx.lineTo(1110, 715);
                ctx.lineTo(1110, 10);
                ctx.lineTo(32, 10);
                ctx.lineTo(32, 20);
            }
            ctx.stroke();
        }
        else if (x1 == x2 && y1 == y2) {
            ctx.beginPath();
            ctx.moveTo(x1, y1);
            ctx.bezierCurveTo(x1+20, y1-14, x1+20, y1+14, x1, y1);
            ctx.stroke();
        }
        else if (x1 == x2 && y2 != y1 + 20 && (y2 != 280 || y1 >= y2)) {
            var dx = 1.8*Math.sqrt(Math.abs(y2-y1));
            if (y2 < y1) {
                dx = -dx;
            }

            ctx.beginPath();
            ctx.moveTo(x1, y1);
            ctx.bezierCurveTo(x1+dx,y1, x2+dx, y2, x2, y2);
            ctx.stroke();
        }
        else {
            ctx.beginPath();
            ctx.moveTo(x1, y1);
            ctx.lineTo(x2, y1);
            ctx.lineTo(x2, y2);
            ctx.stroke();
        }
    };
    
    ctx.fillStyle = '#000000';
    ctx.strokeStyle = '#000000';
    ctx.lineWidth = 0.5;

    ctx.beginPath();
    ctx.moveTo(42, 715)
    ctx.lineTo(1110, 715);
    ctx.lineTo(1110, 10);
    ctx.lineTo(32, 10);
    ctx.lineTo(32, 20);
    ctx.stroke();

    for (var i = 0; i < n_states; i++) {
        for (let j of state_description.conn[i]) {
            const x1 = state_description.pos[i][0];
            const y1 = state_description.pos[i][1];
            const x2 = state_description.pos[j][0];
            const y2 = state_description.pos[j][1];

            if (i == hover_state || (i == curr_state && j == next_state)) {
                if (i == hover_state) {
                    ctx.strokeStyle = '#0000FF';
                }
                else {
                    ctx.strokeStyle = '#FF0000';
                }
                ctx.lineWidth = 2;
                draw_transition(x1, y1, x2, y2, true);
                ctx.strokeStyle = '#000000';
                ctx.lineWidth = 0.5;
            }
            else {
                draw_transition(x1, y1, x2, y2, false);
            }
        }
    }

    ctx.fillStyle = '#C0C0C0';
    ctx.strokeStyle = '#000000';
    for (var i = 0; i < n_states; i++) {
        const coord = state_description.pos[i];

        if (i == hover_state) {
            ctx.strokeStyle = '#0000FF';
            ctx.lineWidth = 2;
            ctx.fillStyle = '#8080FF';
        }
        else if (i == curr_state) {
            ctx.strokeStyle = '#FF0000';
            ctx.lineWidth = 2;
            ctx.fillStyle = '#FF8080';
        }
        else if (i == next_state) {
            ctx.strokeStyle = '#FF8000';
            ctx.lineWidth = 2;
            ctx.fillStyle = '#FFE0C0';
        }

        ctx.beginPath();
        ctx.ellipse(coord[0], coord[1],
            6, 6, 0, 0, 2*Math.PI);
        ctx.fill();
        ctx.stroke();

        if (i == hover_state || i == curr_state || i == next_state) {
            ctx.fillStyle = '#C0C0C0';
            ctx.strokeStyle = '#000000';
            ctx.lineWidth = 1;
        }
    }
};

const get_hover_state = (x,y) => {
    const n_states = state_description.states.length;
    for (var i = 0; i < n_states; i++) {
        const coord = state_description.pos[i];

        if (Math.hypot(x - coord[0], y - coord[1]) <= 6) {
            return i;
        }
    }

    return null;
};

const draw_tapes = () => {
    const canvas = document.getElementById('tapes_canvas');
    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    tape_hover_boxes = [];
    ctx.fillStyle = '#000000';
    ctx.lineWidth = 1;
    draw_mem_tape();
    draw_reg_tape();
    draw_ustack_tape();
    draw_ucode_tape();
};

const draw_hover_info = () => {
    const div = document.getElementById('hover_info');

    if (curr_tape_hover_box !== null) {
        if (curr_tape_hover_box.type == 'mem') {
            div.innerText = "Memory[" + curr_tape_hover_box.value
                            + "] = " + get_mem_byte(curr_tape_hover_box.value);
        }
        else if (curr_tape_hover_box.type == 'reg') {
            div.innerText = "Register " + curr_tape_hover_box.value + " = " +
                            curr_regs[curr_tape_hover_box.value];
        }
        else if (curr_tape_hover_box.type == 'uinst') {
            div.innerText = "Uinst " + curr_tape_hover_box.value;
        }
        else if (curr_tape_hover_box.type == 'uinst_code') {
            div.innerText = "Uinst Code " + curr_tape_hover_box.value;
        }
        else if (curr_tape_hover_box.type == 'uop_code') {
            div.innerText = "Uop Code " + curr_tape_hover_box.value;
        }
    }
    else if (hover_state !== null) {
        div.innerText = "State " + state_description.states[hover_state];
    }
    else {
        div.innerText = '';
    }
}

draw_tapes();
draw_states();

const states_canvas = document.getElementById('states_canvas');
const tapes_canvas = document.getElementById('tapes_canvas');

states_canvas.addEventListener("mousemove", e => {
    const x = e.clientX - states_canvas.getBoundingClientRect().x;
    const y = e.clientY - states_canvas.getBoundingClientRect().y;
    
    const old_hover_state = hover_state;
    hover_state = get_hover_state(x,y);

    if (old_hover_state != hover_state) {
        draw_states();
        draw_hover_info();
    }
});

tapes_canvas.addEventListener("mousemove", e => {
    const x = e.clientX - tapes_canvas.getBoundingClientRect().x;
    const y = e.clientY - tapes_canvas.getBoundingClientRect().y;

    const old_tape_hover_box = curr_tape_hover_box;
    curr_tape_hover_box = null;
    for (var i = tape_hover_boxes.length-1; i >= 0; i--) {
        const box = tape_hover_boxes[i];
        if (x >= box.x1 && x <= box.x2 && y >= box.y1 && y <= box.y2) {
            curr_tape_hover_box = box;
            break;
        }
    }

    if ((old_tape_hover_box === null && curr_tape_hover_box !== null) ||
        (old_tape_hover_box !== null && curr_tape_hover_box === null) ||
        (old_tape_hover_box !== null && curr_tape_hover_box !== null && (
        (old_tape_hover_box.x1 != curr_tape_hover_box.x1) ||
        (old_tape_hover_box.x2 != curr_tape_hover_box.x2) ||
        (old_tape_hover_box.y1 != curr_tape_hover_box.y1) ||
        (old_tape_hover_box.y2 != curr_tape_hover_box.y2) ||
        (old_tape_hover_box.type != curr_tape_hover_box.type) ||
        (old_tape_hover_box.value != curr_tape_hover_box.value)))
    ) {
        draw_tapes();
        const ctx = tapes_canvas.getContext('2d');

        if (curr_tape_hover_box !== null) {
            ctx.lineWidth = 4;
            ctx.strokeStyle = '#000000';
            ctx.strokeRect(curr_tape_hover_box.x1, curr_tape_hover_box.y1,
                curr_tape_hover_box.x2 - curr_tape_hover_box.x1,
                curr_tape_hover_box.y2 - curr_tape_hover_box.y1);
        }
        draw_hover_info();
    }
})

const insert_machine_info = () => {
    var div = document.getElementById('machine_info');

    div.innerHTML = "Num Steps: " + num_steps + "<br>" +
                    "State: " + state_description.states[curr_state] + "<br>" +
                    "Uop: " + curr_uop + "<br>" +
                    "Uinst: " + curr_uinst + "<br>" +
                    "Inst: " + curr_inst + "<br>" +
                    "MAR: " + curr_regs["MAR"] + "<br>" +
                    "PC: " + curr_regs["PC"] + "<br>" +
                    "A: " + curr_regs["A"] + "<br>" +
                    "X: " + curr_regs["X"] + "<br>" +
                    "Y: " + curr_regs["Y"] + "<br>" +
                    "SP: " + curr_regs["SP"] + "<br>" +
                    "N: " + curr_regs["N"] + "<br>" +
                    "V: " + curr_regs["V"] + "<br>" +
                    "Z: " + curr_regs["Z"] + "<br>" +
                    "C: " + curr_regs["C"] + "<br>";
}

const draw_mem_info = () => {
    var text = "";
    for (var i = 0; i < 256; i++) {
        if (i % 8 == 0) {
            text += ('0000' + i.toString(16)).substr(-4) + ': ';
        }

        if (i == curr_regs['PC']) {
            text += "<span style=\"background-color: #FF8080;\">";
        }

        text += ('00' + get_mem_byte(i).toString(16)).substr(-2);
        
        if (i == curr_regs['PC']) {
            text += "</span>";
        }

        text += ' ';
        
        if ((i + 1) % 8 == 0 && i != 255) {
            text += "<br>";
        }
    }

    document.getElementById('mem_info').innerHTML = text;
}

const ui_step = () => {
    sim_step();
    sim_calc_next_state();
    sim_determine_regs();
    draw_tapes();
    draw_states();
    insert_machine_info();
    draw_hover_info();
    draw_mem_info();
}

const ui_step_uop = () => {
    while ((sim_step() & 3) == 0) {}
    sim_calc_next_state();
    sim_determine_regs();
    draw_tapes();
    draw_states();
    insert_machine_info();
    draw_hover_info();
    draw_mem_info();
}

const ui_step_uinst = () => {
    while ((sim_step() & 5) == 0) {}
    sim_calc_next_state();
    sim_determine_regs();
    draw_tapes();
    draw_states();
    insert_machine_info();
    draw_hover_info();
    draw_mem_info();
}

const ui_step_jump = () => {
    for (var i = 0; i < 1000000; i++) {
        if ((sim_step() & 1) != 0) {
            break;
        }
    }
    sim_calc_next_state();
    sim_determine_regs();
    draw_tapes();
    draw_states();
    insert_machine_info();
    draw_hover_info();
    draw_mem_info();
}

const ui_step_inst = () => {
    while ((sim_step() & 9) == 0) {}
    sim_calc_next_state();
    sim_determine_regs();
    draw_tapes();
    draw_states();
    insert_machine_info();
    draw_hover_info();
    draw_mem_info();
}

document.addEventListener('keydown', e => {
    if (e.key == 'Enter') {
        ui_step();
    }
    else if (e.key == 'u') {
        ui_step_uop();
    }
    else if (e.key == 'i') {
        ui_step_uinst();
    }
    else if (e.key == 'j') {
        ui_step_jump();
    }
    else if (e.key == 'I') {
        ui_step_inst();
    }
});

const setProgram = () => {
    const prog = document.getElementById('program_select').value;
    if (prog == 'sum') {
        sim_init([
            0xE0, 10,           // loop:    CPX 10
            0xF0, 8,            //          BEQ end
            0xE8,               //          INX
            0x86, 0xFF,         //          STX $0xFF
            0x65, 0xFF,         //          ADC $0xFF
            0x4C, 0x00, 0x00,   //          JMP loop
            0x00                // end:     <illegal instruction>
        ]);
    }
    else {
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
    }
    sim_calc_next_state();
    sim_determine_regs();
    draw_tapes();
    draw_states();
    insert_machine_info();
    draw_hover_info();
    draw_mem_info();
};

window.addEventListener('resize', e => {
    document.getElementById('tapes_canvas').width = window.innerWidth;
    draw_tapes();
});

document.getElementById('program_select').addEventListener('change', e => {
    setProgram();
});

setProgram();