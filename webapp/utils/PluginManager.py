import os
import importlib
import sys
import ctypes
import shutil
import struct

class Plugin:
    def __init__(self, name, packageName, instance, dllHandle):
        self.name = name
        self.packageName = packageName
        self.instance = instance
        self.dllHandle = dllHandle
        self.altitude = instance.altitude

    def call(self, input, architecture):
        return self.instance.process(self.dllHandle, input, architecture)

class PluginManager:
    def __init__(self):
        self.plugins = []

    def runPlugins(self, input, architecture):
        result_dict = {}
        for plugin in self.plugins:
            print(f"Running plugin {plugin.packageName}")
            result_dict[plugin.packageName] = plugin.call(input, architecture)
        return result_dict
    
    def getHtmlFiles(self):
        return [f"plugin_{plugin.packageName}.html" for plugin in sorted(self.plugins, key=lambda x: x.altitude)]

    def loadPlugins(self, pluginDirs):
        sys.path.append(pluginDirs)
        for plugin in os.listdir(pluginDirs):
            print(f"Initializing plugin {plugin}")
            moduleName = plugin
            pluginClassName = None
            dllPath = None
            htmlName = None
            dllHandle = None
            for file in os.listdir(os.path.join(pluginDirs, plugin)):
                if file.endswith('Plugin.py'):
                    pluginClassName = file.replace('.py', '')
                if PluginManager.is32BitPython():
                    if file.endswith('32.dll'):
                        dllPath = os.path.join(pluginDirs, os.path.join(plugin, file))
                else:
                    if file.endswith('64.dll'):
                        dllPath = os.path.join(pluginDirs, os.path.join(plugin, file))
                if file.endswith('.html'):
                    htmlName = file
            htmlSrcPath = os.path.join(pluginDirs, os.path.join(plugin, htmlName))
            htmlDstPath = os.path.join('webapp\\templates', htmlName)
            if not os.path.exists(htmlDstPath):
                shutil.copy(htmlSrcPath, htmlDstPath)
            fullModuleName = f"{moduleName}.{pluginClassName}"
            module = importlib.import_module(fullModuleName)
            class_ = getattr(module, pluginClassName)
            instance = class_()
            if dllPath:
                print(f"Loaded {dllPath}")
                dllHandle = ctypes.WinDLL(dllPath)
            self.plugins.append(Plugin(pluginClassName, plugin, instance, dllHandle))

    @staticmethod
    def is32BitPython():
        return 8 * struct.calcsize("P") == 32