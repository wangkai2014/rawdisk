# -*- coding: utf-8 -*-
from rawdisk.util.rawstruct import RawStruct
from .headers import MBR_PARTITION_ENTRY
from rawdisk.util.addressing import chs2lba
import logging


MBR_SIGNATURE = 0xAA55
MBR_SIG_SIZE = 2
MBR_SIG_OFFSET = 0x1FE
MBR_SIZE = 512
MBR_NUM_PARTS = 4
PARTITION_ENTRY_SIZE = 16
PARTITION_TABLE_OFFSET = 0x1BE
PARTITION_TABLE_SIZE = PARTITION_ENTRY_SIZE * MBR_NUM_PARTS
SECTOR_SIZE = 512

logger = logging.getLogger(__name__)


class MbrPartitionEntry(RawStruct):
    def __init__(self, data):
        RawStruct.__init__(self, data)

        tmp = self.get_ubyte(2)
        tmp2 = self.get_ubyte(6)

        self.fields = MBR_PARTITION_ENTRY(
            self.get_ubyte(0),          # boot indicator
            self.get_ubyte(1),          # starting_head
            tmp & 0x3F,                 # starting_sector
            ((tmp & 0xC0) << 2) +
            self.get_ubyte(3),          # starting cylinder
            self.get_ubyte(4),          # part_type
            self.get_ubyte(5),          # ending_head
            tmp2 & 0x3F,                # ending_sector
            ((tmp2 & 0xC0) << 2) +
            self.get_ubyte(7),      # ending cylinder
            self.get_uint_le(8),        # relative sector
            self.get_uint_le(12),       # total sectors
        )

    @property
    def part_offset(self):
        lba = chs2lba(
            cylinder=self.fields.starting_cylinder,
            head=self.fields.starting_head,
            sector=self.fields.starting_sector
        )

        # use chs if relative_sector is 0 (which is the case for small images,
        # formatted with linux fdisk)
        if (lba != self.fields.relative_sector
                and self.fields.relative_sector != 0):
            lba = self.fields.relative_sector

        return SECTOR_SIZE * lba

    @property
    def part_type(self):
        return self.fields.part_type

    @property
    def total_sectors(self):
        return self.fields.total_sectors


class PartitionTable(RawStruct):
    """Represents MBR partition table.

    Args:
        data (bytes): byte array to initialize structure with.

    Attributes:
        entries (list): List of initialized :class:`PartitionEntry` objects
    """
    def __init__(self, data):
        RawStruct.__init__(self, data)
        self.__partitions = []

        for i in range(0, MBR_NUM_PARTS):
            entry = MbrPartitionEntry(
                self.get_chunk(PARTITION_ENTRY_SIZE * i, PARTITION_ENTRY_SIZE)
            )

            if entry.fields.part_type != 0:
                self.__partitions.append(entry)

    @property
    def partitions(self):
        return self.__partitions


class Mbr(RawStruct):
    """Represents the Master Boot Record of the filesystem.

    Args:
        filename (str): path to file or device to open for reading

    Attributes:
        partition_table (PartitionTable): Initialized \
        :class:`PartitionTable` object

    Raises:
        IOError: If file does not exist or is not readable.
        Exception: If source has invalid MBR signature
    """

    def __init__(self, filename=None, load_partition_table=True, offset=0):
        self.__offset = offset

        RawStruct.__init__(
            self,
            filename=filename,
            offset=offset,
            length=MBR_SIZE
        )

        self.bootstrap = self.get_chunk(0, 446)
        signature = self.get_ushort_le(MBR_SIG_OFFSET)

        if signature != MBR_SIGNATURE:
            raise Exception("Invalid MBR signature")

        if load_partition_table:
            self.__load_partition_table()

    @property
    def partition_table(self):
        return self.__partition_table

    @property
    def offset(self):
        return self.__offset

    def export_bootstrap(self, filename):
        self.export(filename, 0, 446)

    def __load_partition_table(self):
        logger.info('Loading partition table')
        self.__partition_table = PartitionTable(
            self.get_chunk(PARTITION_TABLE_OFFSET, PARTITION_TABLE_SIZE)
        )
