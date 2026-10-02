# Embedded C Build System — HOST and MSP432

I worked on the GCC/GNU Make build system for Module 2 of Introduction to Embedded Systems Software and Development Environments.

## My contribution

The completed Makefile and sources.mk select HOST or MSP432 toolchains, list sources and include paths, generate dependency files, support preprocessing/assembly/object/link targets, and rebuild when switching platforms.

## Reproduce with the supplied course sources

This folder publishes the completed build files. The original C, CMSIS and device-support code belongs to the course and its respective authors.

1. Clone https://github.com/afosdick/ese-coursera-course1.git.
2. Copy the two files in this folder's src/ into the clone's assessments/m2/src/.
3. From that directory run:

```sh
make build PLATFORM=HOST
./c1m2.out
make build PLATFORM=MSP432
```

HOST requires GCC and GNU Make. MSP432 requires arm-none-eabi tools with Newlib/nosys.specs. See README-assignment.md for all commands and VERIFICATION.txt for prior assistant-run results. The MCU executable was cross-compiled, not tested on physical hardware.

## Author and context

**Assignment contributor:** Hritika Adhikary  
**Where:** Coursera, Introduction to Embedded Systems Software and Development Environments.  
**Original course author:** Alex Fosdick, University of Colorado.  
**Implementation assistance:** AI-assisted build-file development and verification.

The course copyright and redistribution notices in the supplied files remain applicable; the portfolio's general rights notice does not replace them.
