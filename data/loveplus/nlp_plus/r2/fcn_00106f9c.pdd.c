/* r2dec pseudo code output (r2 6.0.7) */
/* code_text_unpacked.bin @ 0x106f9c */
#include <stdint.h>
 
void fcn_00106f9c (int32_t arg_20h, int32_t arg1, int32_t arg2) {
    r0 = arg1;
    r1 = arg2;
    r5 = sp + 0x20;
    r4 = r0;
    r0 = *(r5);
    ip = *((r5 + 4));
    r5 = *(0x107024);
    if (r0 != 0) {
        r0 = *(0x00107024);
    }
    if (r0 != 0) {
        r0 = *((r0 + 0x98));
    }
    if (ip != 0) {
        ip = *(0x00107028);
    }
    r0 = *(0x107024);
    if (ip != 0) {
        ip = *((ip + 0x1c));
    }
    if (r0 != 0) {
        *(sp) = r3;
        *((sp + 4)) = ip;
        r3 = r2;
        r2 = r1;
        r1 = r4;
        fcn_0010d6f8 (r0);
    }
    r3 = 0;
    r0 = 1;
    r2 = 2;
    r4 = r3;
    *(sp) = r0;
    *((sp + 4)) = r2;
    *((sp + 8)) = r3;
    *((sp + 12)) = r4;
    r1 = sp;
    r2 = r3;
    r0 = ip;
    fcn_00122908 ();
    r0 = 0;
}
