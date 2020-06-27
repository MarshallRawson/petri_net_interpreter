all: main

main: main.o source.o ./objects/state_graph
	gcc -pthread -o main ./objects/main.o ./objects/source.o

main.o: main.c ./objects/header.h
	gcc -c main.c -o ./objects/main.o

source.o: ./objects/source.c ./objects/header.h types.h
	gcc -c ./objects/source.c -o ./objects/source.o

./objects/source.c ./objects/header.h ./objects/state_graph: ../linux_static.py ../graph_entities.py ../os_features.py ../petri_net.py ../make_petrinet.py simple.dot
	../make_petrinet.py -dot simple.dot -header ./objects/header.h -source ./objects/source.c -types ../types.h -os linux_static --debug print --state_graph_type png --state_graph_output ./objects/state_graph.png
