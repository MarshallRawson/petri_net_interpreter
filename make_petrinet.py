#!/usr/bin/env python3
import sys
import argparse
from petri_net import PetriNet
from os_features import Debug

if __name__ == '__main__':
  parser = argparse.ArgumentParser(
                      description='Interprets dot file representing a Petri Net and generates the' +\
                                  ' corresponding C templates for G8RTOS.',
                      formatter_class=argparse.RawTextHelpFormatter)

  parser.add_argument('-dot', help='name of dot file to be interpreted', required=True)
  parser.add_argument('-header', help='header file that will be overridden', required=True)
  parser.add_argument('-source', help='source file that will be overridden', required=True)
  parser.add_argument('-types', help='file where types are defined', required=True)
  parser.add_argument('-os', help='OS that is to be used, supported are: linux_static, G8RTOS',
                      required=True)
  parser.add_argument('--debug', help='OPTIONAL: type of debugger to be used.\n' +\
                                      '  G8RTOS Options: uart, wifi\n' +\
                                      '  linux_static Options: print',
                      required=False)
  args = parser.parse_args()

  dot = args.dot
  header = args.header
  source = args.source
  types = args.types
  os = args.os
  debug = Debug

  if os == 'G8RTOS':
    from G8RTOS import G8RTOS
    from G8RTOS import UartDebug, WifiDebug
    if args.debug:
      if args.debug == 'uart':
        debug = UartDebug
      elif args.debug == 'wifi':
        debug = WifiDebug
      else:
        raise Exception('only valid debug options are: uart, wifi')
    net = PetriNet(dot, header, source, types, G8RTOS(debug))

  elif os == 'linux_static':
    from linux_static import LinuxStatic, PrintDebug
    if args.debug == 'print':
      debug = PrintDebug
    else:
      debug = Debug
    net = PetriNet(dot, header, source, types, LinuxStatic(source, debug))

  else:
    raise Exception('%s is not a supported OS'%os)

  net.to_files()
