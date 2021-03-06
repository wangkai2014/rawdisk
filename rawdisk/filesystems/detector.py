# -*- coding: utf-8 -*-

"""This module is mostly used by plugins to register filesystem
detection routines that are internaly used by rawdisk.reader.Reader
to match filesystems"""

from collections import defaultdict
import logging
import uuid
import itertools


class FilesystemDetector(object):
    """A class that allows to match filesystem id or guid against available
    plugins.
    """
    def __init__(self, fs_plugins=None):
        self.logger = logging.getLogger(__name__)
        # 2 dimensional array of fs_id : [list of plugins]
        self.__mbr_plugins = defaultdict(list)
        # 2 dimensional array of fs_guid : [list of plugins]
        self.__gpt_plugins = defaultdict(list)

        if fs_plugins is not None:
            self.__register_plugins(fs_plugins=fs_plugins)

    def __register_plugins(self, fs_plugins):
        self.logger.debug('Registering filesystem plugins')

        for plugin in fs_plugins:
            gpt_identifiers = plugin.gpt_identifiers
            mbr_identifiers = plugin.mbr_identifiers

            for fs_id in mbr_identifiers:
                self.register_mbr_plugin(fs_id=fs_id, plugin=plugin)

            for fs_guid in gpt_identifiers:
                self.register_gpt_plugin(fs_guid=fs_guid, plugin=plugin)

    def clear_plugins(self):
        self.__mbr_plugins.clear()
        self.__gpt_plugins.clear()

    def __get_plugin_name(self, plugin):
        return type(plugin).__name__

    @property
    def all_plugins(self):
        gpt_plugins = self.get_gpt_plugins()
        mbr_plugins = self.get_mbr_plugins()
        return gpt_plugins + mbr_plugins

    def get_gpt_plugins(self, fs_guid=None):
        if fs_guid is None:
            return list(
                itertools.chain.from_iterable(self.__gpt_plugins.values()))
        else:
            return self.__gpt_plugins.get(fs_guid)

    def get_mbr_plugins(self, fs_id=None):
        if fs_id is None:
            return list(
                itertools.chain.from_iterable(self.__mbr_plugins.values()))
        else:
            return self.__mbr_plugins.get(fs_id)

    def register_mbr_plugin(self, fs_id, plugin):
        """Used in plugin's registration routine,
        to associate it's detection method with given filesystem id

        Args:
            fs_id: filesystem id that is read from MBR partition entry
            plugin: plugin that supports this filesystem
        """
        self.logger.debug('MBR: {}, FS ID: {}'
                          .format(self.__get_plugin_name(plugin), fs_id))
        self.__mbr_plugins[fs_id].append(plugin)

    def register_gpt_plugin(self, fs_guid, plugin):
        """Used in plugin's registration routine,
        to associate it's detection method with given filesystem guid

        Args:
            fs_guid: filesystem guid that is read from GPT partition entry
            plugin: plugin that supports this filesystem
        """
        key = uuid.UUID(fs_guid.lower())

        self.logger.debug('GPT: {}, GUID: {}'
                          .format(self.__get_plugin_name(plugin), fs_guid))
        self.__gpt_plugins[key].append(plugin)

    def detect_standalone(self, filename, offset):
        for plugin in self.all_plugins:
            if plugin.detect(filename, offset, standalone=True):
                return plugin.get_volume_object()

    def detect_mbr(self, filename, offset, fs_id):
        """Used by rawdisk.session.Session to match mbr partitions against
        filesystem plugins.

        Args:
            filename: device or file that it will read in order to detect
            the filesystem fs_id: filesystem id to match (ex. 0x07)
            offset: offset for the filesystem that is being matched

        Returns:
            Volume object supplied by matched plugin.
            If there is no match, None is returned
        """
        self.logger.debug('Detecting MBR partition type')

        if fs_id not in self.__mbr_plugins:
            return None
        else:
            plugins = self.__mbr_plugins.get(fs_id)
            for plugin in plugins:
                if plugin.detect(filename, offset):
                    return plugin.get_volume_object()
        return None

    def detect_gpt(self, filename, offset, fs_guid):
        """Used by rawdisk.session.Session to match gpt partitions agains
        filesystem plugins.

        Args:
            filename: device or file that it will read in order to detect the
            filesystem
            fs_id: filesystem guid to match
            (ex. {EBD0A0A2-B9E5-4433-87C0-68B6B72699C7})
            offset: offset for the filesystem that is being matched

        Returns:
            Volume object supplied by matched plugin.
            If there is no match, None is returned
        """
        self.logger.debug('Detecting GPT partition type')

        if fs_guid not in self.__gpt_plugins:
            return None
        else:
            plugins = self.__gpt_plugins.get(fs_guid)
            for plugin in plugins:
                if plugin.detect(filename, offset):
                    return plugin.get_volume_object()

        return None
