#!/usr/bin/env python3
import warnings
import pygraphviz as pgv


class StateGraph(object):
    def __init__(self, petri_net):
        self.state_graph = {}
        self.petri_net = petri_net
        self.graph = None

    def generate(self):
        transition0 = self.petri_net.transitions[self.petri_net.transition0()]
        start_state = {}
        for name in self.petri_net.places.keys():
            start_state[name] = 0
        for edge in transition0.outs.keys():
            start_state[edge] += 1
        self.explore_state(start_state)
        self.graph = pgv.AGraph(self.state_graph, directed=True)

    def explore_state(self, prev_state):
        if self.str(prev_state) not in self.state_graph.keys():
            self.state_graph[self.str(prev_state)] = []
        next_states = self.next_states(prev_state)
        for state in next_states:
            self.state_graph[self.str(prev_state)].append(self.str(state))
            if self.str(state) not in self.state_graph.keys():
                if sum(state.values()) > self.petri_net.max_tokens():
                    warnings.warn(
                        'State ' +
                        self.str(state) +
                        ' has more than the max number of tokens, this state will not be explored',
                        RuntimeWarning)
                else:
                    self.explore_state(state)

    def next_states(self, state):
        # find all the transitions that could fire at this state
        next_states = []
        for transition in self.petri_net.transitions.values():
            in_places = [edge for edge in transition.ins.keys()]
            out_places = [edge for edge in transition.outs.keys()]
            availble_tokens = [state[place] for place in in_places]
            if 0 not in availble_tokens and len(availble_tokens) > 0:
                # take a token from all input places
                new_state = state.copy()
                for place in in_places:
                    new_state[place] -= 1
                # add a token to all output places
                for place in out_places:
                    new_state[place] += 1
                next_states.append(new_state)
        return next_states

    def to_dot(self, dot_file):
        self.graph.write(dot_file)

    def to_png(self, png_file):
        self.graph.layout()
        self.graph.draw(png_file)

    def str(self, state):
        return str(state).replace(', ',',\n ')
