from collections import deque
from datetime import datetime, timedelta
from typing import TypeVar

_KT = TypeVar("_KT")
_VT = TypeVar("_VT")


class TmpStorage(dict):
    """
    Creates a repository for temporary storage of any objects (for example, keyboards that should
    save its state between calls to handlers).

    The repository behaves like an ordinary dictionary.
    When creating a repository, three basic parameters of the repository can be specified:
        - max_number_elements: int - maximum storage capacity
        - max_lifetime_sec: int - maximum retention time of the element
        - min_lifetime_sec: int - the minimum critical time of saving the element
    About min_lifetime_sec - used only as a signal parameter. At high load and large
    the number of created objects for temporary storage, their lifetime may be too low to ensure
    the desired functioning of the system (for example - a saved keyboard may exist for less time
    than is really necessary to go through the full cycle of its use by the user). In the event
    that the lifetime of the object upon deletion will be less than min_lifetime_sec - a warning is
    created in the logs, which signals the need to increase the size of the permissible one
    the number of objects in the repository or take other actions that will correct the situation.

    max_lifetime_sec - the time after which the element is considered not relevant and is not
    returned upon request (raise KeyError)
    max_number_elements - the maximum number of elements in the storage
    """

    def __init__(
        self,
        max_number_elements: int = 64,
        min_lifetime_sec: int = 900,
        max_lifetime_sec: int = 84600,
    ) -> None:
        self.max_number_elements = max_number_elements
        self.min_lifetime = timedelta(seconds=min_lifetime_sec)
        self.max_lifetime = timedelta(seconds=max_lifetime_sec)
        self._deque = deque("")
        self._time_creation = {}

    def __setitem__(self, __key: _KT, __value: _VT) -> None:
        """Checks for an element with the following key
        if there is:
            - overwrites the storage time of an element with the following key (self._time_creation)
            - removes the existing key from the queue (self._deque)
            - writes the key to the beginning of the queue (self._deque)
            - overwrites the value in the dictionary for this key with the new value
        if not:
            - records the time of entry into the repository of an element with the following key (self._time_creation)
            - writes the key to the beginning of the queue (self._deque)
            - records the meaning for this key in the dictionary
            - if the total length of the queue is greater than self.max_number_elements, then:
                - "picks up" (receives and removes) a key from the end of the queue
                - removes the element with the received key from the dictionary
                - reads the creation time for the received key. If its lifetime is less than self.min_lifetime,
                generates a warning in the log
                - removes the element for this key in self._time_creation
        """
        if __key in self._deque:
            self._deque.remove(__key)
        self._time_creation[__key] = datetime.now()
        self._deque.append(__key)
        if len(self._deque) > self.max_number_elements:
            key_for_del = self._deque.popleft()
            if datetime.now() - self._time_creation[key_for_del] < self.min_lifetime:
                print(
                    f"WARNING: in object {self} deleted element with key = {key_for_del}. \
                      The lifetime of this element is less than Wh. You may need to increase the storage size."
                )  # TODO -> in log
            self.__delitem__(key_for_del)
        return super().__setitem__(__key, __value)

    def __getitem__(self, __key: _KT) -> _VT:
        """Returns an element from the repository by its key if the element's lifetime is less than self.max_lifetime.

        - checks for the presence of a key and, if not, creates a KeyError exception
        - by key reads from self._time_creation the time of entering the element into the repository
        - if the lifetime of the element currently exceeds self.max_lifetime, then:
            - deletes by key
                - an element from the dictionary
                - the time of entering the element into the repository from self._time_creation
                - key from the queue
                - throws a KeyError exception with the appropriate message
        """
        try:
            res = super().__getitem__(__key)
            if datetime.now() - self._time_creation[__key] > self.max_lifetime:
                self.__delitem__(__key)
                raise KeyError(
                    f"the {res} object (key={__key}) has been removed from storage \
                               because the storage interval for the object has been exceeded."
                )
            return res
        except KeyError:
            print(f"The key {__key} is missing in the object {self}")

    def __delitem__(self, __key: _KT) -> None:
        """Removes an element from the dictionary and all accompanying elements:
        - checks for the presence of a key and, if not, creates a KeyError exception
        - the time of entering the element into the repository
        - key from the queue
        """
        try:
            super().__delitem__(__key)
            del self._time_creation[__key]
            self._deque.remove(__key)
        except KeyError:
            print(f"The key {__key} is missing in the object {self}")
            raise
        except ValueError:
            pass
