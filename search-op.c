#include <clib.h>

static char *file_r = "/home/zerons/workspace/vmlinuxs/debian.vmlinux";
static char *opcode1[] = {
	"\x48\x8b\x47",
	"\x48\x8b\x5f",
	"\x48\x8b\x6f",
	"\x4c\x8b\x67",
	"\x4c\x8b\x6f",
};
static char *opcode2[] = {
	"\x48\x8b\x47",
	"\x48\x8b\x5f",
	"\x48\x8b\x6f",
	"\x4c\x8b\x67",
	"\x4c\x8b\x6f",
};

static char *mem_match(char *b, char *match, size_t match_len, size_t max)
{
	char *p = b;
	while (p < (b+max)) {
		if (memcmp(p, match, match_len)) {
			p++;
			continue;
		}
		return p;
	}
	return NULL;
}

int main(int argc, char *argv[])
{
	size_t len;
	char *buf = clib_loadfile(file_r, &len);
	if (!buf)
		err_exit(0, "clib_loadfile err");

	char *pos0 = buf, *pos1;
	while (1) {
		if (pos0 >= (buf + len))
			break;
		int i = 0, j = 0;
		for (i = 0; i < sizeof(opcode1) / sizeof(opcode1[0]); i++) {
			if (memcmp(pos0, opcode1[i], strlen(opcode1[i])))
				continue;
			pos1 = pos0 + strlen(opcode1[i]) + 1;
			for (j = 0; j < sizeof(opcode2)/sizeof(char *); j++) {
				char *pos_tmp = pos1;
				while ((pos_tmp = mem_match(pos_tmp, opcode2[j],
							strlen(opcode2[j]),
							0x20-(pos_tmp-pos1)))) {
					char *pos2 = pos_tmp + strlen(opcode2[j]) + 1;
					char *pos3 = mem_match(pos2, "\xc3", 1, 0x20);
					if (pos3) {
						if (mem_match(pos2, "\x48\x8b", 2, pos3-pos2)) {
						fprintf(stdout, "addr: 0x%lx\n",
						     0xffffffff80e00000+(pos0 - buf));
						fflush(stdout);
						}
					}
					pos_tmp++;
					if ((pos_tmp - pos1) >= 0x20)
						break;
				}
			}
		}
		pos0++;
	}
	return 0;
}
