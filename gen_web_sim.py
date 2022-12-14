from description import tm, ucode, regSet, isa

tm.genJSCode('web_sim/tm_sim_step.js')
tm.genJSTransitionTable('web_sim/tm_transitions.js')
ucode.genJsonDescription(regSet, 'web_sim/ucode_description.js')

tm.genDescriptionTextFile('web_sim/description.txt')