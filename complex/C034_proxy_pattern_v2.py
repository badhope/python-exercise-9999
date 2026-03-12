# -----------------------------
# 题目：代理模式实现图片懒加载。
# -----------------------------

import time

class Image:
    def __init__(self, filename):
        self.filename = filename
        self._load()
    
    def _load(self):
        print(f"加载图片: {self.filename}")
        time.sleep(0.1)
    
    def display(self):
        return f"显示图片: {self.filename}"

class ImageProxy:
    def __init__(self, filename):
        self.filename = filename
        self._real_image = None
    
    def display(self):
        if self._real_image is None:
            self._real_image = Image(self.filename)
        return self._real_image.display()

class ImageGallery:
    def __init__(self):
        self.images = []
    
    def add_image(self, image):
        self.images.append(image)
    
    def display_all(self):
        results = []
        for image in self.images:
            results.append(image.display())
        return results
    
    def display_one(self, index):
        if 0 <= index < len(self.images):
            return self.images[index].display()
        return None

class ProtectedImageProxy:
    def __init__(self, filename, password):
        self.filename = filename
        self.password = password
        self._real_image = None
        self._authenticated = False
    
    def authenticate(self, password):
        if password == self.password:
            self._authenticated = True
            return True
        return False
    
    def display(self):
        if not self._authenticated:
            return "请先验证身份"
        if self._real_image is None:
            self._real_image = Image(self.filename)
        return self._real_image.display()

class CachedImageProxy:
    _cache = {}
    
    def __init__(self, filename):
        self.filename = filename
    
    def display(self):
        if self.filename not in self._cache:
            self._cache[self.filename] = Image(self.filename)
        return self._cache[self.filename].display()
    
    @classmethod
    def get_cache_size(cls):
        return len(cls._cache)

def main():
    print("=== 懒加载代理 ===")
    gallery = ImageGallery()
    gallery.add_image(ImageProxy("photo1.jpg"))
    gallery.add_image(ImageProxy("photo2.jpg"))
    gallery.add_image(ImageProxy("photo3.jpg"))
    
    print("图片已添加到画廊")
    print("\n显示第一张图片:")
    print(gallery.display_one(0))
    print("\n显示所有图片:")
    for result in gallery.display_all():
        print(result)
    
    print("\n=== 保护代理 ===")
    protected = ProtectedImageProxy("secret.jpg", "123456")
    print(protected.display())
    protected.authenticate("wrong")
    print(protected.display())
    protected.authenticate("123456")
    print(protected.display())
    
    print("\n=== 缓存代理 ===")
    cached1 = CachedImageProxy("cached1.jpg")
    cached2 = CachedImageProxy("cached1.jpg")
    print(cached1.display())
    print(cached2.display())
    print(f"缓存大小: {CachedImageProxy.get_cache_size()}")


if __name__ == "__main__":
    main()
