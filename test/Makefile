all: main

main: main.o source.o
	gcc -pthread -o main ./objects/main.o ./objects/source.o

main.o: main.c header.h
	gcc -c main.c -o ./objects/main.o

source.o: source.c header.h types.h
	gcc -c source.c -o ./objects/source.o

source.c header.h: ../linux_static.py ../graph_entities.py ../os_features.py ../petri_net.py ../make_petrinet.py simple.dot
	../make_petrinet.py -dot simple.dot -header header.h -source source.c -types types.h -os linux_static --debug print
