# Petri Net Interpreter

This is a program that is meant to interpret a Petri Net written in
dot(a graph description language) that is a high level description of a concurrent program
into boilerplate C code.

## The Problem

Concurrent programming is hard, but there are significant benefits if
it can be properly done.

Large concurrent programs:
  * Cons:
    * hard / nearly impossible to inspect
    * hard / nearly impossible to test
    * usually have many more possible states than intended
    * difficult to maintain due to ballooning complexity
  * Pros:
    * can see performance increases (especially in multi-core systems)
    * can be much more modular / expandable

## What is a Petri Net?

Petri Nets are directed bipartite graphs originally made for describing chemical reactions by
Carl Adam Petri.

They consist of two types of nodes:
 * Places (usually represented by a circle)
 * Transitions (usually represented by a box or line)

No edge is allowed to go from a place to a place or a transition to a transition (bipartite).

The thing that makes Petri nets special is that tokens can go from place to place through
transitions following a certain set of rules specified in the transitions:
  * When a transition fires, it gives all of its output places tokens
  * A transition only fires:
    * if all of its input places have tokens **AND**
    * The tokens in its input places meet the a certain criteria (usually none)

**NOTE: There is no conservation of tokens**

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
