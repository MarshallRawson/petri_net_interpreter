#!/usr/bin/env python3
from os_features import InterProccessCommunication, Semaphore, OperatingSystem, Debug
from graph_entities import Place, Transition

class  UartDebug(Debug):
  def __init__(self, parent):
    super().__init__(parent)

  def call(self, give_string):
    s = '{\n'
    s += self.parent.transition_sem.wait()
    s += give_string + ';\n'
    s += self.get_debug_state()
    s += 'G8RTOS_Print(debug_state);\n'
    s += self.parent.transition_sem.signal()
    s += '}\n'
    s = s.replace('\\n', '\\n\\r')
    return s


class WifiDebug(Debug):
  def __init__(self, parent):
    super().__init__(parent)

  @staticmethod
  def prototype():
    return '#include <cc3100_usage.h>\n'

  @staticmethod
  def initialize():
    return 'initCC3100(Client);\n'

  def call(self, give_string):
    s = '{\n'
    s += self.parent.transition_sem.wait()
    s += give_string + ';\n'
    s += self.get_debug_state()
    s += 'SendData((unsigned char*)(&debug_state), HOST_IP_ADDR,' + str(self.string_len()) +' );\n'
    s += self.parent.transition_sem.signal()
    s += '}\n'
    return s


class SharedBuffer(InterProccessCommunication):
  def __init__(self, place):
    super().__init__(place)
    self.data_type_with_spaces = place.out_type
    self.data_type = place.out_type.replace(' ', '')
    if self.data_type == 'void':
      raise Exception('cannot create shared buffer with void datatype')

  @staticmethod
  def size():
    return '32'

  def prototype(self):
    ret = '#ifndef __SHARED_BUFFER_PROTOTYPES_' + self.data_type + str(self.size()) +'__\n'
    ret += '#define __SHARED_BUFFER_PROTOTYPES_' + self.data_type + str(self.size()) +'__\n' +\
      'SharedBuffer_Prototypes('+ self.data_type + ',' + str(self.size()) + ')\n' +\
      '#endif\n' +\
      'SharedBuffer_' + self.data_type + str(self.size()) + ' ' + self.name
    if self.data_type_with_spaces != self.data_type:
      ret += ';\n'
      ret += 'typedef ' + self.data_type_with_spaces + ' ' + self.data_type
    ret += ';\n'
    return ret

  def define(self):
    ret = '#ifndef __SHARED_BUFFER_DEFINITIONS_' + self.data_type + str(self.size()) + '__\n' +\
          '#define __SHARED_BUFFER_DEFINITIONS_' + self.data_type + str(self.size()) + '__\n' +\
          'SharedBuffer_Definitions(' + self.data_type + ', ' + str(self.size()) + ')\n' +\
          '#endif\n'
    return ret

  def enqueue(self, var_name):
    return self.name + '.Enqueue(&' + self.name + ', &' + var_name + ')'

  def take(self, val):
    return self.data_type + ' ' + val + ' = ' + self.dequeue()

  def dequeue(self):
    return self.name + '.Dequeue(&' + self.name + ');\n'

  def check_for_new_data(self):
    return self.name + '.NewData(&' + self.name + ')'

  def initialize(self):
    return 'SharedBuffer_Init_' + self.data_type + str(self.size()) + '(&' + self.name + ');\n'

  def get_size(self):
    return self.name + '.GetSize(&' + self.name + ')'

  def close(self):
    return ''

class G8rtosSem(Semaphore):
  def __init__(self, place):
    super().__init__(place)

  def prototype(self):
    return 'Semaphore_t ' + self.name + ';\n'

  def initialize(self, val=0):
    return 'G8RTOS_InitSemaphore(&' + self.name + ', ' + str(val) + ');\n'

  def get_value(self):
    return 'G8RTOS_GetSemaphoreValue(&' + self.name + ')'

  def signal(self):
    return 'G8RTOS_SignalSemaphore(&' + self.name + ');\n'

  def wait(self):
    return 'G8RTOS_WaitSemaphore(&' + self.name + ');\n'

  def take(self, val):
    return self.wait()

  def close(self):
    return ''

class G8rtosPlace(Place):
  def __init__(self, node, parent):
    super().__init__(node, parent)

  def c_header(self):
    h = '// ' + str(self.node) + '\n'
    h += self.output.prototype()
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
    s += 'bool called_transition = false;\n'
    if self.out_type != 'void':
      s += self.out_type + '* ' + self.name + ' = &ret;\n'
    for edge in self.outs.values():
      s += 'if (' + edge.condition + ')\n'
      s += '{\n'
      s += '  called_transition = true;\n'
      transition = self.parent.transitions[str(edge.edge[1])]
      s += '  ' + transition.name + '();\n'
      s += '}\n'
    s += 'if (!called_transition)\n'
    s += '{\n'
    s += '  G8RTOS_Print("' + self.name + ' failed to call any transitions and therfore '
    s += 'the program is in a blocked state it will not recover from\\n");\n'
    s += '}\n'
    s += self.parent.os.kill_self() + ';\n'
    s += '}\n\n'
    return s

class G8rtosTransition(Transition):
  def __init__(self, node, parent):
    super().__init__(node, parent)

  def c_header(self):
    header = '// ' + str(self.node) + '\n'
    header += 'void ' + str(self.node) + '();\n\n'
    return header

  def c_source(self):
    s = '// ' + str(self.node) + '\n'
    s += 'void ' + str(self.node) + '()\n'
    s += '{\n'
    s += '  ' + self.parent.transition_sem.wait()
    s += '  if('
    for edge in self.ins.values():
      place = self.parent.places[str(edge.edge[0])]
      s += place.output.is_ready() + '&&\n'
    s += '  true)\n'
    s += '  {\n'
    # check condition
    for edge in self.ins.values():
      place = self.parent.places[str(edge.edge[0])]
      s += '    ' + place.output.take(place.name + '_buf')
      if place.out_type != 'void':
        s += '    ' + place.out_type + '* ' + place.name + ' = &' + place.name + '_buf;\n'
    for edge in self.outs.values():
      place = self.parent.places[str(edge.edge[1])]
      s += '    ' + self.parent.os.add_thread(place, edge.var_name)
    s += '  }\n'
    s += self.parent.transition_sem.signal()
    s += '}\n\n'
    return s



class G8RTOS(OperatingSystem):
  def __init__(self, debug):
    super().__init__(SharedBuffer, G8rtosSem, G8rtosPlace, G8rtosTransition, debug)

  @staticmethod
  def includes():
    return '#include "G8RTOS.h"\n' + \
           '#include "BSP.h"\n'

  @staticmethod
  def kill_self():
    return 'G8RTOS_KillSelf()'

  @classmethod
  def add_thread(cls, place, param=''):
    if type(place) != str:
      name = str(place.node)
    else:
      name = place

    ret = 'G8RTOS_AddThread((void(*)())(' + name + '), '+ str(cls.priority())  + ', ' + \
          '"' + name + '",\n'

    if type(place) == str:
      ret += '0, 0)'
    elif param == '' or place.in_type.replace(' ', '') == 'void':
      ret += '0, 0)'
    else:
      ret += '(uint8_t*)(&' + param + '), sizeof(' + place.in_type + '))'
    ret += ';\n'
    return ret

  @staticmethod
  def priority():
    return '254'
