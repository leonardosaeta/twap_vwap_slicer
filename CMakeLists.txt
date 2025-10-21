# CMakeLists.txt
cmake_minimum_required(VERSION 3.20)
project(twap_vwap_slicer CXX)
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_FLAGS_RELEASE "${CMAKE_CXX_FLAGS_RELEASE} -O3 -march=native")
add_executable(twap_vwap src/main.cpp)
target_include_directories(twap_vwap PRIVATE include)
