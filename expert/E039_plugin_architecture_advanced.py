# -----------------------------
# 题目：实现插件架构高级版。
# -----------------------------

from typing import Dict, List, Any, Callable, Type, Optional
from dataclasses import dataclass
from abc import ABC, abstractmethod
import importlib
import inspect

@dataclass
class PluginInfo:
    name: str
    version: str
    description: str
    author: str = ""
    dependencies: List[str] = None

class PluginBase(ABC):
    @classmethod
    @abstractmethod
    def get_info(cls) -> PluginInfo:
        pass
    
    @abstractmethod
    def initialize(self, context: 'PluginContext'):
        pass
    
    @abstractmethod
    def shutdown(self):
        pass

class PluginContext:
    def __init__(self, manager: 'PluginManager'):
        self.manager = manager
        self.services: Dict[str, Any] = {}
        self.hooks: Dict[str, List[Callable]] = {}
        self.config: Dict[str, Any] = {}
    
    def register_service(self, name: str, service: Any):
        self.services[name] = service
    
    def get_service(self, name: str) -> Optional[Any]:
        return self.services.get(name)
    
    def register_hook(self, name: str, callback: Callable):
        if name not in self.hooks:
            self.hooks[name] = []
        self.hooks[name].append(callback)
    
    def execute_hook(self, name: str, *args, **kwargs) -> List[Any]:
        results = []
        for callback in self.hooks.get(name, []):
            try:
                result = callback(*args, **kwargs)
                results.append(result)
            except Exception as e:
                print(f"Hook执行失败: {e}")
        return results
    
    def set_config(self, key: str, value: Any):
        self.config[key] = value
    
    def get_config(self, key: str, default: Any = None) -> Any:
        return self.config.get(key, default)

class PluginManager:
    def __init__(self):
        self.plugins: Dict[str, PluginBase] = {}
        self.context = PluginContext(self)
        self._plugin_classes: Dict[str, Type[PluginBase]] = {}
        self._loaders: List['PluginLoader'] = []
    
    def register_plugin_class(self, plugin_class: Type[PluginBase]):
        info = plugin_class.get_info()
        self._plugin_classes[info.name] = plugin_class
    
    def add_loader(self, loader: 'PluginLoader'):
        self._loaders.append(loader)
    
    def discover_plugins(self):
        for loader in self._loaders:
            for plugin_class in loader.load():
                self.register_plugin_class(plugin_class)
    
    def load_plugin(self, name: str) -> bool:
        if name in self.plugins:
            return True
        
        plugin_class = self._plugin_classes.get(name)
        if not plugin_class:
            return False
        
        info = plugin_class.get_info()
        
        if info.dependencies:
            for dep in info.dependencies:
                if dep not in self.plugins:
                    if not self.load_plugin(dep):
                        return False
        
        plugin = plugin_class()
        plugin.initialize(self.context)
        self.plugins[name] = plugin
        
        return True
    
    def unload_plugin(self, name: str) -> bool:
        if name not in self.plugins:
            return False
        
        for plugin_name, plugin in self.plugins.items():
            info = plugin.__class__.get_info()
            if info.dependencies and name in info.dependencies:
                self.unload_plugin(plugin_name)
        
        self.plugins[name].shutdown()
        del self.plugins[name]
        
        return True
    
    def get_plugin(self, name: str) -> Optional[PluginBase]:
        return self.plugins.get(name)
    
    def get_loaded_plugins(self) -> List[str]:
        return list(self.plugins.keys())
    
    def execute_hook(self, name: str, *args, **kwargs) -> List[Any]:
        return self.context.execute_hook(name, *args, **kwargs)

class PluginLoader(ABC):
    @abstractmethod
    def load(self) -> List[Type[PluginBase]]:
        pass

class DirectoryPluginLoader(PluginLoader):
    def __init__(self, directory: str):
        self.directory = directory
    
    def load(self) -> List[Type[PluginBase]]:
        import os
        plugins = []
        
        if not os.path.exists(self.directory):
            return plugins
        
        for filename in os.listdir(self.directory):
            if filename.endswith('.py') and not filename.startswith('_'):
                module_name = filename[:-3]
                try:
                    spec = importlib.util.spec_from_file_location(
                        module_name,
                        os.path.join(self.directory, filename)
                    )
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    
                    for name, obj in inspect.getmembers(module):
                        if (inspect.isclass(obj) and 
                            issubclass(obj, PluginBase) and 
                            obj != PluginBase):
                            plugins.append(obj)
                except Exception as e:
                    print(f"加载插件失败 {filename}: {e}")
        
        return plugins

class PluginRegistry:
    _plugins: Dict[str, Type[PluginBase]] = {}
    
    @classmethod
    def register(cls, plugin_class: Type[PluginBase]):
        info = plugin_class.get_info()
        cls._plugins[info.name] = plugin_class
        return plugin_class
    
    @classmethod
    def get(cls, name: str) -> Optional[Type[PluginBase]]:
        return cls._plugins.get(name)
    
    @classmethod
    def all(cls) -> Dict[str, Type[PluginBase]]:
        return cls._plugins.copy()

def plugin(cls):
    return PluginRegistry.register(cls)

class LoggerPlugin(PluginBase):
    @classmethod
    def get_info(cls) -> PluginInfo:
        return PluginInfo(
            name="logger",
            version="1.0.0",
            description="日志插件"
        )
    
    def initialize(self, context: PluginContext):
        self.context = context
        context.register_service("logger", self)
        context.register_hook("on_log", self._on_log)
        print("日志插件已加载")
    
    def shutdown(self):
        print("日志插件已卸载")
    
    def _on_log(self, level: str, message: str):
        print(f"[{level}] {message}")
    
    def log(self, level: str, message: str):
        self.context.execute_hook("on_log", level, message)

class CachePlugin(PluginBase):
    @classmethod
    def get_info(cls) -> PluginInfo:
        return PluginInfo(
            name="cache",
            version="1.0.0",
            description="缓存插件",
            dependencies=["logger"]
        )
    
    def initialize(self, context: PluginContext):
        self.context = context
        self._cache: Dict[str, Any] = {}
        context.register_service("cache", self)
        print("缓存插件已加载")
    
    def shutdown(self):
        self._cache.clear()
        print("缓存插件已卸载")
    
    def get(self, key: str) -> Any:
        return self._cache.get(key)
    
    def set(self, key: str, value: Any):
        self._cache[key] = value
        logger = self.context.get_service("logger")
        if logger:
            logger.log("DEBUG", f"缓存设置: {key}")

def main():
    manager = PluginManager()
    
    manager.register_plugin_class(LoggerPlugin)
    manager.register_plugin_class(CachePlugin)
    
    print("=== 加载插件 ===")
    manager.load_plugin("cache")
    
    print(f"\n已加载插件: {manager.get_loaded_plugins()}")
    
    print("\n=== 使用插件服务 ===")
    cache = manager.context.get_service("cache")
    if cache:
        cache.set("user:1", {"name": "张三"})
        print(f"获取缓存: {cache.get('user:1')}")
    
    print("\n=== 执行钩子 ===")
    manager.execute_hook("on_log", "INFO", "测试消息")
    
    print("\n=== 卸载插件 ===")
    manager.unload_plugin("logger")
    print(f"剩余插件: {manager.get_loaded_plugins()}")


if __name__ == "__main__":
    main()
