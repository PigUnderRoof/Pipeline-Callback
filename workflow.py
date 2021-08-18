from functools import wraps
from typing import Dict, List, Callable


def check_callback(f: Callable) -> Callable:
    event = f.__name__

    @wraps(f)
    def _inner(self, *args, **kwargs):
        if f'before_{event}' in self.cbsMap.keys():
            for cb in self.cbsMap[f'before_{event}']:
                getattr(cb, f'before_{event}')(*args, **kwargs)

        result = f(self, **kwargs)

        if f'after_{event}' in self.cbsMap.keys():
            for cb in self.cbsMap[f'after_{event}']:
                getattr(cb, f'after_{event}')(result)

        return result

    return _inner


class CallBack:
    _defaults = ['order', 'name', 'events']
    order = 0

    @property
    def name(self) -> str:
        return self.__class__.__name__

    @property
    def events(self) -> List[str]:
        return list(filter(lambda x: (not x.startswith('_')) and (x not in self._defaults), self.__dir__()))

    def __repr__(self) -> str:
        return self.name


class WorkFlow:
    def __init__(self) -> None:
        self.events: List[str] = []
        self.cbs: List[CallBack] = []
        self.cbsMap: Dict[str, List[CallBack]] = {}

    def _grab_cbs(self, event: str) -> List[CallBack]:
        return self.cbsMap[event]

    def _sort_cbs(self, event: str):
        self.cbs.sort(key=lambda x: x.order, reverse=True)
        self.cbsMap[event].sort(key=lambda x: x.order, reverse=True)

    def add_cb(self, cb: CallBack) -> str:
        self.cbs.append(cb)
        for event in cb.events:
            if event not in self.cbsMap.keys():
                self.cbsMap[event] = [cb]
            else:
                self.cbsMap[event].append(cb)
                self._sort_cbs(event)
        return cb.name

    def add_cbs(self, cbs: List[CallBack]) -> List[str]:
        return [self.add_cb(cb) for cb in cbs]

    def remove_cb(self, cb_type: type):
        _f = lambda x: x.name != cb_type.__name__
        for event in self.cbsMap.keys():
            self.cbsMap[event] = list(
                filter(_f, self.cbsMap[event]))
        self.cbs = list(filter(_f, self.cbs))

    def remove_cbs(self, cb_types: List[type]):
        for cb_type in cb_types:
            self.remove_cb(cb_type)
