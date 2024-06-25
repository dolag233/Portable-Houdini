class SimpleEnumMetaClass(type):
    def __new__(metacls, name, bases, class_dict):
        cls = super().__new__(metacls, name, bases, class_dict)
        cls._value_map = {}
        cls._name_map = {}
        value = 0
        for key in class_dict:
            if not key.startswith('_') and not callable(class_dict[key]):
                setattr(cls, key, value)
                cls._value_map[value] = key
                cls._name_map[key] = value
                value += 1
        return cls

    def __contains__(cls, value):
        return value in cls._value_map or value in cls._name_map

    def __getitem__(cls, key):
        if isinstance(key, int):
            return cls._value_map[key]
        elif isinstance(key, str):
            return cls._name_map[key]
        raise KeyError(f"Invalid key: {key}")


class SimpleEnum(metaclass=SimpleEnumMetaClass):
    pass
