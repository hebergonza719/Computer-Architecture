"""CPU functionality."""

import sys

HLT = 0b00000001
LDI = 0b10000010
PRN = 0b01000111
MUL = 0b10100010
PUSH = 0b01000101
POP = 0b01000110

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.pc = 0
        # set the stack pointer
        self.reg[7] = 0xF3
        self.running = True
        self.branchtable = {}
        self.branchtable[HLT] = self.HLT
        self.branchtable[LDI] = self.LDI
        self.branchtable[PRN] = self.PRN
        self.branchtable[MUL] = self.MUL
        self.branchtable[PUSH] = self.PUSH
        self.branchtable[POP] = self.POP


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
            self.reg[reg_a] += self.reg[reg_b]
        #elif op == "SUB": etc
        elif op == "MUL":
            self.MUL(reg_a, reg_b)
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

    def MUL(self, operand_a, operand_b):
        self.reg[operand_a] = self.reg[operand_a] * self.reg[operand_b]
        self.pc += 2

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


    def run(self):
        """Run the CPU."""
        while self.running:
            IR = self.ram[self.pc]
            operand_a = self.ram_read(self.pc + 1)
            operand_b = self.ram_read(self.pc + 2)
            is_alu_operation = ((IR >> 5) & 0b1) == 1

            # if IR == HLT:
            #     # self.running = False
            #     self.HLT()

            # elif IR == LDI:
            #     # register_address = operand_a
            #     # value_to_save = operand_b

            #     # self.reg[register_address] = value_to_save

            #     # self.pc += 2
            #     self.LDI(operand_a, operand_b)

            # elif IR == PRN:
            #     # register_address = operand_a

            #     # value = self.reg[register_address]

            #     # print(value)

            #     # self.pc += 1
            #     self.PRN(operand_a)

            if is_alu_operation:
                if IR == MUL:
                    self.alu("MUL", operand_a, operand_b)
            else:
                self.branchtable[IR](operand_a, operand_b)

            self.pc += 1
