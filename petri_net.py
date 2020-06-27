#!/usr/bin/env python3
import pygraphviz as pgv
import pydot
from graph_entities import Edge
from os_features import OperatingSystem
from graph_entities import Place, Transition
from state_graph import StateGraph


class DummyPlace:
  def __init__(self, name):
    self.node = name
    self.name = name


class PetriNet(object):
  def __init__(self, dot_file, header_file, source_file, types_file, os):
    self.header_file = header_file
    self.source_file = source_file
    self.types_file = types_file
    dot = pydot.graph_from_dot_file(dot_file)
    if len(dot) > 1:
      raise Exception('multiple graphs are not supported')
    dot = str(dot[0])
    self.net = pgv.AGraph(dot)

    if not issubclass(type(os), OperatingSystem):
      raise Exception('os must inherit from OperatingSystem')
    self.os = os

    if not issubclass(os.place, Place):
      raise Exception('place must inherit from Place')
    self.place = os.place

    if not issubclass(os.transition, Transition):
      raise Exception('transition must inherit from Transition')
    self.transition = os.transition

    self.debug = self.os.debug(self)

    self.transitions = {}
    self.places = {}
    self.parse_graph()

    # needed for generating C code
    dummy_place = DummyPlace(self.transition_semaphore())
    self.transition_sem = self.os.sem(dummy_place, suffix='')

  def parse_graph(self):
    #TODO: check for parallel edges
    edges = []
    for i in self.net.edges():
      edges.append(Edge(i, self))

    for i in edges:
      # get transition outs and place ins
      if i.edge[0].attr['shape'] == self.transition.shape() and \
         i.edge[1].attr['shape'] == self.place.shape():
        node = i.edge[0]
        # if we have never seen this transition before add it
        if str(node) not in self.transitions.keys():
          self.transitions[str(node)] = self.transition(node, self)
        self.transitions[str(node)].add_out_edge(i)

        # get places outs
        node = i.edge[1]
        # if we have never seen this place before, add it
        if str(node) not in self.places.keys():
          self.places[str(node)] = self.place(node, self)
        self.places[str(node)].add_in_edge(i)

      # get transition ins and place outs
      if i.edge[1].attr['shape'] == self.transition.shape() and \
         i.edge[0].attr['shape'] == self.place.shape():
        # transition ins
        node = i.edge[1]
        # if we have never seen this transition before, add it
        if str(node) not in self.transitions.keys():
          self.transitions[str(node)] = self.transition(node, self)
        self.transitions[str(node)].add_in_edge(i)

        # get places outs
        node = i.edge[0]
        # if we have never seen this place before, add it
        if str(node) not in self.places.keys():
          self.places[str(node)] = self.place(node, self)
        self.places[str(node)].add_out_edge(i)

    self.state_graph = StateGraph(self)


  def __str__(self):
    ret = 'Petri Net:\n' + 'Transitions:' + '\n'
    for i in self.transitions.values():
      ret += '  ' + str(i) + '\n'
    ret += 'Places:\n'
    for i in self.places.values():
      ret += '  ' + str(i) + '\n'
    return ret

  def c_code(self):
    # make header
    header = self.os.header_start() + '\n'
    header += self.os.includes() + '\n'
    header += '#include "' + self.types_file + '"\n'
    header += '// Places:\n'
    for place in self.places.values():
      header += place.c_header()

    header += '// Transitions:\n'
    header += self.transition_sem.prototype() + ';\n'
    for transition in self.transitions.values():
      header += transition.c_header()

    header += '\n// Start Thread\n'
    header += 'void* ' + self.start_thread()  + '();\n'

    header += '\n// Petri Net Init:\n'
    header += 'void ' + self.init_function() + '();\n'

    header += '\n//Petri Net Close:\n'
    header += 'void ' + self.close_function() + '();\n'

    header += self.debug.prototype()
    header += self.os.header_file_end() + '\n'

    # make source
    source = ''
    source = self.os.includes() + '\n'
    source += '#include "' + self.header_file.split('/')[-1] + '"\n'
    source += '// Places:\n'
    for place in self.places.values():
      source += place.c_source()

    source += '// Transitions:\n'
    for v in self.transitions.values():
      source += v.c_source()

    source += '// Start Thread\n'
    source += 'void* ' + self.start_thread()  + '()\n'
    source += '{\n'
    source += self.transition0() + '();\n'
    source += self.os.kill_self() + ';\n'
    source += 'return 0;\n'
    source += '}\n\n'

    source += self.debug.define()

    source += '//Petri Net Init:\n'
    source += 'void ' + self.init_function() + '()\n'
    source += '{\n'
    source += self.os.initialize()
    source += self.debug.initialize()
    source += self.transition_sem.initialize(1)
    for place in self.places.values():
      source += place.initialize()
    source += self.os.add_thread(self.start_thread(), 'void')
    source += '}\n'

    source += '//Petri Net Close:\n'
    source += 'void ' + self.close_function() + '()\n'
    source += '{\n'
    for place in self.places.values():
      source += place.close()
    source += self.transition_sem.close()
    source += '}\n'
    return header, source

  def to_files(self):
    header, source = self.c_code()
    h = open(self.header_file, 'w')
    h.write(header)
    h.close()
    s = open(self.source_file, 'w')
    s.write(source)
    s.close()

  @staticmethod
  def transition0():
    return 'transition_0'

  @staticmethod
  def delim():
    return ';'

  @staticmethod
  def transition_semaphore():
    return 'PETRI_TRANSITION_SEMAPHORE'

  @staticmethod
  def init_function():
    return 'PetriNet_Init'

  @staticmethod
  def start_thread():
    return 'PetriNet_StartThread'

  @staticmethod
  def close_function():
    return 'PetriNet_Close'

  @staticmethod
  def max_tokens():
    return 32
