# udis86 - test/testgen.py
# 
# Copyright (c) 2009 Vivek Thampi
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without modification, 
# are permitted provided that the following conditions are met:
# 
#     * Redistributions of source code must retain the above copyright notice, 
#       this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright notice, 
#       this list of conditions and the following disclaimer in the documentation 
#       and/or other materials provided with the distribution.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND 
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED 
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE 
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR 
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES 
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; 
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON 
# ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT 
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS 
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import os
import sys
import random

if ( len( os.getenv( 'UD_SCRIPT_DIR', "" ) ) ):
    scriptsPath = os.getenv( 'UD_SCRIPT_DIR' ) + "/scripts"
else:
    scriptsPath = '../scripts'
sys.path.append( scriptsPath );

import ud_optable
import ud_opcode
import testgen_opr

def bits2name(bits):
    bits2name_map = {
         8 : "byte",
        16 : "word",
        32 : "dword",
        64 : "qword",
    }
    return bits2name_map[bits]


class UdTestGenerator( ud_opcode.UdOpcodeTables ):

    OprTable = []

    ExcludeList = ( 'fcomp3', 'fcom2', 'fcomp5', 'fstp1', 'fstp8', 'fstp9',
                    'fxch4', 'fxch7', 'xchg', 'pop' )

    def __init__(self, mode):
        self.mode = mode
        pass

    def OprMem(self, size, cast=False):
        choices = []
        if self.mode < 64:
            choices = ["[bx+si+0x1234]",
                       "[bx+0x10]", 
                       "[bp+di+0x27]",
                       "[di+0x100]"]
        choices.extend(("[eax+ebx]", "[ebx+ecx*4]", 
                        "[ebp+0x10]"))
        if self.mode == 64:
            choices.extend(("[rax+rbx]", "[rbx+r8-0x10]"))
        addr = random.choice(choices)
        if cast:
            addr = "%s %s" % (bits2name(size), addr)
        return addr

    def Gpr(self, size):
        if size == 8:
            choices = ['al', 'cl']
            if self.mode == 64:
                choices.extend(['sil', 'r10b'])
        elif size == 16:
            choices = ['ax', 'bp', 'dx']
            if self.mode == 64:
                choices.extend(['r8w', 'r14w'])
        elif size == 32:
            choices = ['eax', 'ebp', 'edx']
            if self.mode == 64:
                choices.extend(['r10d', 'r12d'])
        elif size == 64:
            choices = ['rax', 'rsi', 'rsp']
            if self.mode == 64:
                choices.extend(['r9', 'r13'])
        return random.choice(choices)

    def Xmm(self):
        r = 16 if self.mode == 64 else 8
        return "xmm%d" % random.choice(range(r))

    def Mmx(self):
        return "mm%d" % random.choice(range(8))

    def Modrm_RM_GPR(self, size, cast=False):
        return random.choice([self.Gpr(size),
                              self.OprMem(size=size, cast=cast)])

    def Modrm_RM_XMM(self, size, cast=False):
        return random.choice([self.Xmm(),
                              self.OprMem(size=size, cast=cast)])
    
    def Opr_ST0(self):
        return "st0"

    def Opr_ST1(self):
        return "st1"

    def Opr_ST2(self):
        return "st2"

    def Opr_ST3(self):
        return "st3"

    def Opr_ST4(self):
        return "st4"

    def Opr_ST5(self):
        return "st5"

    def Opr_ST6(self):
        return "st6"

    def Opr_ST7(self):
        return "st7"

    def Opr_rAX(self):
        choices = ['ax', 'eax']
        if self.mode == 64:
            choices.append('rax')
        return random.choice(choices)

    def Opr_Gb(self):
        return self.Gpr(8)

    def Opr_Eb(self):
        return self.Modrm_RM_GPR(8)

    def Opr_Ew(self):
        return self.Modrm_RM_GPR(16)

    def Insn_Ev(self):
        choices = [self.Modrm_RM_GPR(16, cast=True),
                   self.Modrm_RM_GPR(32, cast=True)]
        if self.mode == 64:
            choices.append(self.Modrm_RM_GPR(64, cast=True))
        return [random.choice(choices)]

    def Opr_V(self):
        return self.Xmm()

    def Opr_W(self):
        return random.choice([self.Xmm(), self.OprMem(size=128)])

    def Opr_P(self):
        return self.Mmx()

    def Opr_Q(self, cast=False):
        return random.choice([self.Mmx(), self.OprMem(size=64, cast=cast)])

    def Insn_Eb(self):
        return [self.Modrm_RM_GPR(size=8, cast=True)]

    def Insn_Ew(self):
        return [self.Modrm_RM_GPR(size=16, cast=True)]

    def Insn_Ev_Gv(self):
        choices = [(self.Modrm_RM_GPR(16), self.Gpr(16)),
                   (self.Modrm_RM_GPR(32), self.Gpr(32))]
        if self.mode == 64:
            choices.append((self.Modrm_RM_GPR(64), self.Gpr(64)))
        return random.choice(choices)

    def Insn_Gv_Ev(self):
        x, y = self.Insn_Ev_Gv();
        return (y, x)

    def Insn_V_Q(self):
        return [self.Opr_V(), self.Opr_Q(cast=True)]

    def generate_yasm( self, mode, seed ):
        opr_combos = {}
        random.seed( seed )
        print "[bits %s]" % mode
        for insn in self.InsnTable:
            if insn[ 'mnemonic' ] in self.ExcludeList:
                continue
            if 'inv64' in insn[ 'prefixes' ] and mode == '64':
                continue
            if 'def64' in insn[ 'prefixes' ] and mode != '64':
                continue

            if len(insn['operands']) == 0:
                continue
                # print "\t%s" % insn['mnemonic']

            fusedName = '_'.join(insn['operands'])
            if fusedName not in opr_combos:
                opr_combos[fusedName] = { 'covered' : False, 'freq' : 0 }
            opr_combos[fusedName]['freq'] += 1

            fn = getattr(self, "Insn_" + fusedName , None)
            if fn is not None:
                operands = ", ".join(fn())
            else: 
                oprgens = [ getattr(self, "Opr_" + opr, None) 
                                for opr in insn['operands'] ]
                if None not in oprgens:
                    operands = ", ".join([ oprgen() for oprgen in oprgens ])
                else:
                    operands = None
            if operands is not None:
                print "\t%s %s" % (insn['mnemonic'], operands)
                opr_combos[fusedName]['covered'] = True

        # stats
        total = 0
        covered = 0
        for combo in sorted(opr_combos, key=lambda k: opr_combos[k]['freq']):
            total += 1
            covered += (1 if opr_combos[combo]['covered'] else 0)
            sys.stderr.write("==> %12s : %5d %s\n" % 
                                (combo, opr_combos[combo]['freq'], 
                                 "!covered" if not opr_combos[combo]['covered']
                                                else ''))
        sys.stderr.write("==> Coverage = %d / %d (%d%%)\n" % (covered, total, (100 * covered / total)))

def main():
    generator = UdTestGenerator(int(sys.argv[3]))
    optableXmlParser = ud_optable.UdOptableXmlParser()
    optableXmlParser.parse( sys.argv[ 1 ], generator.addInsnDef )

    generator.generate_yasm( sys.argv[ 3 ], int( sys.argv[ 2 ] ) )

if __name__ == '__main__':
    main()
