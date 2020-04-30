#!/usr/bin/env python3
from os_features import InterProccessCommunication, Semaphore, OperatingSystem, Debug

class  UartDebug(Debug):
  def __init__(self, parent):
    super().__init__(parent)

  def call(self, give_string):
    s = '{\n'
    s += self.parent.os.sem._wait(self.parent.transition_semaphore()) + ';\n'
    s += give_string + ';\n'
    s += self.get_debug_state()
    s += 'G8RTOS_Print(debug_state);\n'
    s += self.parent.os.sem._signal(self.parent.transition_semaphore()) + ';\n'
    s += '}\n'
    s = s.replace('\\n', '\\n\\r')
    return s


class WifiDebug(Debug):
  def __init__(self, parent):
    super().__init__(parent)

  @staticmethod
  def _prototype():
    return '#include <cc3100_usage.h>\n'

  @staticmethod
  def _initialize():
    return 'initCC3100(Client);\n'

  def call(self, give_string):
    s = '{\n'
    s += self.parent.os.sem._wait(self.parent.transition_semaphore()) + ';\n'
    s += give_string + ';\n'
    s += self.get_debug_state()
    s += 'SendData((unsigned char*)(&debug_state), HOST_IP_ADDR,' + str(self.string_len()) +' );\n'
    s += self.parent.os.sem._signal(self.parent.transition_semaphore()) + ';\n'
    s += '}\n'
    return s


class G8RTOS(OperatingSystem):
  def __init__(self, debug):
    super().__init__(SharedBuffer, G8rtosSem, debug)

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
    return ret

  @staticmethod
  def priority():
    return '254'



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
    ret = self._prototype(self.name, self.data_type, self.size())
    if self.data_type_with_spaces != self.data_type:
      ret += ';\n'
      ret += 'typedef ' + self.data_type_with_spaces + ' ' + self.data_type
    return ret

  @staticmethod
  def _prototype(name, data_type, size):
    ret = '#ifndef __SHARED_BUFFER_PROTOTYPES_' + data_type + str(size) +'__\n'
    ret += '#define __SHARED_BUFFER_PROTOTYPES_' + data_type + str(size) +'__\n' +\
      'SharedBuffer_Prototypes('+ data_type + ',' + str(size) + ')\n' +\
      '#endif\n' +\
      'SharedBuffer_' + data_type + str(size) + ' ' + name
    return ret

  def define(self):
    return self._define(self.data_type, self.size())

  @staticmethod
  def _define(data_type, size):
    ret = '#ifndef __SHARED_BUFFER_DEFINITIONS_' + data_type + str(size) + '__\n' +\
          '#define __SHARED_BUFFER_DEFINITIONS_' + data_type + str(size) + '__\n' +\
          'SharedBuffer_Definitions(' + data_type + ', ' + str(size) + ')\n' +\
          '#endif\n'
    return ret

  @staticmethod
  def _enqueue(name, var_name):
    return name + '.Enqueue(&' + name + ', &' + var_name + ')'

  def take(self, val):
    return self.data_type + ' ' + val + ' = ' + self.dequeue()


  @staticmethod
  def _dequeue(name):
    return name + '.Dequeue(&' + name + ')'

  @staticmethod
  def _check_for_new_data(name):
    return name + '.NewData(&' + name + ')'

  def initialize(self):
    return self._initialize(self.name, self.data_type, self.size())

  @staticmethod
  def _initialize(name, data_type, size):
    return 'SharedBuffer_Init_' + data_type + str(size) + '(&' + name + ')'

  @staticmethod
  def _peak(name):
    return name + '.Peak(&' + name + ')'

  @staticmethod
  def _get_size(name):
    return name + '.GetSize(&' + name + ')'


class G8rtosSem(Semaphore):
  def __init__(self, place):
    super().__init__(place)

  @staticmethod
  def _prototype(name):
    return 'Semaphore_t ' + name

  def initialize(self):
    return self._initialize(self.name, 0)

  @staticmethod
  def _initialize(name, val):
    return 'G8RTOS_InitSemaphore(&' + name + ', ' + str(val) + ')'

  @staticmethod
  def _get_value(name):
    return 'G8RTOS_GetSemaphoreValue(&' + name + ')'

  @staticmethod
  def _signal(name):
    return 'G8RTOS_SignalSemaphore(&' + name + ')'

  @staticmethod
  def _wait(name):
    return 'G8RTOS_WaitSemaphore(&' + name  + ')'

  @staticmethod
  def _decrement(name):
    return 'G8RTOS_DecrementSemaphore(&' + name  + ')'




