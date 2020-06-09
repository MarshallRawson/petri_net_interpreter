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
    self.name = str(node)
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
    self.wrapper_name = self.parent.os.place_wrapper_name(self)

  def initialize(self):
    return self.output.initialize()

  def close(self):
    return self.output.close()

  @abstractmethod
  def c_header(self):
    pass

  @abstractmethod
  def c_source(self):
    pass

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

  @abstractmethod
  def c_header(self):
    pass

  @abstractmethod
  def c_source(self):
    pass

  @staticmethod
  def shape():
    return 'box'


class Edge(GraphEntity):
  def __init__(self, edge, parent):
    self.edge = edge
    super().__init__(parent)
    if self.edge[0].attr['shape'] == self.parent.place.shape():
      self.condition = edge.attr['xlabel']
      if self.condition == '':
        self.condition = 'true'
    elif self.edge[1].attr['shape'] == self.parent.place.shape():
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
    ret = str(self.edge) + '\n'
    if hasattr(self, 'var_name'):
      ret += 'Moves: ' + self.var_name + '\n'
    elif hasattr(self, 'condition'):
      ret += 'Only fires when ' + self.condition + '\n'
    else:
      ret += 'Oops, this edge is broke'
    return ret

