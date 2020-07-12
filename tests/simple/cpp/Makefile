all: main

main: main.o source.o ./objects/state_graph
	g++ -pthread -std=c++14 -o main ./objects/main.o ./objects/source.o

main.o: main.cpp ./objects/header.hpp
	g++ -Wall -std=c++14 -c main.cpp -o ./objects/main.o

source.o: ./objects/source.cpp ./objects/header.hpp types.h
	g++ -Wall -std=c++14 -c ./objects/source.cpp -o ./objects/source.o

./objects/source.cpp ./objects/header.hpp ./objects/state_graph: ../../../petri_net_interpreter ../simple.dot
	make_petri_net -dot                ../simple.dot \
                -header              ./objects/header.hpp \
                -source              ./objects/source.cpp \
                -types               ../types.h \
                -os                  linux_cpp \
                --state_graph_type   png \
                --debug              print \
                --state_graph_output ./objects/state_graph.png
