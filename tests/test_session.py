import unittest
from rawdisk.session import Session
from rawdisk.filesystems.unknown_volume import UnknownVolume
from rawdisk.scheme.common import PartitionScheme


class TestSession(unittest.TestCase):
    def setUp(self):
        self.session = Session(load_plugins=False)

    def test_load_fileystem_plugins(self):
        self.session.load_plugins()

    def test_load_mbr_without_plugins(self):
        self.session.load(filename='sample_images/ntfs_mbr.vhd')
        self.assertEqual(self.session.partition_scheme,
                         PartitionScheme.SCHEME_MBR)
        self.assertEqual(len(self.session.volumes), 1)
        self.assertEqual(type(self.session.volumes[0]), UnknownVolume)

    def test_load_mbr(self):
        self.session.load_plugins()
        self.session.load(filename='sample_images/ntfs_mbr.vhd')
        self.assertEqual(self.session.partition_scheme,
                         PartitionScheme.SCHEME_MBR)
        self.assertEqual(len(self.session.volumes), 1)

    def test_load_gpt(self):
        # truncated image, actual partitions are missing, plugins won't work
        self.session.load(filename='sample_images/ntfs_primary_gpt.bin')
        self.assertEqual(self.session.partition_scheme,
                         PartitionScheme.SCHEME_GPT)
        self.assertEqual(len(self.session.volumes), 2)
