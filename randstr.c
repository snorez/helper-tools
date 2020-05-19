#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <time.h>
#include <stdint.h>
#include <sys/time.h>
#include <errno.h>
#include <ctype.h>
#include <strings.h>

char printable[] = {' ', '!', '"', '#', '$', '%', '&', '\'', '(', ')', '*',
		'+', ',', '-', '.', '/', '0', '1', '2', '3', '4', '5', '6',
		'7', '8', '9', ':', ';', '<', '=', '>', '?', '@', 'A', 'B',
		'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N',
		'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
		'[', '\\', ']', '^', '_', '`', 'a', 'b', 'c', 'd', 'e', 'f',
		'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r',
		's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '{', '|', '}', '~',};

char nr_en[] = {'0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
		'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k',
		'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v',
		'w', 'x', 'y', 'z', 'A', 'B', 'C', 'D', 'E', 'F', 'G',
		'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R',
		'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'};

char complex_passwd[] = {'!', '@', '#', '$', '%', '^', '&', '*', '(', ')',
			',', '.', '_'};

static char *random_user_name(int cnt)
{
	if ((cnt < 0) || (cnt > 32)) {
		fprintf(stderr, "random_user_name err, invalid cnt, 32 max\n");
		return NULL;
	}

	char *ret = (char *)malloc(cnt + 1);
	if (!ret) {
		fprintf(stderr, "random_user_name malloc err\n");
		return NULL;
	}
	memset(ret, 0, cnt + 1);

	size_t len = strlen(nr_en);
	size_t i;
	struct timeval tv;
	if (gettimeofday(&tv, NULL) == -1) {
		fprintf(stderr, "random_user_name gettimeofday err\n");
		free(ret);
		return NULL;
	}
	srand(tv.tv_sec + tv.tv_usec);

	for (i = 0; i < cnt; i++)
		ret[i] = nr_en[random()%len];
	return ret;
}

static char *random_user_passwd0(int cnt)
{
	return random_user_name(cnt);
}

static char *random_user_passwd1(int cnt)
{
	if ((cnt < 0) || (cnt > 32)) {
		fprintf(stderr, "random_user_passwd1 err, invalid cnt\n");
		return NULL;
	}

	char *ret = (char *)malloc(cnt + 1);
	if (!ret) {
		fprintf(stderr, "random_user_passwd1 malloc err\n");
		return NULL;
	}
	memset(ret, 0, cnt + 1);

	size_t len0 = strlen(nr_en);
	size_t len1 = strlen(complex_passwd);
	size_t i;
	struct timeval tv;
	if (gettimeofday(&tv, NULL) == -1) {
		fprintf(stderr, "random_user_passwd1 gettimeofday err\n");
		free(ret);
		return NULL;
	}
	srand(tv.tv_sec + tv.tv_usec);

	for (i = 0; i < cnt; i++) {
		if (random() % 2)
			ret[i] = nr_en[random() % len0];
		else
			ret[i] = complex_passwd[random() % len1];
	}
	return ret;
}

int main(int argc, char *argv[])
{
	if (argc != 3) {
		fprintf(stderr, "usage: %s -[u|p|P] outlen\n", argv[0]);
		fprintf(stderr, "\t\t -u\t random an user name\n");
		fprintf(stderr, "\t\t -p\t random a simple user password\n");
		fprintf(stderr, "\t\t -P\t random a complex user password\n");
		return -1;
	}

	int cnt = atoi(argv[2]);
	char *str = NULL;
	if (argv[1][1] == 'u')
		str = random_user_name(cnt);
	else if (argv[1][1] == 'p')
		str = random_user_passwd0(cnt);
	else if (argv[1][1] == 'P')
		str = random_user_passwd1(cnt);
	else
		fprintf(stderr, "invalid arg\n");
	if (str)
		fprintf(stderr, "%s\n", str);
	free(str);
	return 0;
}
