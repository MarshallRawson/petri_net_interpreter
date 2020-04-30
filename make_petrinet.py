#!/usr/bin/env python3
import sys
import argparse
from petri_net import PetriNet
from graph_entities import Place, Transition
from os_features import Debug
from G8RTOS import G8RTOS, UartDebug, WifiDebug

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='Interprets dot file representing a Petri Net and generates the corresponding C templates for G8RTOS.')

  parser.add_argument('dot_file', help='name of dot file to be interpreted')
  parser.add_argument('header_file', help='header file that will be overridden')
  parser.add_argument('source_file', help='source file that will be overridden')
  parser.add_argument('types_file', help='file where types are defined')
  parser.add_argument('--debug', help='OPTIONAL: type of debugger to be used: uart, wifi')
  args = parser.parse_args()

  dot = args.dot_file
  header = args.header_file
  source = args.source_file
  types = args.types_file

  if args.debug:
    if args.debug == 'uart':
      debug = UartDebug
    elif args.debug == 'wifi':
      debug = WifiDebug
    else:
      raise Exception('only valid debug options are: uart, wifi')
  else:
    debug = Debug

  net = PetriNet(dot, header, source, types,
                 G8RTOS(debug), Place, Transition)
  net.to_files()
