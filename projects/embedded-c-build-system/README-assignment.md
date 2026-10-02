# C1M2 — GCC and GNU Make build system

The course repository places this assignment in `assessments/m2/src`, not
`assessments/c2`. Run the commands below from the `src` directory.

## Quick start (Ubuntu course VM)

After extracting the ZIP:

```bash
cd ese-coursera-course1/assessments/m2/src
make clean
make build PLATFORM=HOST
./c1m2.out
make build PLATFORM=MSP432
make clean
```

The HOST program displays `aXy72_L+R`. The unchanged course program actually
emits `aXy72_\x00L+R\n`: buffer index 6 is zero, so an invisible null byte
appears between `_` and `L`. This is expected from the supplied source.

The MSP432 executable is for the microcontroller, not the Ubuntu host.
The build uses `gcc`, `size`, and `objdump` for HOST; and
`arm-none-eabi-gcc`, `arm-none-eabi-size`, and `arm-none-eabi-objdump`
for MSP432. The ARM toolchain must include Newlib and `nosys.specs`.
If a command is missing, check your course VM/toolchain setup and PATH.
No compiler binaries are included in this archive.

## Supported commands

| Command | Result |
|---|---|
| `make main.i PLATFORM=HOST` | Preprocessed C output |
| `make main.asm PLATFORM=HOST` | Compiler assembly output |
| `make main.o PLATFORM=HOST` | Object plus dependency file, without linking |
| `make compile-all PLATFORM=HOST` | All HOST objects, without linking |
| `make build PLATFORM=HOST` | `c1m2.out`, `c1m2.map`, objects, dependencies, size report |
| `make c1m2.asm PLATFORM=HOST` | Disassembly of the linked executable |
| `make clean` | Removes generated build files |

Replace HOST with MSP432 for the embedded build. Individual file targets also
work with `memory` and, for MSP432, the three device-specific source basenames.
`all` and `Build` are aliases for `build`; `Clean` is an alias for `clean`.

## How it works

- `sources.mk` explicitly lists two HOST sources or five MSP432 sources and
  the corresponding include directories. Source discovery uses no wildcards.
- `Makefile` selects the compiler, preprocessor define, architecture flags,
  linker script, binary tools, and build recipes based on PLATFORM.
- `$@` means the output target and `$<` means the first prerequisite.
  `$*` is the basename matched by a pattern rule.
- `-MMD -MP -MF` generates header dependency files; `-MT` lists the object,
  preprocessed, and assembly targets that depend on those headers.
- The linker command lists only object files as its link inputs. The linker
  script and Makefiles are prerequisites, not objects to link.
- A platform stamp invalidates outputs when switching HOST/MSP432 without
  cleaning. Header dependencies and changes to either Makefile also trigger
  rebuilds. If overriding flags manually, run `make clean` first.
- `build`, `compile-all`, and `clean` have `.PHONY` protection.
- Source files, headers, and the supplied linker script are unchanged.

## Verification

Tests passed on Ubuntu 24.04 with native GCC and Arm GNU Toolchain
10.3-2021.10. `VERIFICATION.txt` contains actual assistant-run command output.
Both platforms passed full builds and generation of every required output
format. Compile-only, incremental builds, header changes, platform switching,
cleanup, and invalid-platform handling were also checked.
MSP432 was cross-compiled and its ARM ELF header inspected; it was not run
on physical hardware. Compiler versions in the course VM may differ.

## Submission

The archive is named `C1M2-Adhikary.zip`. It contains the top-level
`ese-coursera-course1` directory, original `.git` history, and edited build
files. Generated build outputs were cleaned before packaging.
Review the Makefile and run the quick-start commands in your VM before
uploading the ZIP to Coursera. The verification log is assistant-run evidence,
not a screenshot or claim that you ran the commands yourself.
