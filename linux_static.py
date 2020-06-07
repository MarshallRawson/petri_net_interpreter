#!/usr/bin/env python3
from os_features import InterProccessCommunication, Semaphore, OperatingSystem, Debug
from graph_entities import Place, Transition

class PrintDebug(Debug):
  def __init__(self, parent):
    super().__init__(parent)

  def call(self, give_string):
    s = '{\n'
    s += self.parent.transition_sem.wait()
    s += give_string
    s += self.get_debug_state()
    s += 'printf("%s", debug_state);\n'
    s += self.parent.transition_sem.signal()
    s += '}\n'
    return s

  def get_debug_state(self):
    s = '// Get Debug state\n'
    s += 'char debug_state[' + str(self.string_len()) + '];\n'
    for place in self.parent.places.values():
      s += 'int ' + place.name + ';\n'
      s += place.output.get_status(place.name)
    s += 'snprintf(debug_state, ' + str(self.string_len())+ ', "'
    for name in self.parent.places.keys():
      s += name + ': %d\\n'
    s += '\\n", '
    for place in self.parent.places.values():
      s += place.name + ', '
    i = s.rfind(',')
    s = s[:i] + s[i+1:]
    s += ');\n'
    return s


class MessageQueue(InterProccessCommunication):
  def __init__(self, place):
    super().__init__(place)
    self.proj_file = place.parent.os.proj_file
    self.data_type = place.out_type
    self.buf = self.name + '_buf'
    if self.data_type == 'void':
      raise Exception('cannot create message queue with void data type')

  def get_status(self, var):
    return self.get_size(var)

  @staticmethod
  def size():
    return 32

  def prototype(self):
    ret =  'int ' + self.name + ';\n'
    ret += 'struct msqid_ds ' + self.buf
    return ret

  def enqueue(self, var_name):
    ret =  'if (-1 == msgsnd(' + self.name + ', &' + var_name + ',\n'
    ret += 'sizeof(' + self.data_type + ') + sizeof(long), 0))\n'
    ret += '{\n'
    ret += '  perror("' + self.name + ' sending ' + var_name + ' failed\\n");\n'
    ret += '  pthread_exit(NULL);\n'
    ret += '}\n'
    return ret

  def dequeue(self, var):
    ret =  self.data_type + '* ' + var + ';\n'
    ret += 'struct ' + var + '_struct\n'
    ret += '{\n'
    ret += '  long type;\n'
    ret += '  ' + self.data_type + ' data;\n'
    ret += '} ' + var + '_buf;\n'
    ret += 'if(-1 == msgrcv(' + self.name + ', &' + var + '_buf,\n'
    ret += 'sizeof(' + self.data_type + ') + sizeof(long), 1,\n'
    ret += '0))\n'
    ret += '{\n'
    ret += '  perror("' + self.name + ' reciving ' + var + ' failed\\n");\n'
    ret += '  pthread_exit(NULL);\n'
    ret += '}\n'
    ret += var + ' = ' + '&(' + var + '_buf.data);\n'
    return ret

  def get_stats(self):
    ret =  'if (-1 == msgctl(' + self.name + ', IPC_STAT, ' + '&' + self.buf + '))\n'
    ret += '{\n'
    ret += '  perror("' + self.name + ' getting stats failed\\n");\n'
    ret += '  pthread_exit(NULL);\n'
    ret += '}\n'
    return ret

  def set_stats(self):
    ret =  'if (-1 == msgctl(' + self.name + ', IPC_SET, ' + '&' + self.buf + '))\n'
    ret += '{\n'
    ret += '  perror("' + self.name + ' setting stats failed\\n");\n'
    ret += '  pthread_exit(NULL);\n'
    ret += '}\n'
    return ret

  def is_ready(self, var):
    ret =  self.get_stats()
    ret += 'bool ' + var + ' = ' + self.check_for_new_data() + ';\n'
    return ret

  def check_for_new_data(self):
    ret = '(' + self.buf + '.msg_qnum > 0)'
    return ret

  def get_size(self, var):
    ret =  self.get_stats()
    ret += var + ' = ' + self.buf + '.msg_qnum;\n'
    return ret

  def initialize(self):
    ret = '{\n'
    ret += 'key_t ' + self.name + '_key = ftok("' + self.proj_file + '", proj_id++);\n'
    ret += self.name + ' = msgget(' + self.name + '_key, 0600 | IPC_CREAT);\n'
    ret += 'if (' + self.name + ' == -1)\n'
    ret += '{\n'
    ret += '  perror("' + self.name + ' message queue creation failed\\n");\n'
    ret += '  pthread_exit(NULL);\n'
    ret += '}\n'
    ret += self.get_stats()
    ret += self.buf + '.msg_qbytes = sizeof(' + self.data_type + ') * ' + str(self.size()) + ';\n'
    ret += self.set_stats()
    ret += '}\n'
    return ret


