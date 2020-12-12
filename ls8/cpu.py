"""CPU functionality."""

import sys

HLT = 0b00000001
LDI = 0b10000010
PRN = 0b01000111
MUL = 0b10100010
PUSH = 0b01000101
POP = 0b01000110
CALL = 0b01010000
RET = 0b00010001
ADD = 0b10100000
CMP = 0b10100111
JMP = 0b01010100
JEQ = 0b01010101
JNE = 0b01010110

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.pc = 0
        # set the stack pointer
        self.reg[7] = 0xF4
        self.running = True
        self.fl = 0
        self.branchtable = {}
        self.branchtable[HLT] = self.HLT
        self.branchtable[LDI] = self.LDI
        self.branchtable[PRN] = self.PRN
        self.branchtable[PUSH] = self.PUSH
        self.branchtable[POP] = self.POP
        self.branchtable[CALL] = self.CALL
        self.branchtable[RET] = self.RET
        self.branchtable[JMP] = self.JMP
        self.branchtable[JEQ] = self.JEQ
        self.branchtable[JNE] = self.JNE


    def ram_read(self, address):
        return self.ram[address]

    def ram_write(self, value, address):
        self.ram[address] = value

    def load(self):
        """Load a program into memory."""
        try:
            if len(sys.argv) < 2:
                print(f'Error from {sys.argv[0]}: missing filename argument')
                sys.exit(1)
            
            ram_index = 0

            with open(sys.argv[1]) as f:
                for line in f:
                    split_line = line.split("#")[0]
                    stripped_split_line = split_line.strip()

                    if stripped_split_line != "":
                        command = int(stripped_split_line, 2)
                        
                        self.ram[ram_index] = command

                        ram_index += 1
        
        except FileNotFoundError:
            print(f'Error from {sys.argv[0]}: {sys.argv[1]} not found')


    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] = self.reg[reg_a] + self.reg[reg_b]
            self.pc += 2
        elif op == "MUL":
            self.reg[reg_a] = self.reg[reg_a] * self.reg[reg_b]
            self.pc += 2
        elif op == "CMP":
            if self.reg[reg_a] == self.reg[reg_b]:
                self.fl = 0b00000001
            elif self.reg[reg_a] > self.reg[reg_b]:
                self.fl = 0b00000010
            elif self.reg[reg_a] < self.reg[reg_b]:
                self.fl = 0b00000100
            self.pc += 2
        
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

    def HLT(self, extraA, extraB):
        self.running = False

    def LDI(self, operand_a, operand_b):
        register_address = operand_a
        value_to_save = operand_b
        self.reg[register_address] = value_to_save
        self.pc += 2

    def PRN(self, operand_a, extraB):
        register_address = operand_a
        value = self.reg[register_address]
        print(value)
        self.pc += 1

    def PUSH(self, operand_a, extraB):
        # decrement the SP
        self.reg[7] -= 1

        # copy value from given register into address pointed to by SP
        register_address = operand_a
        value = self.reg[register_address]

        # copy into SP address
        ## self.reg[7] is one value below
        SP = self.reg[7]
        self.ram[SP] = value

        self.pc += 1
    
    def POP(self, operand_a, extraB):
        # Copy the value from the address pointed to by `SP` to the given register.
        ## get the SP
        SP = self.reg[7]

        ## copy the value from memory at that SP address
        value = self.ram[SP]

        ## get the target register address
        register_address = operand_a

        ## Put the value in that register
        self.reg[register_address] = value

        # Increment `SP`
        self.reg[7] += 1

        self.pc += 1

    def CALL(self, operand_a, extraB):
    # Step 1: push the return address onto the stack
    ## find the address/index of the command AFTER call
        next_index = self.pc + 2
    ## push the address onto the stack

        ### decrement the SP
        self.reg[7] -= 1              
        
        ### put the next command address at the location in memory where the stack pointer points
        SP = self.reg[7]

        self.ram[SP] = next_index

     # Step 2: jump, set the PC to wherever the register says
        ## find the number of the register to look at
        register_address = operand_a

        ## get the address of our subroutine out of that register
        sub_address = self.reg[register_address]
        ## set the pc
        self.pc = sub_address

    def RET(self, extraA, extraB):
        # Pop the value from the top of the stack and store it in the `PC`.
        # ## Pop from top of stack
        ### get the value first
        SP = self.reg[7]
        return_address = self.ram[SP]

        ### then move the stack pointer back up
        self.reg[7] += 1

        ## Step 2, jump back, set the PC to this value
        self.pc = return_address

    def JMP(self, operand_a, extraB):
        register_address = operand_a

        sub_address = self.reg[register_address]

        self.pc = sub_address

    def JEQ(self, operand_a, extraB):
        if self.fl == 0b00000001:
            self.JMP(operand_a, extraB)
        else:
            self.pc += 2

    def JNE(self, operand_a, extraB):
        not_equal = (self.fl & 0b01) == 0
        if not_equal:
            self.JMP(operand_a, extraB)
        else:
            self.pc += 2

    def run(self):
        """Run the CPU."""
        while self.running:
            # print(self.pc)
            IR = self.ram[self.pc]
            operand_a = self.ram_read(self.pc + 1)
            operand_b = self.ram_read(self.pc + 2)
            is_alu_operation = ((IR >> 5) & 0b1) == 1
            sets_pc = ((IR >> 4) & 0b001) == 1

            if is_alu_operation:
                if IR == MUL:
                    self.alu("MUL", operand_a, operand_b)
                elif IR == ADD:
                    self.alu("ADD", operand_a, operand_b)
                elif IR == CMP:
                    self.alu("CMP", operand_a, operand_b)
            else:
                self.branchtable[IR](operand_a, operand_b)

            if not sets_pc:
                self.pc += 1
