import json

class JsonVar:
    _path = ""
    @classmethod
    def _attributes(cls):
        """获取类的所有类属性（不含实例属性）"""
        return {k: v for k, v in cls.__dict__.items() if not k.startswith('_')}
    @classmethod
    def dump(cls):
        with open(cls._path, "w", encoding="utf-8") as f:
            json.dump(cls._attributes(), f)
    @classmethod
    def load(cls):
        with open(cls._path, "r", encoding="utf-8") as f:
            attrs = json.load(f)
        for k, v in attrs.items():
            setattr(cls, k, v)