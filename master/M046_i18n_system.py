# -----------------------------
# 题目：实现国际化系统。
# 描述：支持多语言、区域设置、消息格式化。
# -----------------------------

import json
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum
import re

class Locale(Enum):
    ZH_CN = "zh-CN"
    EN_US = "en-US"
    JA_JP = "ja-JP"
    KO_KR = "ko-KR"

@dataclass
class LocaleConfig:
    locale: Locale
    decimal_separator: str = "."
    thousands_separator: str = ","
    date_format: str = "%Y-%m-%d"
    time_format: str = "%H:%M:%S"
    currency_symbol: str = "$"
    currency_position: str = "before"

LOCALE_CONFIGS: Dict[Locale, LocaleConfig] = {
    Locale.ZH_CN: LocaleConfig(
        locale=Locale.ZH_CN,
        decimal_separator=".",
        thousands_separator=",",
        date_format="%Y年%m月%d日",
        time_format="%H:%M:%S",
        currency_symbol="¥",
        currency_position="before"
    ),
    Locale.EN_US: LocaleConfig(
        locale=Locale.EN_US,
        decimal_separator=".",
        thousands_separator=",",
        date_format="%m/%d/%Y",
        time_format="%I:%M:%S %p",
        currency_symbol="$",
        currency_position="before"
    ),
    Locale.JA_JP: LocaleConfig(
        locale=Locale.JA_JP,
        decimal_separator=".",
        thousands_separator=",",
        date_format="%Y年%m月%d日",
        time_format="%H:%M:%S",
        currency_symbol="¥",
        currency_position="before"
    ),
}

class MessageBundle:
    def __init__(self):
        self._messages: Dict[Locale, Dict[str, str]] = {}
    
    def add_messages(self, locale: Locale, messages: Dict[str, str]):
        if locale not in self._messages:
            self._messages[locale] = {}
        self._messages[locale].update(messages)
    
    def get(self, key: str, locale: Locale, default: str = None) -> str:
        locale_messages = self._messages.get(locale, {})
        return locale_messages.get(key, default or key)
    
    def format(self, key: str, locale: Locale, **kwargs) -> str:
        template = self.get(key, locale)
        
        for name, value in kwargs.items():
            placeholder = "{" + name + "}"
            template = template.replace(placeholder, str(value))
        
        return template

class NumberFormatter:
    def __init__(self, locale: Locale):
        self.config = LOCALE_CONFIGS.get(locale, LOCALE_CONFIGS[Locale.EN_US])
    
    def format_number(self, value: float, decimals: int = 2) -> str:
        format_str = f"{{:.{decimals}f}}"
        formatted = format_str.format(value)
        
        parts = formatted.split(".")
        integer_part = parts[0]
        decimal_part = parts[1] if len(parts) > 1 else ""
        
        result = ""
        for i, digit in enumerate(reversed(integer_part)):
            if i > 0 and i % 3 == 0:
                result = self.config.thousands_separator + result
            result = digit + result
        
        if decimal_part:
            result += self.config.decimal_separator + decimal_part
        
        return result
    
    def format_currency(self, value: float, currency: str = None) -> str:
        formatted = self.format_number(value, 2)
        symbol = currency or self.config.currency_symbol
        
        if self.config.currency_position == "before":
            return f"{symbol}{formatted}"
        else:
            return f"{formatted}{symbol}"
    
    def format_percent(self, value: float, decimals: int = 2) -> str:
        return self.format_number(value * 100, decimals) + "%"

class DateFormatter:
    def __init__(self, locale: Locale):
        self.config = LOCALE_CONFIGS.get(locale, LOCALE_CONFIGS[Locale.EN_US])
    
    def format_date(self, date) -> str:
        return date.strftime(self.config.date_format)
    
    def format_time(self, date) -> str:
        return date.strftime(self.config.time_format)
    
    def format_datetime(self, date) -> str:
        return f"{self.format_date(date)} {self.format_time(date)}"

class I18n:
    def __init__(self, default_locale: Locale = Locale.ZH_CN):
        self.default_locale = default_locale
        self.current_locale = default_locale
        self.messages = MessageBundle()
        self._load_default_messages()
    
    def _load_default_messages(self):
        self.messages.add_messages(Locale.ZH_CN, {
            "welcome": "欢迎",
            "hello": "你好，{name}！",
            "goodbye": "再见",
            "error.not_found": "未找到资源",
            "error.permission_denied": "权限不足",
            "success.saved": "保存成功",
            "item.count": "共 {count} 个项目"
        })
        
        self.messages.add_messages(Locale.EN_US, {
            "welcome": "Welcome",
            "hello": "Hello, {name}!",
            "goodbye": "Goodbye",
            "error.not_found": "Resource not found",
            "error.permission_denied": "Permission denied",
            "success.saved": "Saved successfully",
            "item.count": "{count} items in total"
        })
        
        self.messages.add_messages(Locale.JA_JP, {
            "welcome": "ようこそ",
            "hello": "こんにちは、{name}さん！",
            "goodbye": "さようなら",
            "error.not_found": "リソースが見つかりません",
            "success.saved": "保存しました"
        })
    
    def set_locale(self, locale: Locale):
        self.current_locale = locale
    
    def t(self, key: str, **kwargs) -> str:
        if kwargs:
            return self.messages.format(key, self.current_locale, **kwargs)
        return self.messages.get(key, self.current_locale)
    
    def number(self) -> NumberFormatter:
        return NumberFormatter(self.current_locale)
    
    def date(self) -> DateFormatter:
        return DateFormatter(self.current_locale)
    
    def format_number(self, value: float, decimals: int = 2) -> str:
        return self.number().format_number(value, decimals)
    
    def format_currency(self, value: float, currency: str = None) -> str:
        return self.number().format_currency(value, currency)
    
    def format_date(self, date) -> str:
        return self.date().format_date(date)
    
    def format_datetime(self, date) -> str:
        return self.date().format_datetime(date)

def i18n_context(locale: Locale):
    def decorator(func):
        def wrapper(i18n: I18n, *args, **kwargs):
            old_locale = i18n.current_locale
            i18n.set_locale(locale)
            try:
                return func(i18n, *args, **kwargs)
            finally:
                i18n.set_locale(old_locale)
        return wrapper
    return decorator

def main():
    i18n = I18n()
    
    print("=== 中文 ===")
    i18n.set_locale(Locale.ZH_CN)
    print(i18n.t("welcome"))
    print(i18n.t("hello", name="张三"))
    print(i18n.t("item.count", count=100))
    print(f"数字: {i18n.format_number(1234567.89)}")
    print(f"货币: {i18n.format_currency(1234.56)}")
    
    print("\n=== English ===")
    i18n.set_locale(Locale.EN_US)
    print(i18n.t("welcome"))
    print(i18n.t("hello", name="John"))
    print(i18n.t("item.count", count=100))
    print(f"Number: {i18n.format_number(1234567.89)}")
    print(f"Currency: {i18n.format_currency(1234.56)}")
    
    print("\n=== 日本語 ===")
    i18n.set_locale(Locale.JA_JP)
    print(i18n.t("welcome"))
    print(i18n.t("hello", name="田中"))
    print(f"数字: {i18n.format_number(1234567.89)}")
    print(f"通貨: {i18n.format_currency(1234.56)}")
    
    from datetime import datetime
    print(f"\n日期格式化:")
    now = datetime.now()
    i18n.set_locale(Locale.ZH_CN)
    print(f"中文: {i18n.format_datetime(now)}")
    i18n.set_locale(Locale.EN_US)
    print(f"英文: {i18n.format_datetime(now)}")

if __name__ == "__main__":
    main()
