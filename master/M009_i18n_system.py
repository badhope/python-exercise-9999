# -----------------------------
# 题目：实现简单的国际化系统。
# 描述：支持多语言翻译和本地化。
# -----------------------------

class I18n:
    def __init__(self, default_locale='en'):
        self.default_locale = default_locale
        self.translations = {}
        self.current_locale = default_locale
    
    def add_translations(self, locale, translations):
        if locale not in self.translations:
            self.translations[locale] = {}
        self.translations[locale].update(translations)
    
    def set_locale(self, locale):
        self.current_locale = locale
    
    def translate(self, key, **kwargs):
        locale_translations = self.translations.get(self.current_locale, {})
        template = locale_translations.get(key)
        
        if template is None:
            locale_translations = self.translations.get(self.default_locale, {})
            template = locale_translations.get(key, key)
        
        if kwargs:
            return template.format(**kwargs)
        return template
    
    def format_date(self, date):
        formats = {
            'en': '%Y-%m-%d',
            'zh': '%Y年%m月%d日',
            'ja': '%Y年%m月%d日'
        }
        fmt = formats.get(self.current_locale, formats[self.default_locale])
        return date.strftime(fmt)
    
    def format_number(self, number):
        import locale
        try:
            locale.setlocale(locale.LC_ALL, f'{self.current_locale}.utf8')
        except:
            pass
        return locale.format_string('%d', number, grouping=True)

i18n = I18n()

def _(key, **kwargs):
    return i18n.translate(key, **kwargs)

def main():
    i18n.add_translations('en', {
        'hello': 'Hello, {name}!',
        'welcome': 'Welcome to our website',
        'items_count': 'You have {count} items'
    })
    
    i18n.add_translations('zh', {
        'hello': '你好, {name}!',
        'welcome': '欢迎访问我们的网站',
        'items_count': '你有 {count} 个项目'
    })
    
    i18n.set_locale('zh')
    print(_('hello', name='张三'))
    print(_('welcome'))
    print(_('items_count', count=5))
    
    i18n.set_locale('en')
    print(_('hello', name='John'))


if __name__ == "__main__":
    main()
