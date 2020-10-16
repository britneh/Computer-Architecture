"""CPU functionality."""

LDI = 0b10000010
PRN = 0b01000111
HLT = 0b00000001
MUL = 0b10100010
ADD = 0b10100000
PUSH = 0b01000101
POP = 0b01000110
CALL = 0b01010000
RET = 0b00010001
CMP = 0b10100111
JEQ = 0b01010101
PRA = 0b01001000
JMP = 0b01010100
JNE = 0b01010110

import sys

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256 #8-bit addressing; 256 bytes of RAM
        self.reg = [0] * 8 #general purpose 8bit numeric registers
        self.pc = 0 #program counter; address of curretly executing instruction
        self.SP = 7
        self.FL = [0] * 8
        self.reg[self.SP] = 0xf4 #Initialize SP
        self.running = True
        # self.opcodes = {
        #     # 0b10000010: self.LDI,
        #     # 0b01000111: self.PRN,
        #     # 0b00000001: self.HLT,
        #     # 0b10100010: self.MUL,
        #     # # 0b10100011: self.DIV,
        #     # 0b10100000: self.ADD
        #     # 0b10100001: self.SUB
        # }
    def ram_read(self, MAR):
        """Reads and returns value in stored address"""
        return self.ram[MAR] #memory address register

    def ram_write(self, MDR, MAR):
        """Writes value to address"""
        self.ram[MAR] = MDR #memory data register

    def load(self, filename):
        """Load a program into memory."""

        address = 0

        # For now, we've just hardcoded a program:

        # program = [
        #     # From print8.ls8
        #     0b10000010, # LDI R0,8
        #     0b00000000,
        #     0b00001000,
        #     0b01000111, # PRN R0
        #     0b00000000,
        #     0b00000001, # HLT
        # ]

        # for instruction in program:
        #     self.ram[address] = instruction
        #     address += 1
        # if len(sys.argv) != 2:
        #     print("usage: python3 ls8.py examples/filename")
        #     sys.exit(1)

        try:
            address = 0

            with open(filename) as f:
                for line in f:
                    t = line.split('#')
                    n = t[0].strip()

                    if n == '':
                        continue

                    try:
                        n = int(n, 2)
                    except ValueError:
                        print(f"Invalid number '{n}'")
                        sys.exit(1)

                    self.ram[address] = n
                    address += 1

        except FileNotFoundError:
            print(f"File not found: {filename}")
            sys.exit(1)

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        #elif op == "SUB": etc
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    # def MUL(self):
    #     operand_1 = self.ram_read(self.pc + 1)
    #     operand_2 = self.ram_read(self.pc + 2)
    #     self.alu("MUL", operand_1, operand_2)

    # def ADD(self):
    #     operand_1 = self.ram_read(self.pc + 1)
    #     operand_2 = self.ram_read(self.pc + 2)
    #     self.alu("ADD", operand_1, operand_2)


    def run(self):
        """Run the CPU.
        It needs to read the memory address that's stored in register PC, 
        and store that result in IR, the Instruction Register.
        """
        self.running = True


        while self.running:

            ir = self.ram_read(self.pc) # Instruction Register, contains a copy of the currently executing instruction
            
            # self.trace()
            
            operand_1 = self.ram_read(self.pc + 1)
            operand_2 = self.ram_read(self.pc + 2)
            
            if ir == LDI: # LDI
                self.reg[operand_1] = operand_2
                self.pc += 3

            elif ir == PRN: # PRN
                print(self.reg[operand_1])
                self.pc += 2

            elif ir == HLT: # HLT
                self.running = False
                self.pc += 1
            
            elif ir == MUL: #MUL
                self.reg[self.ram_read(self.pc + 1)] = self.reg[self.ram_read(self.pc+1)]*self.reg[self.ram_read(self.pc+2)]
                self.pc += 3

            elif ir == PUSH: #Push
                #decrement stack pointer
                self.reg[self.SP] -= 1
                value = self.reg[operand_1] #value to push
                #self.ram_write(self.reg[self.SP], value) #copy value on to stack
                topstack = self.reg[self.SP]
                self.ram[topstack] = value
                self.pc += 2
            
            elif ir == POP: #Pop
                #get value from top of stack
                value = self.ram[self.reg[self.SP]]
                #store in a reg
                regnum = operand_1
                #set reg to value
                self.reg[regnum] = value
                #increment the SP 
                self.reg[self.SP] += 1
                self.pc += 2
            
            elif ir == CMP:
                # if self.pc == 33:
                # breakpoint()
                #00000LGE
                if self.reg[operand_1] > self.reg[operand_2]:
                    self.FL[5] = 1
                elif self.reg[operand_1] < self.reg[operand_2]:
                    self.FL[6] = 1
                else:
                    self.FL[7] = 1
                self.pc += 3
            
            elif ir == JEQ:
                #If equal flag is set (true), jump to the address stored in the given register
                if self.FL[7] == 1:
                    self.pc = self.reg[operand_1]
                else:
                    self.pc +=2


            elif ir ==  JMP:
                #Jump to the address stored in the given register
                self.pc = self.reg[operand_1]

            elif ir == JNE:
                #If E flag is clear, jump to the address stored in the given register.
                if self.FL[7] == 0:
                    self.pc = self.reg[operand_1]
                else:
                    self.pc += 2

            
#             elif instruction == CALL:
# 		        # Get address of the next instruction after the CALL
# 		        return_addr = self.pc + 2
# ​
# 		        # Push it on the stack
# 		        
# ​
# 		        # Get subroutine address from register
# 		        reg_num = self.ram[self.pc + 1]
# 		        subroutine_addr = register[reg_num]
# ​
# 		        # Jump to it
# 		        pc = subroutine_addr
# ​
# 	        elif instruction == RET:
# 		        # Get return addr from top of stack
# 		        return_addr = 
# ​
# 		        # Store it in the PC
# 		        self.pc = return_addr



            else: 
                print(f"Unknown instruction")
                sys.exit(1)
