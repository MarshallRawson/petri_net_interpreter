#!/usr/bin/env python3
from abc import ABC, abstractmethod
from petri_net_interpreter.graph_entities import Place, Transition


class OsFeature(ABC):
    def __init__(self, parent):
        self.parent = parent

    @abstractmethod
    def prototype(self):
        pass

    def define(self):
        return ''

    @abstractmethod
    def initialize(self):
        pass


class Debug(OsFeature):
    def __init__(self, parent):
        super().__init__(parent)

    def string_len(self):
        all_names = ''
        for name in self.parent.places.keys():
            all_names += name
        return len(all_names) + len(self.parent.places.keys()) * 6

    def get_debug_state(self):
        s = '// Get Debug state\n'
        s += 'char debug_state[' + str(self.string_len()) + '];\n'
        s += 'snprintf(debug_state, ' + str(self.string_len()) + ', "'
        for name in self.parent.places.keys():
            s += name + ': %d\\n'
        s += '\\n", \n'
        for place in self.parent.places.values():
            s += place.output.get_status() + ',\n'
        i = s.rfind(',')
        s = s[:i] + s[i + 1:]
        s += ');\n'
        return s

    def prototype(self):
        return ''

    def initialize(self):
        return ''

    def call(self, give_string):
        return give_string


class ProccessOutput(OsFeature):
    def __init__(self, parent, name):
        super().__init__(parent)
        self.name = name
        self.previous_names = []

    @abstractmethod
    def is_ready(self):
        pass

    @abstractmethod
    def take(self, val):
        pass

    @abstractmethod
    def give(self, val):
        pass

    @abstractmethod
    def close(self):
        pass

    def change_name(self, new_name):
        self.previous_names.append(self.name)
        self.name = new_name

    def revert_name(self):
        self.name = self.previous_names.pop()


class InterProccessCommunication(ProccessOutput):
    def __init__(self, place, name=None):
        if name is None:
            name = place.name + '_OUT_IPC'
        super().__init__(place, name)

    def give(self, val):
        return self.enqueue(val)

    def take(self, val):
        return self.dequeue(val)

    @abstractmethod
    def enqueue(self, val):
        pass

    @abstractmethod
    def dequeue(self, val):
        pass

    def is_ready(self):
        return self.check_for_new_data()

    @abstractmethod
    def check_for_new_data(self):
        pass

    @abstractmethod
    def get_size(self):
        pass

    def get_status(self):
        return self.get_size()

    def __str__(self):
        return self.name


class Semaphore(ProccessOutput):
    def __init__(self, place, name=None):
        if name is None:
            name = place.name + '_OUT_SEMAPHORE'
        super().__init__(place, name)

    def give(self, val):
        return self.signal()

    @abstractmethod
    def signal(self):
        pass

    def take(self, val):
        return self.wait()

    @abstractmethod
    def wait(self):
        pass

    @abstractmethod
    def get_value(self):
        pass

    def get_status(self):
        return self.get_value()

    def is_ready(self):
        return '(' + self.get_value() + ' > 0)'

    def __str__(self):
        return self.name


class OperatingSystem(ABC):
    def __init__(self, ipc, sem, place, transition, debug=Debug):
        self.ipc = ipc
        if not issubclass(ipc, InterProccessCommunication):
            raise Exception('ipc must inherit from InterProccessCommunication')
        self.sem = sem
        if not issubclass(sem, Semaphore):
            raise Exception('sem must inherit from Semaphore')
        self.place = place
        if not issubclass(place, Place):
            raise Exception('place must inherit from Place')
        self.transition = transition
        if not issubclass(transition, Transition):
            raise Exception('transition must inherit from Transition')
        self.debug = debug
        if not issubclass(debug, Debug):
            raise Exception('debug must inherit from Debug')

    @staticmethod
    def place_body_name(place):
        return place.name + '_body'

    @staticmethod
    def place_wrapper_name(place):
        return place.name + '_wrapper'

    def header_file_start(self, net):
        return "#pragma once"

    def header_file_end(self, net):
        return ''

    def source_file_start(self, net):
        return ''

    def source_file_end(self, net):
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
    def add_thread(cls, place, param):
        pass

    def initialize(self):
        return ''
