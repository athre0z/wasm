#include <iostream>

int meow() {
    volatile int asd = 123;
    return asd;
}

int hurr = meow();

int main() {
    std::cout << "Hello, WebAssembly! " << hurr << std::endl;
    return 0;
}
