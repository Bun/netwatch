from json import load, dump


class FQueue(object):
    def __init__(self, qfile):
        self.qfile = qfile
        self._load()

    def _load(self):
        try:
            with open(self.qfile) as fp:
                self._entries = load(fp)

            return

        except IOError as e:
            if e.errno != 2:
                raise

        self._entries = []

    def empty(self):
        return not len(self._entries)

    def __iter__(self):
        return self._entries.__iter__()

    def add(self, entry):
        self._entries.append(entry)

    def extend(self, entry):
        self._entries.extend(entry)

    def peek(self):
        return self._entries[0]

    def get(self):
        self._entries.pop(0)

    def save(self):
        with open(self.qfile, 'w') as fp:
            dump(self._entries, fp, sort_keys=True)
