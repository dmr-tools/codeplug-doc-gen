from datetime import date
from cpdgen.pattern import Codeplug


class Firmware:
    def __init__(self, name: str = None, released: date = None, codeplug: Codeplug = None):
        self._name = name
        self._released = released
        self._codeplug = codeplug

    def __lt__(self, other):
        if self.has_released() is None or other.has_released() is None:
            return self.get_released() < other.get_released()
        return self.get_name() < other.get_name()

    def is_valid(self) -> bool:
        return bool(self._name) and bool(self._codeplug)

    def get_name(self):
        return self._name

    def set_name(self, name: str):
        self._name = name

    def has_released(self):
        return self._released is not None

    def get_released(self) -> date:
        return self._released

    def set_released(self, released: date):
        self._released = released

    def get_codeplug(self):
        return self._codeplug

    def set_codeplug(self, codeplug: Codeplug):
        self._codeplug = codeplug


class Model:
    def __init__(self, name=None, description=None):
        self._name = name
        self._description = description
        self._manufacturer = None
        self._url = None
        self._versions = []
        self._latest = None

    def __len__(self):
        return len(self._versions)

    def __getitem__(self, item):
        return self._versions[item]

    def __iter__(self):
        return iter(self._versions)

    def is_valid(self) -> bool:
        return bool(self._name)

    def get_name(self) -> str:
        return self._name

    def set_name(self, name: str):
        self._name = name

    def has_description(self) -> bool:
        return bool(self._description)

    def get_description(self) -> str:
        return self._description

    def set_description(self, descr: str):
        self._description = descr

    def get_manufacturer(self):
        return self._manufacturer

    def set_manufacturer(self, manufacturer: str):
        self._manufacturer = manufacturer

    def get_url(self):
        return self._url

    def set_url(self, url):
        self._url = url

    def add(self, firmware: Firmware):
        if self._latest is None or self._latest < firmware:
            self._latest = firmware
        self._versions.append(firmware)
        self._versions.sort()


class Catalog:
    def __init__(self):
        self._models = []

    def __len__(self):
        return len(self._models)

    def __getitem__(self, item):
        return self._models[item]

    def __iter__(self):
        return iter(self._models)

    def is_valid(self) -> bool:
        return True

    def add(self, model: Model):
        self._models.append(model)

