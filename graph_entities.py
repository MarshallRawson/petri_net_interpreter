#!/usr/bin/env python3
from abc import ABC, abstractmethod


class GraphEntity(ABC):
  def __init__(self, parent):
    self.parent = parent
    self.check_xlabel()

  @abstractmethod
  def check_xlabel(self):
    pass


class Node(GraphEntity):
  def __init__(self, node, parent):
    self.node = node
    self.ins = {}
    self.outs = {}
    super().__init__(parent)

  def add_out_edge(self, edge):
      self.outs[str(edge)] = edge

  def add_in_edge(self, edge):
      self.ins[str(edge)] = edge

  def __str__(self):
    ret = str(self.node) + '\n outs:'
    for v in self.outs.values():
      ret += '\n' + str(v)
    ret += '\n ins:'
    for v in self.ins.values():
      ret += '\n' + str(v)
    return ret

  def check_xlabel(self):
    if self.node.attr['xlabel'].count(self.parent.delim()) > 1:
      raise Exception('%s has multiple delimitors'%str(a))

  @abstractmethod
  def c_header(self):
    pass

  @abstractmethod
  def c_source(self):
    pass

  @staticmethod
  @abstractmethod
  def shape():
    pass


class Place(Node):
  def __init__(self, node, parent):
    super().__init__(node, parent)
    self.in_type = self.node.attr['xlabel'].split(self.parent.delim())[1].strip()
    self.out_type = self.node.attr['xlabel'].split(self.parent.delim())[0].strip()
    # if void out type, then use a sem as output instead of an ipc
    if self.out_type == 'void':
      self.output = self.parent.os.sem(self)
    else:
      self.output = self.parent.os.ipc(self)
    self.body_name = self.parent.os.place_body_name(self)

  def c_header(self):
    h = '// ' + str(self.node) + '\n'
    h += self.output.prototype() + ';\n'
    h += 'void ' + str(self.node) + '(' + self.in_type + ');\n'
    h += self.out_type + ' ' + self.body_name + '(' + self.in_type + ');\n'
    h += '\n'
    return h

  def c_source(self):
    s = '// ' + str(self.node) + '\n'
    #define our out incase it needs it
    s += self.output.define() + '\n'
    if self.in_type != 'void':
      s += 'void ' + str(self.node) + '(' + self.in_type + ' in_data)\n'
      in_data = 'in_data'
    else:
      s += 'void ' + str(self.node) + '()\n'
      in_data = ''
    s += '{\n'

    if self.out_type != 'void':
      s += self.out_type + ' ret = ' + self.body_name + '(' + in_data + ');\n'
    else:
      s += self.body_name + '(' + in_data + ');\n'
    s += self.parent.debug.call(self.output.give('ret'))
    for edge in self.outs.values():
      transition = self.parent.transitions[str(edge.edge[1])]
      s += str(transition.node) + '();\n'
    s += self.parent.os.kill_self() + ';\n'
    s += '}\n\n'
    return s

  def __str__(self):
    ret = super().__str__() + '\n in_type:\n' + self.in_type + \
      '\n out_type:\n' + self.out_type
    ret += '\nOutput : ' + str(self.output) + '\n'
    return ret

  def check_xlabel(self):
    super().check_xlabel()
    if self.node.attr['xlabel'] is None or self.node.attr['xlabel'] == '':
      raise Exception('Place: %s has no specified in / out type. \n\
      xlabel format for places is: out_type; in_type'%str(self.node))

  @staticmethod
  def shape():
    return 'oval'



class Transition(Node):
  def __init__(self, node, parent):
    super().__init__(node, parent)
    self.condition_needs = ' '.join(node.attr['xlabel'].split(self.parent.delim())[0].split())
    self.condition = node.attr['xlabel'].split(self.parent.delim())[1]

  def c_header(self):
    header = '// ' + str(self.node) + '\n'
    header += 'void ' + str(self.node) + '();\n\n'
    return header

  def c_source(self):
    s = '// ' + str(self.node) + '\n'
    s += 'void ' + str(self.node) + '()\n'
    s += '{\n'
    s += '  ' + self.parent.os.sem._wait(self.parent.transition_semaphore()) + ';\n'
    s += '  if('
    for edge in self.ins.values():
      place = self.parent.places[str(edge.edge[0])]
      s += place.output.is_ready() + '&&\n'
    s += '  true)\n'
    s += '  {\n'
    # check condition
    for need in self.condition_needs:
      place = self.parent.places[need]
      s += '    ' + place.out_type + ' ' +  need + ' = ' + place.output.peak() + ';\n'
    s += '    if('
    s += self.condition + ')\n'
    s += '    {\n'
    for edge in self.ins.values():
      place = self.parent.places[str(edge.edge[0])]
      s += '      ' + place.output.take(str(place.node)) + ';\n'
    for edge in self.outs.values():
      place = self.parent.places[str(edge.edge[1])]
      s += '      ' + self.parent.os.add_thread(place, edge.var_name) + ';\n'
    s += '    }\n'
    s += '  }\n'
    s += self.parent.os.sem._signal(self.parent.transition_semaphore()) + ';\n'
    s += '}\n\n'
    return s

  def __str__(self):
    return super().__str__() + '\n Condition:\n' + self.condition + '\n'

  def check_xlabel(self):
    super().check_xlabel()
    return

  @staticmethod
  def shape():
    return 'box'


class Edge(GraphEntity):
  def __init__(self, edge, parent):
    self.edge = edge
    super().__init__(parent)
    self.var_name = edge.attr['xlabel']

  def check_xlabel(self):
    if self.edge[1].attr['shape'] == self.parent.transition.shape():
      return
    elif self.edge.attr['xlabel'] is None or self.edge.attr['xlabel'] == '':
      #TODO check to make sure the variable name makes sense
      raise Exception('Edge: %s must have a defined variable name to pass on'%str(self.edge))

  def check(self):
    # error on unsupported shapes
    shapes = [self.edge[i].attr['shape'] for i in range(2)]
    for i in shapes:
      if i != self.parent.place.shape() and i != self.parent.transition.shape():
        raise Exception("%s: '%s' is not a defined shape in this configuration.\n\
                         Current shapes are: %s"%(self.edge, i,
                         str({'place': self.parent.place.shape(),
                              'transition': self.parent.transition.shape()})))

    # make sure graph is bipartite
    if shapes[0] == shapes[1]:
      raise Exception("%s: Edge cannot connect two alike nodes"%str(self.edge))

  def __str__(self):
    ret = str(self.edge) + '\n' + self.var_name
    return ret

