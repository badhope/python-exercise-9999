# -----------------------------
# 题目：实现简单的插件系统。
# 描述：支持动态加载和管理插件。
# -----------------------------

class Plugin:
    def __init__(self, name):
        self.name = name
    
    def activate(self):
        print(f"插件 {self.name} 已激活")
    
    def deactivate(self):
        print(f"插件 {self.name} 已停用")
    
    def execute(self, *args, **kwargs):
        raise NotImplementedError

class PluginManager:
    def __init__(self):
        self.plugins = {}
        self.active_plugins = set()
    
    def register(self, plugin):
        self.plugins[plugin.name] = plugin
    
    def unregister(self, name):
        if name in self.plugins:
            if name in self.active_plugins:
                self.plugins[name].deactivate()
                self.active_plugins.remove(name)
            del self.plugins[name]
    
    def activate(self, name):
        if name in self.plugins and name not in self.active_plugins:
            self.plugins[name].activate()
            self.active_plugins.add(name)
    
    def deactivate(self, name):
        if name in self.active_plugins:
            self.plugins[name].deactivate()
            self.active_plugins.remove(name)
    
    def execute(self, name, *args, **kwargs):
        if name in self.active_plugins:
            return self.plugins[name].execute(*args, **kwargs)
        return None

class HelloPlugin(Plugin):
    def __init__(self):
        super().__init__("hello")
    
    def execute(self, name):
        return f"Hello, {name}!"

def main():
    manager = PluginManager()
    manager.register(HelloPlugin())
    manager.activate("hello")
    result = manager.execute("hello", "World")
    print(result)


if __name__ == "__main__":
    main()