class LinuxSem(Semaphore):
  def __init__(self, place, **kwargs):
    super().__init__(place, **kwargs)

  def get_status(self, var):
    ret = self.get_value(var)
    return ret

  def prototype(self):
    return 'sem_t ' + self.name

  def initialize(self, val=0):
    ret =  'if (-1 == sem_init(&' + self.name + ', 0, ' + str(val) + '))\n'
    ret += '{\n'
    ret += '  perror("' + self.name + ' semaphore initialization failed\\n");\n'
    ret += '  pthread_exit(NULL);\n'
    ret += '}\n'
    return ret

  def is_ready(self, var):
    ret = 'int ' + var + ';\n'
    ret += self.get_value(var)
    return ret

  def get_value(self, var):
    ret =  'if (-1 == sem_getvalue(&' + self.name + ', &' + var + '))\n'
    ret += '{\n'
    ret += '  perror("' + self.name + ' semaphore get value failed\\n");\n'
    ret += '  pthread_exit(NULL);\n'
    ret += '}\n'
    return ret

  def signal(self):
    ret =  'if (-1 == sem_post(&' + self.name + '))\n'
    ret += '{\n'
    ret += '  perror("signaling ' + self.name + ' failed\\n");\n'
    ret += '  pthread_exit(NULL);\n'
    ret += '}\n'
    return ret

  def wait(self):
    ret =  'if (-1 == sem_wait(&' + self.name  + '))\n'
    ret += '{\n'
    ret += '  perror("waiting on ' + self.name + ' failed\\n");\n'
    ret += '  pthread_exit(NULL);\n'
    ret += '}\n'
    return ret


