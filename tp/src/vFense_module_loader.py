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

    def __init__(self):
        self.curr_dir = os.path.dirname(os.path.realpath(__file__)) 
        self.plugins_dir = 'plugins'
        self.plugins_path = os.path.join(self.curr_dir, self.plugins_dir)

        sys.path.append(self.plugins_path)

    def _get_all_plugins(self):
        plugins = []

        for entry in os.listdir(self.plugins_path):
            entry_path = os.path.join(self.plugins_path, entry)
            init_path = os.path.join(entry_path, '__init__.py')

            if os.path.isdir(entry_path) and os.path.exists(init_path):
                module = os.path.join(
                    self.plugins_dir, entry
                ).replace('/', '.')

                plugins.append(module)

        return(plugins)

    def _import_all_plugins(self, plugins):
        imported_plugins = []

        for module in plugins:
            imported_plugins.append(importlib.import_module(module))

        return imported_plugins

    def get_plugins_listener_api_handlers(self):
        plugins = self._get_all_plugins()

        try:
            imported_plugins = self._import_all_plugins(plugins)

            for plugin in imported_plugins:
                if 'get_listener_api_handlers' in plugin.__dict__.keys():
                    return plugin.get_listener_api_handlers()

        except Exception as e:
            print "Log this: {0}".format(e)
            print traceback.format_exc()

    def get_plugins_web_api_handlers(self):
        plugins = self._get_all_plugins()

        try:
            imported_plugins = self._import_all_plugins(plugins)

            for plugin in imported_plugins:
                if 'get_web_api_handlers' in plugin.__dict__.keys():
                    return plugin.get_web_api_handlers()

        except Exception as e:
            print "Log this: {0}".format(e)
            print traceback.format_exc()
