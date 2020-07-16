#!/usr/bin/env python3
from petri_net_interpreter.os_features \
    import InterProccessCommunication, Semaphore, OperatingSystem, Debug
from petri_net_interpreter.graph_entities import Place, Transition


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
            s += 'int ' + place.name + '_in_progress;\n'
            s += place.in_progress_sem.get_value(place.name + '_in_progress')
            s += 'int ' + place.name + '_finished;\n'
            s += place.output.get_status(place.name + '_finished')
        s += 'snprintf(debug_state, ' + str(self.string_len()) + ', "'
        for name in self.parent.places.keys():
            s += name + ' in progress: %d, finished: %d total: %d\\n'
        s += '\\n", '
        for place in self.parent.places.values():
            s += place.name + '_in_progress, '
            s += place.name + '_finished, '
            s += place.name + '_finished + ' + place.name + '_in_progress, '
        i = s.rfind(',')
        s = s[:i] + s[i + 1:]
        s += ');\n'
        return s

    def string_len(self):
        all_names = ''
        for name in self.parent.places.keys():
            all_names += name
        return len(all_names) * 48 + len(self.parent.places.keys()) * 6


class MessageQueue(InterProccessCommunication):
    def __init__(self, place, name=None):
        super().__init__(place, name)
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

    def prototype(self, type_prefix=''):
        ret = type_prefix + 'int ' + self.name + ';\n'
        ret += type_prefix + 'struct msqid_ds ' + self.buf
        return ret

    def enqueue(self, var_name):
        ret = 'if (-1 == msgsnd(' + self.name + ', &' + var_name + ',\n'
        ret += 'sizeof(' + self.data_type + ') + sizeof(long), 0))\n'
        ret += '{\n'
        ret += '  perror("' + self.name + ' sending ' + \
            var_name + ' failed");\n'
        ret += '  pthread_exit(NULL);\n'
        ret += '}\n'
        return ret

    def dequeue(self, var):
        ret = self.data_type + '* ' + var + ';\n'
        ret += 'struct ' + var + '_struct\n'
        ret += '{\n'
        ret += '  long type;\n'
        ret += '  ' + self.data_type + ' data;\n'
        ret += '} ' + var + '_buf;\n'
        ret += 'if(-1 == msgrcv(' + self.name + ', &' + var + '_buf,\n'
        ret += 'sizeof(' + self.data_type + ') + sizeof(long), 1,\n'
        ret += '0))\n'
        ret += '{\n'
        ret += '  perror("' + self.name + ' reciving ' + var + ' failed");\n'
        ret += '  pthread_exit(NULL);\n'
        ret += '}\n'
        ret += var + ' = ' + '&(' + var + '_buf.data);\n'
        return ret

    def get_stats(self):
        ret = 'if (-1 == msgctl(' + self.name + \
            ', IPC_STAT, ' + '&' + self.buf + '))\n'
        ret += '{\n'
        ret += '  perror("' + self.name + ' getting stats failed");\n'
        ret += '  pthread_exit(NULL);\n'
        ret += '}\n'
        return ret

    def set_stats(self):
        ret = 'if (-1 == msgctl(' + self.name + \
            ', IPC_SET, ' + '&' + self.buf + '))\n'
        ret += '{\n'
        ret += '  perror("' + self.name + ' setting stats failed");\n'
        ret += '  pthread_exit(NULL);\n'
        ret += '}\n'
        return ret

    def is_ready(self, var):
        ret = self.get_stats()
        ret += 'bool ' + var + ' = ' + self.check_for_new_data() + ';\n'
        return ret

    def check_for_new_data(self):
        ret = '(' + self.buf + '.msg_qnum > 0)'
        return ret

    def get_size(self, var):
        ret = self.get_stats()
        ret += var + ' = ' + self.buf + '.msg_qnum;\n'
        return ret

    def initialize(self, key_name=None):
        if key_name is None:
            key_name = self.name + '_key'
        ret = '{\n'
        ret += 'key_t ' + key_name + \
            ' = ftok("' + self.proj_file + '", proj_id++);\n'
        ret += self.name + \
            ' = msgget(' + key_name + ', 0600 | IPC_CREAT);\n'
        ret += 'if (' + key_name + ' == -1)\n'
        ret += '{\n'
        ret += '  perror("' + key_name + ' message queue creation failed");\n'
        ret += '  pthread_exit(NULL);\n'
        ret += '}\n'
        ret += self.get_stats()
        ret += self.buf + \
            '.msg_qbytes = sizeof(' + self.data_type + ') * ' + str(self.size()) + ';\n'
        ret += self.set_stats()
        ret += '}\n'
        return ret

    def close(self):
        ret = 'if (-1 == msgctl(' + self.name + ', IPC_RMID, NULL))\n'
        ret += '{\n'
        ret += '  perror("Failed to close ' + self.name + '");\n'
        ret += '}\n'
        return ret

    def change_name(self, new_name):
        self.previous_names.append((self.name, self.buf))
        self.name = new_name
        self.buf = new_name + '_buf'

    def revert_name(self):
        (self.name, self.buf) = self.previous_names.pop()


