# -----------------------------
# 题目：建造者模式实现配置构建。
# 描述：使用建造者模式构建复杂配置对象。
# -----------------------------

class Config:
    def __init__(self):
        self.host = "localhost"
        self.port = 8080
        self.debug = False
        self.database = None
        self.cache = None
    
    def __str__(self):
        return f"Config(host={self.host}, port={self.port}, debug={self.debug}, db={self.database}, cache={self.cache})"

class ConfigBuilder:
    def __init__(self):
        self.config = Config()
    
    def set_host(self, host):
        self.config.host = host
        return self
    
    def set_port(self, port):
        self.config.port = port
        return self
    
    def set_debug(self, debug):
        self.config.debug = debug
        return self
    
    def set_database(self, database):
        self.config.database = database
        return self
    
    def set_cache(self, cache):
        self.config.cache = cache
        return self
    
    def build(self):
        return self.config

def main():
    config = ConfigBuilder() \
        .set_host("0.0.0.0") \
        .set_port(3000) \
        .set_debug(True) \
        .set_database("mysql") \
        .build()
    print(config)


if __name__ == "__main__":
    main()
