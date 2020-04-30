#!/usr/bin/env python3
from abc import ABC, abstractmethod


class OsFeature(ABC):
  def __init__(self, parent):
    self.parent = parent

  @staticmethod
  @abstractmethod
  def _prototype(name):
    pass

  def prototype(self):
    return self._prototype(self.name)

  @staticmethod
  def _define(name):
    return ''

  def define(self):
    return self._define(self.name)

  @staticmethod
  @abstractmethod
  def _initialize(name):
    pass

  def initialize(self):
    return self._initialize(self.name)


class Debug(OsFeature):
  def __init__(self, parent):
    super().__init__(parent)

  def string_len(self):
    all_names = ''
    for name in self.parent.places.keys():
      all_names += name
    return len(all_names) + len(self.parent.places.keys())*6

  def get_debug_state(self):

    s = '// Get Debug state\n'
    s += 'char debug_state[' + str(self.string_len()) + '];\n'
    s += 'snprintf(debug_state, ' + str(self.string_len())+ ', "'
    for name in self.parent.places.keys():
      s += name + ': %d\\n'
    s += '\\n", \n'
    for place in self.parent.places.values():
      s += place.output.get_status() + ',\n'
    i = s.rfind(',')
    s = s[:i] + s[i+1:]
    s += ');\n'
    return s

  @staticmethod
  def _prototype():
    return ''

  @staticmethod
  def _initialize():
    return ''

  def call(self, give_string):
    return give_string + ';\n'

  @staticmethod
  def _define():
    return ''


class ProccessOutput(OsFeature):
  def __init__(self, parent):
    super().__init__(parent)

  @abstractmethod
  def get_status(self):
    pass

  @abstractmethod
  def is_ready(self):
    pass

  @abstractmethod
  def take(self, val):
    pass

  @abstractmethod
  def give(self, val):
    pass


class InterProccessCommunication(ProccessOutput):
  def __init__(self, place):
    super().__init__(place)
    self.name = str(place.node) + '_OUT_IPC'

  def give(self, val):
    return self.enqueue(val)

  @staticmethod
  @abstractmethod
  def _enqueue(name, val):
    pass

  def enqueue(self, val):
    return self._enqueue(self.name, val)

  @staticmethod
  @abstractmethod
  def _dequeue(name):
    pass

  def dequeue(self):
    return self._dequeue(self.name)

  def is_ready(self):
    return self.check_for_new_data()

  @staticmethod
  @abstractmethod
  def _check_for_new_data(name):
    pass

  def check_for_new_data(self):
    return self._check_for_new_data(self.name)

  @staticmethod
  @abstractmethod
  def _peak(name):
    pass

  def peak(self):
    return self._peak(self.name)

  @staticmethod
  @abstractmethod
  def _get_size(name):
    pass

  def get_size(self):
    return self._get_size(self.name)

  def get_status(self):
    return self.get_size()

  def __str__(self):
    return self.name


class Semaphore(ProccessOutput):
  def __init__(self, place):
    super().__init__(place)
    self.name = str(place.node) + '_OUT_SEMAPHORE'

  def prototype(self):
    return self._prototype(self.name)

  def give(self, val):
    return self.signal()

  @staticmethod
  @abstractmethod
  def _signal(name):
    pass

  def signal(self):
    return self._signal(self.name)

  def take(self, val):
    return self.decrement()

  @staticmethod
  @abstractmethod
  def _wait(name):
    pass

  def wait(self):
    return self._wait(self.name)

  @staticmethod
  @abstractmethod
  def _get_value(name):
    pass

  def get_value(self):
    return self._get_value(self.name)

  def get_status(self):
    return self.get_value()

  def is_ready(self):
    return '(' + self.get_value() + ' > 0)'

  @staticmethod
  @abstractmethod
  def _decrement(name):
    pass

  def decrement(self):
    return self._decrement(self.name)

  def __str__(self):
    return self.name


class OperatingSystem(ABC):
  def __init__(self, ipc, sem, debug=Debug):
    self.ipc = ipc
    if not issubclass(ipc, InterProccessCommunication):
      raise Exception('ipc must inherit from InterProccessCommunication')
    self.sem = sem
    if not issubclass(sem, Semaphore):
      raise Exception('sem must inherit from Semaphore')
    self.debug = debug
    if not issubclass(debug, Debug):
      raise Exception('debug must inherit from Debug')

  @staticmethod
  def place_body_name(place):
    return str(place.node) + '_body'

  @staticmethod
  def header_start():
    return "#pragma once"

  @staticmethod
  def header_file_end():
    return ''

  @staticmethod
  @abstractmethod
  def includes():
    pass

  @staticmethod
  @abstractmethod
  def kill_self():
    pass

  @classmethod
  @abstractmethod
  def add_thread(place, param):
    pass


