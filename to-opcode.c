#include <clib.h>
#include <sys/wait.h>

int main(int argc, char *argv[])
{
	if (argc < 2)
		err_exit(0, "usage: %s (asmcode) [format]", argv[0]);

	enable_dbg_mode();

	char *file_w = "/tmp/to_opcode.asm";
	char *file_r = "/tmp/to_opcode.disa";
	int fd_w = open(file_w, O_WRONLY | O_CREAT | O_TRUNC, S_IWUSR | S_IRUSR);
	if (fd_w == -1)
		err_exit(1, "open err");
	int err = write(fd_w, argv[1], strlen(argv[1]));
	if (err == -1)
		err_exit(1, "write err");
	close(fd_w);

	if ((err = fork()) < 0) {
		err_exit(1, "fork err");
	} else if (err == 0) {
		char *arg0 = "/usr/bin/nasm";
		char *arg1 = (argc == 3) ? argv[2] : "-fwin64";
		char *arg2 = "/tmp/to_opcode.asm";
		char *arg3 = "-o";
		char *arg4 = "/tmp/to_opcode.o";
		char *new_argv[6] = {arg0, arg2, arg1, arg3, arg4, NULL};
		execv("/usr/bin/nasm", new_argv);
	}
	int status;
	waitpid(err, &status, 0);
	if (WIFEXITED(status)) {
		system("objdump -dS -M intel /tmp/to_opcode.o"
				" > /tmp/to_opcode.disa");
		regfile *rf = regfile_open(REGFILE_T_TXT, file_r, O_RDONLY);
		if (!rf)
			err_exit(0, "regfile_open err");

		err = txtfile_readlines(rf);
		if (err == -1)
			err_exit(0, "txtfile_readlines err");
		list_comm *tmp;
		int flag = 0;
		list_for_each_entry(tmp, txt_rdata(rf), list_head) {
			buf_struct *bs = (buf_struct *)tmp->data;
			if (flag == 1)
				printf("%s\n", bs->buf);
			if (strstr(bs->buf, "00000000") &&
				strstr(bs->buf, "<.text>")) {
				flag = 1;
			}
		}
		regfile_close(rf);
	} else {
		err_exit(0, "to_opcode err");
	}

	return 0;
}