class Semaphore(Semaphore):
    def __init__(self, place, **kwargs):
        super().__init__(place, **kwargs)

    def get_status(self, var):
        ret = self.get_value(var)
        return ret

    def prototype(self, type_prefix=''):
        return type_prefix + 'sem_t ' + self.name

    def initialize(self, val=0):
        ret = 'if (-1 == sem_init(&' + self.name + ', 0, ' + str(val) + '))\n'
        ret += '{\n'
        ret += '  perror("' + self.name + \
            ' semaphore initialization failed");\n'
        ret += '  pthread_exit(NULL);\n'
        ret += '}\n'
        return ret

    def is_ready(self, var):
        ret = 'int ' + var + ';\n'
        ret += self.get_value(var)
        return ret

    def get_value(self, var):
        ret = 'if (-1 == sem_getvalue(&' + self.name + ', &' + var + '))\n'
        ret += '{\n'
        ret += '  perror("' + self.name + ' semaphore get value failed");\n'
        ret += '  pthread_exit(NULL);\n'
        ret += '}\n'
        return ret

    def signal(self):
        ret = 'if (-1 == sem_post(&' + self.name + '))\n'
        ret += '{\n'
        ret += '  perror("signaling ' + self.name + ' failed");\n'
        ret += '  pthread_exit(NULL);\n'
        ret += '}\n'
        return ret

    def wait(self):
        ret = 'if (-1 == sem_wait(&' + self.name + '))\n'
        ret += '{\n'
        ret += '  perror("waiting on ' + self.name + ' failed");\n'
        ret += '  pthread_exit(NULL);\n'
        ret += '}\n'
        return ret

    def close(self):
        ret = 'if (-1 == sem_close(&' + self.name + '))\n'
        ret += '{\n'
        ret += '  perror("Failed to close ' + self.name + '");\n'
        ret += '}\n'
        return ret


class Place(Place):
    def __init__(
            self,
            node,
            parent,
            in_copy_name=None,
            in_progress_name=None,
            **kwargs):
        super().__init__(node, parent, **kwargs)
        # we need this to signal the transition that we have copied the data and that it can kill self now
        # copying data is kinda the only way to solve this without dynamic
        # memory I think
        if self.in_type != 'void':
            if in_copy_name is None:
                self.in_data_copy_sem = parent.os.sem(
                    self, name=self.name + '_IN_DATA_COPY_SEMAPHORE')
            else:
                self.in_data_copy_sem = parent.os.sem(self, name=in_copy_name)
        if in_progress_name is None:
            self.in_progress_sem = parent.os.sem(
                self, name=self.name + '_IN_PROGRESS_SEMAPHORE')
        else:
            self.in_progress_sem = parent.os.sem(self,
                                                 name=in_progress_name)

    def initialize(self):
        ret = self.output.initialize()
        if self.in_type != 'void':
            ret += self.in_data_copy_sem.initialize()
        ret += self.in_progress_sem.initialize()
        return ret

    def close(self):
        ret = self.output.close()
        if hasattr(self, 'in_data_copy_sem'):
            ret += self.in_data_copy_sem.close()
        return ret

    def c_header(self, type_prefix=''):
        h = '// ' + str(self.node) + '\n'
        h += self.output.prototype(type_prefix) + ';\n'
        if self.in_type != 'void':
            h += self.in_data_copy_sem.prototype(type_prefix) + ';\n'
        h += self.in_progress_sem.prototype(type_prefix) + ';\n'
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
            s += 'memcpy(&' + in_data + \
                ', parg, sizeof(' + self.in_type + '));\n'
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
        s += self.parent.debug.call(self.output.give('ret') +
                                    self.in_progress_sem.wait())

        s += 'bool called_transition = false;\n'
        if self.out_type != 'void':
            s += self.out_type + '* ' + str(self.node) + ' = &ret.data;\n'
        for edge in self.outs.values():
            s += 'if (' + edge.condition + ')\n'
            s += '{\n'
            s += '  called_transition = true;\n'
            transition = self.parent.transitions[str(edge.edge[1])]
            s += '  ' + transition.name + '();\n'
            s += '}\n'
        s += 'if (!called_transition)\n'
        s += '{\n'
        s += '  perror("' + self.name + \
            ' failed to call any transitions and therfore '
        s += 'the program is in a blocked state it will not recover from");\n'
        s += '}\n'
        s += self.parent.os.kill_self() + ';\n'
        s += '}\n\n'
        return s


