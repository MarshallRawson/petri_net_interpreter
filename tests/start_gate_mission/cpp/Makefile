all: ./objects/start_gate_mission.cpp ./objects/start_gate_mission.hpp ./objects/state_graph

./objects/start_gate_mission.cpp \
./objects/start_gate_mission.hpp \
./objects/state_graph: ../../../petri_net_interpreter ../start_gate_mission.dot
	make_petri_net -dot                ../start_gate_mission.dot \
                -header              ./objects/start_gate_mission.hpp \
                -source              ./objects/start_gate_mission.cpp \
                -types               ../types.h \
                -os                  linux_cpp \
                --debug              print \
                --state_graph_type   dot \
                --state_graph_output ./objects/state_graph.dot
