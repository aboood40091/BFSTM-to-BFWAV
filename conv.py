import os, struct, sys

FWAV_head = bytearray.fromhex("46574156FEFF00400001010000000000000200007000000000000040000000C07001000000000100000000000000000000000000000000000000000000000000")
INFO_head = bytearray.fromhex("494E464F000000C0000000000000000000000000000000000000000000000000710000000000001471000000000000281F000000000000180300000000000028000000001F000000000000000300000000000042000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000")

if not sys.argv[1].endswith(".bfstm"):
    print("LOL FAIL")
    print("")
    print("Exiting in 5 seconds...")
    time.sleep(5)
    sys.exit(1)

with open(sys.argv[1], "rb") as inf:
    inb = inf.read()
    inf.close()

data_pos = struct.unpack(">I", inb[0x30:0x34])[0]
data_size = struct.unpack(">I", inb[0x34:0x38])[0]

FWAV_head[0x0C:0x10] = (0x100 + data_size).to_bytes(4, 'big')
FWAV_head[0x28:0x2C] = (data_size).to_bytes(4, 'big')

INFO_head[0x08:0x09] = inb[0x60:0x61]
INFO_head[0x09:0x0A] = inb[0x61:0x62]
INFO_head[0x1F:0x20] = inb[0x62:0x63]
INFO_head[0x14:0x18] = inb[0x6c:0x70]
INFO_head[0x0E:0x10] = (struct.unpack(">I", inb[0x64:0x68])[0]).to_bytes(2, 'big')
INFO_head[0x10:0x14] = inb[0x68:0x6C]

FSTM_interleave_block_size = struct.unpack(">I", inb[0x74:0x78])[0]
FSTM_interleave_smallblock_size = struct.unpack(">I", inb[0x84:0x88])[0]

FWAV_interleave_block_size = FSTM_interleave_block_size - ((FSTM_interleave_smallblock_size & 0xFF) // 2)
FWAV_interleave_block_size -= (((FSTM_interleave_smallblock_size & 0xFF) // 2) + (FSTM_interleave_smallblock_size & 0xFFFFFF00))
FWAV_interleave_block_size += FSTM_interleave_smallblock_size # This is dumb

INFO_head[0x48:0x4C] = (0x18 + FWAV_interleave_block_size).to_bytes(4, 'big')

INFO_head[0x58:0xB2] = inb[0xDC:0x136]

data = inb[data_pos:data_pos+data_size]

FWAV = FWAV_head + INFO_head + data

name = os.path.splitext(sys.argv[1])[0]

with open(name + ".bfwav", "wb") as output:
    output.write(FWAV)
    output.close()
