cmake_minimum_required(VERSION 3.16)
project(DET01_Sim)

find_package(Geant4 REQUIRED ui_all vis_all)

include(${Geant4_USE_FILE})

include_directories(${PROJECT_SOURCE_DIR}/include)
include_directories(${Geant4_INCLUDE_DIRS})

file(GLOB SOURCES ${PROJECT_SOURCE_DIR}/src/*.cc)
file(GLOB HEADERS ${PROJECT_SOURCE_DIR}/include/*.hh)

add_executable(det01 det01.cc ${SOURCES} ${HEADERS})
target_link_libraries(det01 ${Geant4_LIBRARIES})

# Copy macros to the build directory
file(COPY init_vis.mac vis.mac vis_fast.mac run_cosmic.mac DESTINATION ${CMAKE_BINARY_DIR})
