# -----------------------------
# 题目：实现国际化系统。
# -----------------------------

class I18n:
    def __init__(self, default_locale="en"):
        self.default_locale = default_locale
        self.translations = {}
        self.current_locale = default_locale
    
    def add_translations(self, locale, translations):
        if locale not in self.translations:
            self.translations[locale] = {}
        self.translations[locale].update(translations)
    
    def set_locale(self, locale):
        if locale in self.translations:
            self.current_locale = locale
    
    def get(self, key, **kwargs):
        locale = self.current_locale
        
        if key not in self.translations.get(locale, {}):
            locale = self.default_locale
        
        if key not in self.translations.get(locale, {}):
            return key
        
        message = self.translations[locale][key]
        
        if kwargs:
            try:
                message = message.format(**kwargs)
            except KeyError:
                pass
        
        return message
    
    def __call__(self, key, **kwargs):
        return self.get(key, **kwargs)

i18n = I18n("zh")

i18n.add_translations("zh", {
    "hello": "你好 {name}",
    "welcome": "欢迎来到我们的应用",
    "items": "你有 {count} 个项目"
})

i18n.add_translations("en", {
    "hello": "Hello {name}",
    "welcome": "Welcome to our app",
    "items": "You have {count} items"
})

if __name__ == "__main__":
    print(i18n("hello", name="张三"))
    print(i18n("welcome"))
    print(i18n("items", count=5))
    
    i18n.set_locale("en")
    print(i18n("hello", name="John"))
