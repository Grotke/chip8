
import binascii
import sys


class InstructionDecoder:
    valuedBytes = ["F000", "F00F", "F0FF"]
    instructionMap = {
        "0000": {"description":"Execute machine language subroutine at address 0x{address}", "values": ["address"]},
        "00E0": {"description": "Clear the screen", "values":[]},
        "00EE": {"description": "Return from a subroutine", "values":[]},
        "1000": {"description": "Jump to address 0x{address}", "values":["address"]},
        "2000": {"description": "Execute subroutine starting at address 0x{address}", "values":["address"]},
        "3000": {"description": "Skip the following instruction if the value of register V{X} equals {value}", "values": ["X", "value"]},
        "4000": {"description": "Skip the following instruction if the value of register V{X} is not equal to {value}", "values": ["X", "value"]},
        "5000": {"description": "Skip the following instruction if the value of register V{X} is equal to the value of register V{Y}", "values": ["X", "Y"]},
        "6000": {"description": "Store number {value} in register V{X}", "values": ["X", "value"]},
        "7000": {"description": "Add the value {value} to register V{X}", "values": ["X", "value"]},
        "8000": {"description": "Store the value of register V{Y} in register V{X}", "values": ["X", "Y"]},
        "8001": {"description": "Set V{X} to V{X} OR V{Y}", "values": ["X", "Y"]},
        "8002": {"description": "Set V{X} to V{X} AND V{Y}", "values": ["X", "Y"]},
        "8003": {"description": "Set V{X} to V{X} XOR V{Y}", "values": ["X", "Y"]},
        "8004": {"description": "Add the value of register V{Y} to register V{X}. Set VF to 01 if a carry occurs. Set VF to 00 if a carry does not occur", "values": ["X", "Y"]},
        "8005": {"description": "Subtract the value of register V{Y} from register V{X}. Set VF to 00 if a borrow occurs. Set VF to 01 if a borrow does not occur", "values": ["X", "Y"]},
        "8006": {"description": "Store the value of register V{Y} shifted right one bit in register V{X}. Set register VF to the least significant bit prior to the shift", "values": ["X", "Y"]},
        "8007": {"description": "Set register V{X} to the value of V{Y} minus V{X}. Set VF to 00 if a borrow occurs. Set VF to 01 if a borrow does not occur", "values": ["X", "Y"]},
        "800E": {"description": "Store the value of register V{Y} shifted left one bit in register V{X}. Set register VF to the most significant bit prior to the shift", "values": ["X", "Y"]},
        "9000": {"description": "Skip the following instruction if the value of register V{X} is not equal to the value of register V{Y}", "values": ["X", "Y"]},
        "A000": {"description": "Store memory address 0x{address} in register I", "values": ["address"]},
        "B000": {"description": "Jump to address 0x{address} + V0", "values": ["address"]},
        "C000": {"description": "Set V{X} to a random number with a mask of {value}", "values": ["X", "value"]},
        "D000": {"description": "Draw a sprite at position V{X}, V{Y} with {bytes} bytes of sprite data starting at the address stored in I. Set VF to 01 if any set pixels are changed to unset and 00 otherwise", "values":["X", "Y", "bytes"]},
        "E09E": {"description": "Skip the following instruction if the key corresponding to the hex value currently stored in register V{X} is pressed", "values": ["X"]},
        "E0A1": {"description": "Skip the following instruction if the key corresponding to the hex value currently stored in register V{X} is not pressed", "values": ["X"]},
        "F007": {"description": "Store the current value of the delay timer in register V{X}", "values": ["X"]},
        "F00A": {"description": "Wait for a keypress and store the result in register V{X}", "values": ["X"]},
        "F015": {"description": "Set the delay timer to the value of register V{X}", "values": ["X"]},
        "F018": {"description": "Set the sound timer to the value of register V{X}", "values": ["X"]},
        "F01E": {"description": "Add the value stored in register V{X} to register I", "values": ["X"]},
        "F029": {"description": "Set I to the memory address of the sprite data corresponding to the hexadecimal digit stored in register V{X}", "values": ["X"]},
        "F033": {"description": "Store the binary-coded decimal equivalent of the value stored in register V{X} at addresses I, I+1, and I+2", "values": ["X"]},
        "F055": {"description": "Store the values of registers V0 to V{X} inclusive in memory starting at address I. I is set to I + X + 1 after operation", "values": ["X"]},
        "F065": {"description": "Fill registers V0 to V{X} inclusive with the values stored in memory starting at address I. I is set to I + {X} + 1 after operation", "values": ["X"]}
    }

    def decode(self, block):
        strBytes = binascii.hexlify(block).upper()
        if strBytes in self.instructionMap:
            print("Result with no processing was ", strBytes)
            return self.instructionMap[strBytes]
        for mask in self.valuedBytes:
            intMask = int(mask, 16)
            intBytes = int(strBytes, 16)
            result = intMask & intBytes
            strResult = "{0:0{1}X}".format(result, 4)
            if strResult in self.instructionMap:
                print(strResult + ":"+ mask)
                params = self.getParams(strResult, block)
                formattedString = self.instructionMap[strResult]["description"].format_map(params)
                return formattedString
        print("Not mapped.", strBytes)
        return "Couldn't map"

    def getX(self, block):
        intBytes = int.from_bytes(block, byteorder='big')
        intMask = int.from_bytes(b'\x0F\x00', byteorder='big')
        x = (intBytes & intMask) >> 8
        return x

    def getY(self, block):
        intBytes = int.from_bytes(block, byteorder='big')
        intMask = int.from_bytes(b'\x00\xF0', byteorder='big')
        y = (intBytes & intMask) >> 4
        return y

    def getAddress(self, block):
        intBytes = int.from_bytes(block, byteorder='big')
        intMask = int.from_bytes(b'\x0F\xFF', byteorder='big')
        address = intBytes & intMask
        return binascii.hexlify(address.to_bytes(2, byteorder='big')).decode("ascii")

    def getValue(self, block):
        intBytes = int.from_bytes(block, byteorder='big')
        intMask = int.from_bytes(b'\x00\xFF', byteorder='big')
        value = intBytes & intMask
        return value

    def getBytes(self, block):
        intBytes = int.from_bytes(block, byteorder='big')
        intMask = int.from_bytes(b'\x00\x0F', byteorder='big')
        numBytes = intBytes & intMask
        return numBytes

    def getParams(self, instrKey, block):
        paramsToGet = self.instructionMap[instrKey]["values"]
        params = {}
        for param in paramsToGet:
            if param == "X":
                params["X"] = self.getX(block)
            elif param == "address":
                params["address"] = self.getAddress(block)
            elif param == "Y":
                params["Y"] = self.getY(block)
            elif param == "value":
                params["value"] = self.getValue(block)
            elif param == "bytes":
                params["bytes"] = self.getBytes(block)
            else:
                print("ERROR: Parameter {0} not mapped.".format(param))
        return params




files = ["roms/MAZE"]
if len(sys.argv) > 1:
    files = sys.argv[1:]


for file in files:
    print("Opened file ---- ", file)
    with open(file, "rb") as f:
        instruct = InstructionDecoder()
        block = f.read(2)
        while block:
            print(instruct.decode(block))

            #print("Decode", block.decode('utf-8'))
            #intByte = int.from_bytes(block, byteorder='big')
            #print(binascii.hexlify(block), intByte)
            block = f.read(2)


print("END OF FILE")
