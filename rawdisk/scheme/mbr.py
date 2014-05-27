import rawdisk.filesystems
from rawdisk.util.rawstruct import RawStruct


MBR_SIGNATURE = 0xAA55
MBR_SIG_SIZE = 2
MBR_SIG_OFFSET = 0x1FE
MBR_SIZE = 512
PT_ENTRY_SIZE = 16
PT_TABLE_OFFSET = 0x1BE
PT_TABLE_SIZE = PT_ENTRY_SIZE * 4
SECTOR_SIZE = 512


class PartitionEntry(RawStruct):
    def __init__(self, data):
        RawStruct.__init__(self, data)
        self.boot_indicator = self.get_ubyte(0)
        self.starting_head = self.get_ubyte(1)
        tmp = self.get_ubyte(2)
        self.starting_sector = tmp & 0x3F   # Only bits 0-5 are used
        self.starting_cylinder = ((tmp & 0xC0) << 2) + \
            self.get_ubyte(3)
        self.part_type = self.get_ubyte(4)
        self.ending_head = self.get_ubyte(5)

        tmp = self.get_ubyte(6)
        self.ending_sector = tmp & 0x3F
        self.ending_cylinder = ((tmp & 0xC0) << 2) + \
            self.get_ubyte(7)
        self.relative_sector = self.get_uint(8)
        self.total_sectors = self.get_uint(12)
        self.part_offset = SECTOR_SIZE*self.relative_sector


class PartitionTable(RawStruct):
    def __init__(self, data):
        RawStruct.__init__(self, data)
        self.entries = []

        for i in range(0, 4):
            entry = PartitionEntry(
                self.get_chunk(PT_ENTRY_SIZE * i, PT_ENTRY_SIZE)
            )

            if (entry.part_type != 0):
                self.entries.append(entry)


class Mbr(RawStruct):
    def __init__(self):
        RawStruct.__init__(self)
        self.partition_table = None

    def load(self, filename):
        """Reads master boot record of the filesystem and
        loads partition table entries
        """
        try:
            with open(filename, 'rb') as f:
                # Verify MBR signature first
                self.load_from_source(f, 0, MBR_SIZE)
                signature = self.get_ushort(MBR_SIG_OFFSET)

                if (signature != MBR_SIGNATURE):
                    raise Exception("Invalid MBR signature")

                self.partition_table = PartitionTable(
                    self.get_chunk(PT_TABLE_OFFSET, PT_TABLE_SIZE)
                )

        except IOError, e:
            print e
