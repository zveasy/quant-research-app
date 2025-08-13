cmake_minimum_required(VERSION 3.14)
project(quant_cpp_tests)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

enable_testing()

add_executable(sample_test tests/sample_test.cpp)
add_test(NAME sample_test COMMAND sample_test)
