import os
import sys
import importlib
import inspect
import traceback

class CoreLoader():

    def get_core_listener_api_handlers(self):
        return []

    def get_core_web_api_handlers(self):
        return []

class PluginsLoader():
    """Used to retrieve the listener and web api's from every plugin."""

    def __init__(self):
        """Append the plugins directory to sys path."""
        self.curr_dir = os.path.dirname(os.path.realpath(__file__)) 
        self.plugins_dir = 'plugins'
        self.plugins_path = os.path.join(self.curr_dir, self.plugins_dir)

        sys.path.append(self.plugins_path)

    def _get_all_plugins(self):
        """Search through the plugins directory and find all directories
        with an __init__.py file. These directories will be considered
        plugins.
        
        Basic usage:
            >>> from vFense_module_loader import PluginsLoader
            >>> loader = PluginsLoader()
            >>> plugins = loader._get_all_plugins()
            >>> print plugins
            >>> ['plugins.patching', 'plugins.monit', ...]

        Returns:
            (list str) - A list of modules as strings corresponding to found
                plugins.

                Ex: ['plugins.patching', 'plugins.monit', ...]
        """
        plugins = []

        for entry in os.listdir(self.plugins_path):
            entry_path = os.path.join(self.plugins_path, entry)
            init_path = os.path.join(entry_path, '__init__.py')

            if os.path.isdir(entry_path) and os.path.exists(init_path):
                module = os.path.join(
                    self.plugins_dir, entry
                ).replace('/', '.')

                plugins.append(module)

        return plugins

    def _import_all_plugins(self, plugins):
        """Imports the modules given.

        Args:
            plugins (list): A list of modules as strings corresponding to
                plugins.

                Ex: ['plugins.patching', 'plugins.monit', ...]

        Basic usage:
            >>> from vFense_module_loader import PluginsLoader
            >>> loader = PluginsLoader()
            >>> imported = loader._import_all_plugins(plugins)
            >>> print imported
            >>> [<module 'plugins.monit' from 'plugins/monit/__init__.pyc'>]

        Returns:
            (list): A list of loaded modules.

            Ex: [<module 'plugins.monit' from 'plugins/monit/__init__.pyc'>]
        """
        imported_plugins = []

        for module in plugins:
            try:
                imported_plugins.append(importlib.import_module(module))
            except Exception as e:
                print "Failed to import {0} because of: {1}".format(
                    module, e
                )

                continue

        return imported_plugins

    def get_plugins_listener_api_handlers(self):
        """Retrieves the listener handlers from every plugin by calling the
        get_listener_api_handlers function of every plugin found.
        
        Basic usage:
            >>> from vFense_module_loader import PluginsLoader
            >>> loader = PluginsLoader()
            >>> loader.get_plugins_listener_api_handlers()

        Returns:
            (list) - Returns a list of tuples where the first element is
                the regex to be handled and the second element is
                the class that will be used to handle that regex.

            Ex:
                [('/rvl/v1/([a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[a-f0-9]{4}-[a-f0-9]{12})/monitoring/monitordata/?',
                <class 'vFense.plugins.monit.api_handlers.UpdateMonitoringStatsV1'>)]

        """

        plugins = self._get_all_plugins()
        imported_plugins = self._import_all_plugins(plugins)

        handlers = []
        for plugin in imported_plugins:
            try:
                if 'get_listener_api_handlers' in plugin.__dict__.keys():
                    handlers.extend(plugin.get_listener_api_handlers())

            except Exception as e:
                print "Failed to get listener handlers: {0}".format(e)
                print traceback.format_exc()

        return handlers

    def get_plugins_web_api_handlers(self):
        """Retrieves the listener handlers from every plugin by calling the
        get_plugins_web_api_handlers function of every plugin found.
        
        Basic usage:
            >>> from vFense_module_loader import PluginsLoader
            >>> loader = PluginsLoader()
            >>> loader.get_plugins_web_api_handlers()

        Returns:
            (list) - Returns a list of tuples where the first element is
                the regex to be handled and the second element is
                the class that will be used to handle that regex.

            Ex:
                [('/api/monitor/memory/?', <class 'vFense.plugins.monit.api_handlers.GetMemoryStats'>),
                ('/api/monitor/filesystem/?', <class 'vFense.plugins.monit.api_handlers.GetFileSystemStats'>)]

        """
        plugins = self._get_all_plugins()
        imported_plugins = self._import_all_plugins(plugins)

        handlers = []
        for plugin in imported_plugins:
            try:
                if 'get_web_api_handlers' in plugin.__dict__.keys():
                    handlers.extend(plugin.get_web_api_handlers())

            except Exception as e:
                print "Failed to get web handlers: {0}".format(e)
                print traceback.format_exc()

        return handlers