class Transition(Transition):
    def __init__(self, node, parent, name=None):
        super().__init__(node, parent, name=name)

    def c_header(self):
        header = '// ' + self.name + '\n'
        header += 'void ' + self.name + '();\n\n'
        return header

    def c_source(self):
        s = '// ' + self.name + '\n'
        s += 'void ' + self.name + '()\n'
        s += '{\n'
        s += '  ' + self.parent.transition_sem.wait()
        for edge in self.ins.values():
            place = self.parent.places[str(edge.edge[0])]
            s += place.output.is_ready(str(place.node) + '_is_ready')
        s += '  if('
        for edge in self.ins.values():
            place = self.parent.places[str(edge.edge[0])]
            s += '(' + str(place.node) + '_is_ready) &&\n'
        s += '  true)\n'
        s += '  {\n'
        for edge in self.ins.values():
            place = self.parent.places[str(edge.edge[0])]
            s += '    ' + place.output.take(str(place.node))
        for edge in self.outs.values():
            place = self.parent.places[str(edge.edge[1])]
            s += '    ' + place.in_progress_sem.signal()
            s += '    ' + \
                self.parent.os.add_thread(place, edge.var_name)
        s += '  }\n'
        for edge in self.outs.values():
            place = self.parent.places[str(edge.edge[1])]
            if hasattr(place, 'in_data_copy_sem'):
                s += place.in_data_copy_sem.wait()
        s += '  ' + self.parent.transition_sem.signal()
        s += '}\n\n'
        return s


class Linux(OperatingSystem):
    def __init__(self, proj_file,
                 message_queue=MessageQueue,
                 semaphore=Semaphore,
                 place=Place,
                 transition=Transition,
                 debug=Debug):
        super().__init__(
            message_queue,
            semaphore,
            place,
            transition,
            debug)
        self.proj_file = proj_file

    @staticmethod
    def includes():
        ret = '#define _GNU_SOURCE\n' + \
              '#include <stdbool.h>\n' +\
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
        ret = 'pthread_exit(NULL);\n'
        ret += 'return NULL'
        return ret

    @classmethod
    def add_thread(cls, place, param):
        if not isinstance(place, str):
            name = str(place.node)
            func_name = place.wrapper_name
        else:
            name = place
            func_name = place
        ret = '{\n'
        ret += 'pthread_t ' + name + '_pthread;\n'
        ret += 'if (0 != pthread_create(&' + name + \
            '_pthread, NULL, &' + func_name + ', '
        if param == 'void':
            ret += 'NULL'
        else:
            ret += '&' + param
        ret += '))\n'
        ret += '{\n'
        ret += '  perror("Failed to add thread: ' + name + '");\n'
        ret += '  pthread_exit(NULL);\n'
        ret += '}\n'
        ret += 'if (0 != pthread_setname_np(' + name + \
            '_pthread, "' + name[:15] + '"))\n'
        ret += '{\n'
        ret += '  perror("Failed to name thread: ' + name + '");\n'
        ret += '  pthread_exit(NULL);\n'
        ret += '}\n'
        ret += 'if (0 != pthread_detach(' + name + '_pthread))\n'
        ret += '{\n'
        ret += '  perror("Failed to detach thread: ' + name + '");\n'
        ret += '  pthread_exit(NULL);\n'
        ret += '}\n'
        ret += '}\n'
        return ret

    @staticmethod
    def initialize():
        return 'int proj_id = 0;\n'
