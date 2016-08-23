cmake_minimum_required(VERSION 3.0)

# force HUNTER_ROOT to always be on the home dir on Windows
# it would be on C:\Hunter which would be lost during logging out
# on *NIX system it defaults to $HOME/.hunter
if(MSVC)
  set(HUNTER_ROOT "$ENV{HOMEPATH}/.hunter")
endif()

include("cmake/HunterGate.cmake")

HunterGate(
    URL "https://github.com/ruslo/hunter/archive/v0.15.16.tar.gz"
    SHA1 "ca1b3388940bd2ca4452b62a407e6aca743d0ea2"
)

project(comp371-opengl-skeleton)

hunter_add_package(glm)
find_package(glm REQUIRED)

hunter_add_package(glfw)
find_package(glfw3 REQUIRED)

hunter_add_package(glew)
find_package(glew CONFIG REQUIRED)

set(${PROJECT_NAME}_SOURCES
    main.cpp
    COMP371_hw1.vs
    COMP371_hw1.fs
)

add_executable(${PROJECT_NAME}
    ${${PROJECT_NAME}_SOURCES}
)

set_target_properties(${PROJECT_NAME} 
    PROPERTIES
      CXX_STANDARD 11
      CXX_STANDARD_REQUIRED ON
)

target_link_libraries(${PROJECT_NAME} PUBLIC glm glfw glew::glew)

