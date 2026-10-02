#******************************************************************************
# Copyright (C) 2017 by Alex Fosdick - University of Colorado
#
# Redistribution, modification or use of this software in source or binary
# forms is permitted as long as the files maintain this copyright. Users are 
# permitted to modify this and use it to learn about the field of embedded
# software. Alex Fosdick and the University of Colorado are not liable for any
# misuse of this material. 
#
#*****************************************************************************

# Build from assessments/m2/src with PLATFORM=HOST or PLATFORM=MSP432.
# Targets: build/all, compile-all, clean, NAME.i, NAME.asm, NAME.o,
#          and c1m2.asm (disassembly of the linked executable).
.DEFAULT_GOAL := build
.DELETE_ON_ERROR:

# Require an explicit platform, except for a standalone clean operation.
ifneq ($(MAKECMDGOALS),clean)
ifneq ($(MAKECMDGOALS),Clean)
ifeq ($(filter $(PLATFORM),HOST MSP432),)
$(error Specify PLATFORM=HOST or PLATFORM=MSP432)
endif
endif
endif

include sources.mk

TARGET = c1m2
CPU = cortex-m4
ARCH = armv7e-m
SPECS = nosys.specs
CFLAGS = -Wall -Werror -g -O0 -std=c99
CPPFLAGS = $(INCLUDES) -D$(PLATFORM)
LDFLAGS = -Wl,-Map=$(TARGET).map

ifeq ($(PLATFORM),MSP432)
CC = arm-none-eabi-gcc
LD = arm-none-eabi-ld
SIZE = arm-none-eabi-size
OBJDUMP = arm-none-eabi-objdump
LINKER_FILE = ../msp432p401r.lds
ARCH_FLAGS = -mcpu=$(CPU) -mthumb -march=$(ARCH) \
             -mfloat-abi=hard -mfpu=fpv4-sp-d16
CFLAGS += $(ARCH_FLAGS) --specs=$(SPECS)
LDFLAGS += -T $(LINKER_FILE)
else
CC = gcc
LD = ld
SIZE = size
OBJDUMP = objdump
LINKER_FILE =
endif

OBJS = $(SOURCES:.c=.o)
DEPS = $(SOURCES:.c=.d)
# Switching platforms invalidates shared output filenames. This stamp is a
# real file prerequisite; it changes only when the selected platform changes.
PLATFORM_STAMP = .platform-$(PLATFORM)
$(PLATFORM_STAMP):
	rm -f .platform-HOST .platform-MSP432
	touch $@

.PHONY: build all compile-all clean Build Clean
build: $(TARGET).out
	$(SIZE) $(TARGET).out
all Build: build
compile-all: $(OBJS)

$(TARGET).out: $(OBJS) $(LINKER_FILE) Makefile sources.mk $(PLATFORM_STAMP)
	$(CC) $(CFLAGS) $(OBJS) $(LDFLAGS) -o $@

%.o: %.c Makefile sources.mk $(PLATFORM_STAMP)
	$(CC) $(CPPFLAGS) $(CFLAGS) -MMD -MP -MF $(@:.o=.d) -MT "$*.o $*.i $*.asm" -c $< -o $@

%.i: %.c Makefile sources.mk $(PLATFORM_STAMP)
	$(CC) $(CPPFLAGS) $(CFLAGS) -MMD -MP -MF $(@:.i=.d) -MT "$*.o $*.i $*.asm" -E $< -o $@

%.asm: %.c Makefile sources.mk $(PLATFORM_STAMP)
	$(CC) $(CPPFLAGS) $(CFLAGS) -MMD -MP -MF $(@:.asm=.d) -MT "$*.o $*.i $*.asm" -S $< -o $@

$(TARGET).asm: $(TARGET).out
	$(OBJDUMP) -d $< > $@


clean:
	rm -f *.o *.d *.dep *.i *.asm *.map *.out .platform-HOST .platform-MSP432
Clean: clean

-include $(DEPS)
