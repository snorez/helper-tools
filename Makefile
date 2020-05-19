TMP = /tmp
CLIB_PATH = /home/zerons/workspace/clib
CLIB_LIB = $(CLIB_PATH)/lib
CLIB_INC = $(CLIB_PATH)/include
ARCH = $(shell getconf LONG_BIT)
CLIB_SO = clib$(ARCH)
CWD = $(shell pwd)
vpath %.c ./
vpath %.h ./

CC = gcc -Wall -std=gnu11 -m$(ARCH) -D_FILE_OFFSET_BITS=64 -g
objs = get_elf_syms.o \
       randstr.o \
       cp_file.o \
       to_opcode.o \
       search_op.o
elfs = get_elf_syms \
       randstr \
       cp_file \
       to_opcode \
       search_op

all: $(elfs)
	mv $(elfs) bin/
clean:
	rm -vf $(elfs)

$(objs): %.o : %.c
	$(CC) -I$(CLIB_INC) -c $< -o $(TMP)/$@

$(elfs): % : %.o
	$(CC) $(TMP)/$< -L$(CLIB_LIB) -l$(CLIB_SO) -o $@ -Wl,-rpath $(CLIB_LIB)
