libmanu.so: manu.o
	g++ -shared -Wl,-soname,libmanu.so -o libmanu.so manu.o

manu.o: manu.cpp
	g++ -c -fPIC manu.cpp -o manu.o

clean:
	rm -f libmanu.so manu.o
