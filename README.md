# EDK2-Tools

This repository contains some of my tools for edk2-projects (UEFI-level
development), that worth sharing.

- [compilation_database_patch](compilation_database_patch/) allows to generate
  `compile_commands.json` file, that can be used by completion engines
- [qemu_and_gdb](qemu_and_gdb/) allows to pring `gdb` command, that loads
  `.debug` file with debug symbols at a correct address, based on `qemu` logs
- [project_templates](project_templates/) allows to create a new edk2-project in
  a single command call
