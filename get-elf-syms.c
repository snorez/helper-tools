/*
 * this program is used to get an elf file 's symbols, like functions, variables, ...
 * also, you could use `nm --defined-only -n xxx.o` to get symbols
 */

#if 0
test@ubuntu:~/Desktop/linux-4.15.0$ nm -n --defined-only kernel/bpf/verifier.o
0000000000000000 d bpf_verifier_lock
0000000000000000 b insn_state
0000000000000000 r .LC1
0000000000000000 t __reg_deduce_bounds
0000000000000000 d __warned.51300
0000000000000008 b cur_stack
0000000000000010 b insn_stack
0000000000000080 t find_good_pkt_pointers
0000000000000100 r caller_saved
0000000000000120 r reg_type_str
0000000000000180 r bpf_verifier_ops
0000000000000180 t verbose
00000000000002f0 t check_reg_sane_offset
00000000000003c0 t __check_map_access
0000000000000410 t check_packet_access
00000000000004c0 t mark_map_reg
00000000000005a0 t mark_map_regs
0000000000000640 t print_verifier_state
00000000000008f0 t check_map_access
0000000000000a40 t check_stack_boundary
0000000000000c90 t check_helper_mem_access
0000000000000cf0 t coerce_reg_to_size
0000000000000d80 t __reg_bound_offset
0000000000000dc0 t adjust_ptr_min_max_vals
0000000000001420 t __reg_combine_min_max
0000000000001670 t check_ptr_alignment
0000000000001840 t bpf_patch_insn_data
0000000000001950 t convert_ctx_accesses
0000000000001d30 t fixup_bpf_calls
0000000000002120 t check_ids
0000000000002160 t push_insn
0000000000002290 t mark_reg_not_init
0000000000002380 t mark_reg_unknown
0000000000002470 t check_reg_arg
0000000000002550 t check_func_arg
00000000000028d0 t mark_reg_known_zero
00000000000029c0 t regsafe
0000000000002b80 t reg_set_min_max.part.28
0000000000002e70 t realloc_verifier_state
0000000000002fc0 t copy_verifier_state
00000000000030b0 t pop_stack
0000000000003150 t check_mem_access
0000000000003b70 t do_check
0000000000006d30 T bpf_check
#endif

#if 0
0000000000400688 T _init
0000000000400790 T _start
00000000004007c0 t deregister_tm_clones
0000000000400800 t register_tm_clones
0000000000400840 t __do_global_dtors_aux
0000000000400860 t frame_dummy
0000000000400886 t random_user_name
00000000004009f9 t random_user_passwd0
0000000000400a10 t random_user_passwd1
0000000000400bc9 T main
0000000000400d50 T __libc_csu_init
0000000000400dc0 T __libc_csu_fini
0000000000400dc4 T _fini
0000000000400dd0 R _IO_stdin_used
0000000000400f50 r __GNU_EH_FRAME_HDR
0000000000401100 r __FRAME_END__
0000000000601e00 t __frame_dummy_init_array_entry
0000000000601e00 t __init_array_start
0000000000601e08 t __do_global_dtors_aux_fini_array_entry
0000000000601e08 t __init_array_end
0000000000601e10 d __JCR_END__
0000000000601e10 d __JCR_LIST__
0000000000601e18 d _DYNAMIC
0000000000602000 d _GLOBAL_OFFSET_TABLE_
0000000000602080 D __data_start
0000000000602080 W data_start
0000000000602088 D __dso_handle
00000000006020a0 D printable
0000000000602100 D nr_en
0000000000602140 D complex_passwd
000000000060214d B __bss_start
000000000060214d D _edata
0000000000602150 D __TMC_END__
0000000000602160 B stderr@@GLIBC_2.2.5
0000000000602168 b completed.7594
0000000000602170 B _end
#endif

#include <clib.h>

static char *elf_path[] = {
	"/home/test/Desktop/linux-4.4.0/kernel/bpf/verifier.o",
	"/home/test/Desktop/linux-4.4.0/kernel/bpf/core.o",
	"/home/test/Desktop/linux-4.4.0/kernel/bpf/hashtab.o",
	"/home/test/Desktop/linux-4.4.0/kernel/bpf/helpers.o",
	"/home/test/Desktop/linux-4.4.0/kernel/bpf/inode.o",
	"/home/test/Desktop/linux-4.4.0/kernel/bpf/syscall.o"
};
int get_elf_funcs(char *path)
{
	disable_dbg_mode();
	elf_file *ef = elf_parse(path, O_RDONLY);
	if (!ef)
		err_exit(0, "elf_parse err");

	dump_elf_sym(ef);
	dump_elf_dynsym(ef);
#if 0
	list_comm *n;
	struct _elf_sym *es;
	list_for_each_entry(n, &ef->syms.list_head, list_head) {
		es = (void *)n->data;
		if (ef->elf_bits == 32) {
			Elf32_Sym *sym = es->data;
			if (ELF32_ST_TYPE(sym->st_info) != STT_FUNC)
				continue;
			char b = '\0';
			switch (ELF32_ST_BIND(sym->st_info)) {
			case STB_LOCAL:
				b = 't';
				break;
			case STB_GLOBAL:
				b = 'T';
				break;
			case STB_WEAK:
				b = 'w';
				break;
			default:
				break;
			}
			fprintf(stderr, "%s\n", es->name);
		} else if (ef->elf_bits == 64) {
			Elf64_Sym *sym = es->data;
			if (ELF64_ST_TYPE(sym->st_info) != STT_FUNC)
				continue;
			char b = '\0';
			switch (ELF64_ST_BIND(sym->st_info)) {
			case STB_LOCAL:
				b = 't';
				break;
			case STB_GLOBAL:
				b = 'T';
				break;
			case STB_WEAK:
				b = 'w';
				break;
			default:
				break;
			}
			fprintf(stderr, "%s\n", es->name);
		}
	}
#endif
	elf_cleanup(ef);
	return 0;
}

int main(int argc, char *argv[])
{
	int i, err;
	for (i = 0; i < sizeof(elf_path) / sizeof(char *); i++) {
		err = get_elf_funcs(elf_path[i]);
		if (err == -1)
			err_exit(0, "get_elf_funcs err");
	}
	return 0;
}
