# -----------------------------
# 题目：抽象工厂模式实现跨平台UI组件。
# -----------------------------

class Button:
    def render(self):
        pass

class TextBox:
    def render(self):
        pass

class Checkbox:
    def render(self):
        pass

class WindowsButton(Button):
    def render(self):
        return "Windows风格按钮"

class WindowsTextBox(TextBox):
    def render(self):
        return "Windows风格文本框"

class WindowsCheckbox(Checkbox):
    def render(self):
        return "Windows风格复选框"

class MacOSButton(Button):
    def render(self):
        return "macOS风格按钮"

class MacOSTextBox(TextBox):
    def render(self):
        return "macOS风格文本框"

class MacOSCheckbox(Checkbox):
    def render(self):
        return "macOS风格复选框"

class LinuxButton(Button):
    def render(self):
        return "Linux风格按钮"

class LinuxTextBox(TextBox):
    def render(self):
        return "Linux风格文本框"

class LinuxCheckbox(Checkbox):
    def render(self):
        return "Linux风格复选框"

class GUIFactory:
    def create_button(self):
        pass
    
    def create_textbox(self):
        pass
    
    def create_checkbox(self):
        pass

class WindowsFactory(GUIFactory):
    def create_button(self):
        return WindowsButton()
    
    def create_textbox(self):
        return WindowsTextBox()
    
    def create_checkbox(self):
        return WindowsCheckbox()

class MacOSFactory(GUIFactory):
    def create_button(self):
        return MacOSButton()
    
    def create_textbox(self):
        return MacOSTextBox()
    
    def create_checkbox(self):
        return MacOSCheckbox()

class LinuxFactory(GUIFactory):
    def create_button(self):
        return LinuxButton()
    
    def create_textbox(self):
        return LinuxTextBox()
    
    def create_checkbox(self):
        return LinuxCheckbox()

class Application:
    def __init__(self, factory):
        self.factory = factory
        self.button = None
        self.textbox = None
        self.checkbox = None
    
    def create_ui(self):
        self.button = self.factory.create_button()
        self.textbox = self.factory.create_textbox()
        self.checkbox = self.factory.create_checkbox()
    
    def render(self):
        print(f"按钮: {self.button.render()}")
        print(f"文本框: {self.textbox.render()}")
        print(f"复选框: {self.checkbox.render()}")

def get_factory(platform):
    factories = {
        'windows': WindowsFactory(),
        'macos': MacOSFactory(),
        'linux': LinuxFactory()
    }
    return factories.get(platform.lower())

def main():
    platforms = ['Windows', 'macOS', 'Linux']
    
    for platform in platforms:
        print(f"\n=== {platform} 应用 ===")
        factory = get_factory(platform)
        app = Application(factory)
        app.create_ui()
        app.render()


if __name__ == "__main__":
    main()
