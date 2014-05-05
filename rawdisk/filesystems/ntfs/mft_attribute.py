import hexdump
from rawdisk.util.rawstruct import RawStruct

MFT_ATTR_HEADER_SIZE = 16

MFT_ATTR_STANDARD_INFORMATION = 0x10
MFT_ATTR_ATTRIBUTE_LIST = 0x20
MFT_ATTR_FILENAME = 0x30
MFT_ATTR_OBJECT_ID = 0x40
MFT_ATTR_SECURITY_DESCRIPTOR = 0x50
MFT_ATTR_VOLUME_NAME = 0x60
MFT_ATTR_VOLUME_INFO = 0x70
MFT_ATTR_DATA = 0x80
MFT_ATTR_INDEX_ROOT = 0x90
MFT_ATTR_INDEX_ALLOCATION = 0xA0
MFT_ATTR_BITMAP = 0xB0
MFT_ATTR_REPARSE_POINT = 0xC0
MFT_ATTR_LOGGED_TOOLSTREAM = 0x100


class MftAttrHeader(RawStruct):
    def __init__(self, data):
        RawStruct.__init__(self, data)
        self.type = self.get_uint(0)
        self.length = self.get_uint(4)
        self.non_resident_flag = self.get_ubyte(8)
        self.length_of_name = self.get_ubyte(9)     # Used only for ADS
        self.offset_to_name = self.get_ushort(10)   # Used only for ADS
        self.flags = self.get_ushort(12)  # (Compressed, Encrypted, Sparse)
        self.identifier = self.get_ushort(14)


class MftAttr(RawStruct):
    def __init__(self, data):
        RawStruct.__init__(self, data)
        self.header = MftAttrHeader(
            self.get_chunk(0, MFT_ATTR_HEADER_SIZE)
        )


# Define all attribute types here
class MftAttrStandardInformation(MftAttr):
    def __init__(self, data):
        MftAttr.__init__(self, data)


class MftAttrAttributeList(MftAttr):
    def __init__(self, data):
        MftAttr.__init__(self, data)


class MftAttrFilename(MftAttr):
    def __init__(self, data):
        MftAttr.__init__(self, data)


class MftAttrObjectId(MftAttr):
    def __init__(self, data):
        MftAttr.__init__(self, data)


class MftAttrSecurityDescriptor(MftAttr):
    def __init__(self, data):
        MftAttr.__init__(self, data)


class MftAttrVolumeName(MftAttr):
    def __init__(self, data):
        MftAttr.__init__(self, data)


class MftAttrVolumeInfo(MftAttr):
    def __init__(self, data):
        MftAttr.__init__(self, data)


class MftAttrData(MftAttr):
    def __init__(self, data):
        MftAttr.__init__(self, data)


class MftAttrIndexRoot(MftAttr):
    def __init__(self, data):
        MftAttr.__init__(self, data)


class MftAttrIndexAllocation(MftAttr):
    def __init__(self, data):
        MftAttr.__init__(self, data)


class MftAttrBitmap(MftAttr):
    def __init__(self, data):
        MftAttr.__init__(self, data)


class MftAttrReparsePoint(MftAttr):
    def __init__(self, data):
        MftAttr.__init__(self, data)


class MftAttrLoggedToolstream(MftAttr):
    def __init__(self, data):
        MftAttr.__init__(self, data)
