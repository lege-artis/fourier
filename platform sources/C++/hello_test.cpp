#include <iostream>
#include <cassert>
#include <string>

/**
 * C++ Hello World Test
 *
 * A simple test program that demonstrates basic C++ functionality
 * including string operations and assertions.
 */

int main() {
    std::cout << "Starting C++ Hello World Test..." << std::endl;

    // Test 1: Basic string output
    std::string greeting = "Hello, World!";
    std::cout << greeting << std::endl;
    assert(!greeting.empty());
    assert(greeting.length() == 13);

    // Test 2: String comparison
    std::string expected = "Hello, World!";
    assert(greeting == expected);

    // Test 3: Basic arithmetic
    int a = 5;
    int b = 3;
    int sum = a + b;
    assert(sum == 8);
    std::cout << a << " + " << b << " = " << sum << std::endl;

    // Test 4: Multiple assertions
    assert(a > b);
    assert(b < a);
    assert(sum > 0);

    // Test 5: String manipulation
    greeting.append(" (From C++)");
    std::cout << greeting << std::endl;
    assert(greeting.find("C++") != std::string::npos);

    std::cout << "All C++ tests passed successfully!" << std::endl;

    return 0;
}
