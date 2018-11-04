#include <iostream>

class Manu {
	public:
		void bar () {
			//~ std::cout << "foobar" << std::endl;
		}
};

extern "C" {
	Manu* Foo_new() { return new Manu(); }
	void Foo_bar(Manu* manu) { manu->bar(); }
}
