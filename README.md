This will eventually be a modified and packaged version of ehrenbrav's [FCEUX Learning Environment](https://github.com/ehrenbrav/FCEUX_Learning_Environment).

## Building
Right now, the process to build the FCEUX library is to run `scons -C fceux` and then copy `fceux/src/fceux` to `nes_py/libfceux.so`. I'm working on a more elegant solution.
The final goal is to make everything pip-able.