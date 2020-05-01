# Petri Net Interpreter

## What is this?

This is a program that is meant to interpret a
[Petri Net](https://www.techfak.uni-bielefeld.de/~mchen/BioPNML/Intro/pnfaq.html)
written in [dot](https://en.wikipedia.org/wiki/DOT_(graph_description_language) into
boilerplate C code.

### In the context of this framework, petri nets are interpreted as follows:
  * Nodes = Functions
    * Places = Processes = Threads
    * Transitions = Functions that add threads with certain data dependent on conditions
  * Edges = Function calls / Thread Adding
    * Place -> Transition = Call the transition function(no sub data field should be specified)
    * Transition -> Place = Add thread with a certain subset of the available data
  from one of the Transition's input Places

### Goal of This Framework

The goal end result is that the programmer(s) only really needs to worry about the code that
happens inside of each process, and how that process relates to other processes from the
perspective of a petri net.

## Why Use This

### Operating System Agnostic:

  This framework is operating system agnostic, and as a result the petri nets constructed for
  it to interpret are also operating system agnostic, making system migration less painful.

  * Supported Operating Systems:
    * G8RTOS (OS made in Micro Processors 2 at UF (not Open Source-able :-( ))

### Dynamic / Static Memory Agnostic:

  This framework can be made to work in environments where dynamic memory is or is not
  supported (ie: embedded OS applications)

### Deterministic Concurrent Programming:

  This framework makes it relatively easy to make deterministic concurrent programming
  according to a well-defined mathematical object(Petri Nets).

### Lends Itself to Modular Design
  This framework lends itself to modular processes with well defined inputs and
  outputs that are easy to link together in many many different ways.

## Limitations
  This framework does not work well when used as a programming language itself.
  Even though you can totally can, you shouldn't because there may be significant
  overhead when adding, killing, and switching between many threads that do not serve any
  purpose, so this utility should be used at the process level description.

## Examples
  See `example.dot` for an example a valid Petri Net in dot.

## TODOs

  * Add Linux support (both dynamic and static memory)
  * Add FreeRTOS support (static memory)
  * Add ROS bridge
  * Add dummy Place support (so dummy threads aren't actually run, but rather just their
  output semaphores' incremented)
  * Add Non-deterministic petri-net warnings / erros
  * Add petri net simulation to find if a net is likely unbound
  * Add subgraph support as namespaces for C++ compliant systems
  * Add support for linking together of dot files to make a larger net.
