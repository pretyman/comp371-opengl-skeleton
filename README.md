# COMP371 Skeleton code for Windows, Linux and OSX
### CMake based build with instructions be used with:
* [Visual Studio](https://github.com/pretyman/comp371-opengl-skeleton/wiki/Visual-Studio-Instructions)
* [Xcode](https://github.com/pretyman/comp371-opengl-skeleton/wiki/Xcode-Instructions)
* [QtCreator (Linux/OSX)](https://github.com/pretyman/comp371-opengl-skeleton/wiki/QtCreator-Instructions)

### I know my stuff, what do I really need to do to get this working?

You need to set the working directory of the process to where the shaders are. If you don't know how to do that, check the instructions above.

### Note for Linux platform

You need the Mesa 3D library installed:
* Ubuntu: `sudo apt install libgl1-mesa-dev`
* Fedora: `sudo dnf install mesa-libGL-devel`

This skeleton depends on glfw and glew the glew libraries.It has transitive dependencies on `x11`, so it ends up downloading and compiling a lot of package dependencies. This means that the compilation can take long at the first time, but once that is done, the binaries build will be cached.

### Note for OSX platform

For some reason the compilation of glew takes really, really, long. Be patient, but once that is done, the compiled binaries will be cached.




