#include <clib.h>

int main(int argc, char *argv[])
{
	if ((argc != 3) && (argc != 5)) {
		fprintf(stderr, "usage: %s (infile) (outfile) [start] [end]\n",
				argv[0]);
		return -1;
	}

	char *infile = argv[1];
	char *outfile = argv[2];
	unsigned long start = 0, end = 0;
	if (argc == 5) {
		start = atol(argv[3]);
		end = atol(argv[4]);
	}

	return clib_split_file(infile, outfile, start, end);
}