class LinuxStaticPlace(Place):
  def __init__(self, node, parent):
    super().__init__(node, parent)
    # we need this to signal the transition that we have copied the data and that it can kill self now
    # copying data is kinda the only way to solve this without dynamic memory I think
    if self.in_type != 'void':
      self.in_data_copy_sem = LinuxSem(self, suffix='_IN_DATA_COPY_SEMAPHORE')

  def initialize(self):
    ret =  self.output.initialize()
    if self.in_type != 'void':
      ret += self.in_data_copy_sem.initialize()
    return ret

  def c_header(self):
    h = '// ' + str(self.node) + '\n'
    h += self.output.prototype() + ';\n'
    if self.in_type != 'void':
      h += self.in_data_copy_sem.prototype() + ';\n'
    h += 'void* ' + self.wrapper_name + '(void* parg);\n'
    h += self.out_type + ' ' + self.body_name + '(' + self.in_type + ');\n'
    h += '\n'
    return h

  def c_source(self):
    s = '// ' + self.name + '\n'
    # define our out incase it needs it
    s += self.output.define() + '\n'
    s += 'void* ' + self.wrapper_name + '(void* parg)\n'
    if self.in_type != 'void':
      in_data = 'in_data'
    else:
      in_data = ''

    s += '{\n'
    if self.in_type != 'void':
      s += self.in_type + ' ' + in_data + ';\n'
      s += 'memcpy(&' + in_data + ', parg, sizeof(' + self.in_type + '));\n'
      s += self.in_data_copy_sem.signal()

    if self.out_type != 'void':
      s += 'struct ret_buf\n'
      s += '{\n'
      s += '  long type;\n'
      s += '  ' + self.out_type + ' data;\n'
      s += '} ret;\n'
      s += 'ret.type = 1;\n'
      s += 'ret.data = ' + self.body_name + '(' + in_data + ');\n'
    else:
      s += self.body_name + '(' + in_data + ');\n'
    s += self.parent.debug.call(self.output.give('ret'))
    s += 'bool called_transition = false;\n'
    if self.out_type != 'void':
      s += self.out_type + '* ' + self.name + ' = &ret.data;\n'
    for edge in self.outs.values():
      s += 'if (' + edge.condition + ')\n'
      s += '{\n'
      s += '  called_transition = true;\n'
      transition = self.parent.transitions[str(edge.edge[1])]
      s += '  ' + transition.name + '();\n'
      s += '}\n'
    s += 'if (!called_transition)\n'
    s += '{\n'
    s += '  perror("' + self.name + ' failed to call any transitions and therfore '
    s += 'the program is in a blocked state it will not recover from\\n");\n'
    s += '}\n'
    s += self.parent.os.kill_self() + ';\n'
    s += '}\n\n'
    return s


class LinuxStaticTransition(Transition):
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
    for edge in self.ins.values():
      place = self.parent.places[str(edge.edge[0])]
      s += place.output.is_ready(str(place.node) + '_is_ready')
    s += '  if('
    for edge in self.ins.values():
      place = self.parent.places[str(edge.edge[0])]
      s += '(' + str(place.node) + '_is_ready > 0) &&\n'
    s += '  true)\n'
    s += '  {\n'
    for edge in self.ins.values():
      place = self.parent.places[str(edge.edge[0])]
      s += '    ' + place.output.take(str(place.node))
    for edge in self.outs.values():
      place = self.parent.places[str(edge.edge[1])]
      s += '    ' + self.parent.os.add_thread(place.wrapper_name, edge.var_name)
    s += '  }\n'
    s += '  ' + self.parent.transition_sem.signal()
    for edge in self.outs.values():
      place = self.parent.places[str(edge.edge[1])]
      if hasattr(place, 'in_data_copy_sem'):
        s += place.in_data_copy_sem.wait()
    s += '}\n\n'
    return s


class LinuxStatic(OperatingSystem):
  def __init__(self, proj_file, debug=Debug):
    super().__init__(MessageQueue, LinuxSem, LinuxStaticPlace, LinuxStaticTransition, debug)
    self.proj_file = proj_file

  @staticmethod
  def includes():
    ret = '#include <stdbool.h>\n' +\
          '#include <string.h>\n' +\
          '#include <pthread.h>\n' +\
          '#include <sys/types.h>\n' +\
          '#include <sys/ipc.h>\n' +\
          '#include <sys/msg.h>\n' +\
          '#include <stdio.h>\n' +\
          '#include <semaphore.h>\n' +\
          '#include <unistd.h>\n'
    return ret

  @staticmethod
  def kill_self():
    ret =  'pthread_exit(NULL);\n'
    ret += 'return NULL'
    return ret

  @classmethod
  def add_thread(cls, place, param):
    if type(place) != str:
      name = str(place.node)
    else:
      name = place
    ret =  '{\n'
    ret += 'pthread_t ' + name + '_pthread;\n'
    ret += 'pthread_create(&' + name + '_pthread, NULL, &' + place + ', '
    if param == 'void':
      ret += 'NULL'
    else:
      ret += '&' + param
    ret += ');\n'
    ret += '}\n'
    return ret

  @staticmethod
  def initialize():
    return 'int proj_id = 0;\n'
