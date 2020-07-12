#!/usr/bin/env python3
from petri_net_interpreter import linux_c, os_features, petri_net
from functools import partial


class PrintDebug(linux_c.PrintDebug):
    def __init__(self, parent):
        super().__init__(parent)

    def call(self, give_string):
        s = '{\n'
        s += self.parent.transition_sem.wait()
        s += give_string
        s += self.get_debug_state()
        s += 'std::cout << debug_state;\n'
        s += self.parent.transition_sem.signal()
        s += '}\n'
        return s


class MessageQueue(linux_c.MessageQueue):
    def __init__(self, place, name):
        super().__init__(place, name)


class Semaphore(linux_c.Semaphore):
    def __init__(self, place, name, **kwargs):
        super().__init__(place, name=name, **kwargs)


class Place(linux_c.Place):
    def __init__(self, node, parent):
        in_copy_name = 'IN_DATA_COPY_SEMAPHORE'
        in_progress_name = 'IN_PROGRESS_SEMAPHORE'
        out_name = 'OUT'
        super().__init__(node, parent,
                         in_copy_name=in_copy_name,
                         in_progress_name=in_progress_name,
                         out_name=out_name)

    def c_header(self):
        h = 'namespace ' + self.name + '\n'
        h += '{\n'
        h += super().c_header(type_prefix='extern ')
        h += '}\n'
        self.body_name = self.name + '::' + self.body_name
        self.wrapper_name = self.name + '::' + self.wrapper_name

        if hasattr(self, 'in_data_copy_sem'):
            self.in_data_copy_sem.change_name(
                self.name + '::' + self.in_data_copy_sem.name)
        self.output.change_name(self.name + '::' + self.output.name)
        self.in_progress_sem.change_name(
            self.name + '::' + self.in_progress_sem.name)

        return h

    def c_source(self):
        h = super().c_header()
        s = super().c_source()
        return h + s

    def initialize(self):
        if isinstance(self.output, MessageQueue):
            ret = self.output.initialize(key_name=str(self.node) + '_key')
        else:
            ret = self.output.initialize(0)
        if self.in_type != 'void':
            ret += self.in_data_copy_sem.initialize()
        ret += self.in_progress_sem.initialize()
        return ret


class Transition(linux_c.Transition):
    def __init__(self, node, parent):
        super().__init__(node, parent)


class Linux(linux_c.Linux):
    def __init__(self, proj_file,
                 message_queue=MessageQueue,
                 semaphore=Semaphore,
                 place=Place,
                 transition=Transition,
                 debug=os_features.Debug):
        super().__init__(proj_file,
                         message_queue=message_queue,
                         semaphore=semaphore,
                         place=place,
                         transition=transition,
                         debug=debug)

    @staticmethod
    def place_body_name(place):
        return 'Body'

    @staticmethod
    def place_wrapper_name(place):
        return 'Wrapper'

    @staticmethod
    def includes():
        ret = linux_c.Linux.includes()
        ret += '#include <sstream>\n'
        ret += '#include <iostream>\n'
        return ret

    def namespace_start(self, net):
        h = 'namespace ' + net.name + '\n'
        h += '{\n'
        return h

    def namespace_end(self, net):
        return '} //' + net.name + '\n'

    def header_file_start(self, net):
        h = super().header_file_start(net) + '\n'
        h += self.namespace_start(net)
        return h

    def header_file_end(self, net):
        h = super().header_file_end(net) + '\n'
        h += self.namespace_end(net)
        return h

    def source_file_start(self, net):
        return self.namespace_start(net)

    def source_file_end(self, net):
        return self.namespace_end(net)


class PetriNet(petri_net.PetriNet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.transition_sem.prototype = partial(self.transition_sem.prototype,
                                                type_prefix='extern ')

    def c_code(self):
        header, source = super().c_code()
        source += self.os.source_file_start(self)
        self.transition_sem.prototype = partial(self.transition_sem.prototype,
                                                type_prefix='')
        source += self.transition_sem.prototype() + ';\n'
        source += self.os.source_file_end(self)
        return header, source
