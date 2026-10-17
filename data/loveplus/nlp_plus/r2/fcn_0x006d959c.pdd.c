/* r2dec pseudo code output (r2 6.0.7) */
/* code_text_unpacked.bin @ 0x6d959c */
#include <stdint.h>
 
void fcn_006d959c (int32_t arg1) {
    int32_t var_a00h;
    int32_t var_a04h;
    r0 = arg1;
    __asm ("vldr s0, [0x006d9640]");
    __asm ("vpush {d8}");
    r1 = *((r0 + 0x44));
    r4 = sp;
    if (r1 == 0) {
        goto label_0;
    }
    r1 = r4 + 0x500;
    *((sp + 0xa04)) = r1;
    *((sp + 0xa00)) = r4;
    r0 = *((r0 + 0x44));
    __asm ("vmov.f32 s16, s0");
    r2 = 0;
    r1 = sp + 0xa00;
    r0 = *((r0 + 0x5a8));
    r0 = fcn_0072202c ();
    if (r0 == 0) {
        r1 = 0;
    }
    if (r0 == 0) {
        r2 = 0x230;
    }
    if (r0 == 0) {
        goto label_1;
    }
    do {
        r0 = *(r4);
        r4 += 2;
        __asm ("rsblt r0, r0, 0");
        if (r1 >= r0) {
            r1 = r0;
        }
        r2--;
    } while (r2 != r2);
    __asm ("vmov s0, r1");
    __asm ("vldr s1, [0x006d9644]");
    __asm ("vcvt.f32.s32 s0, s0");
    __asm ("vmul.f32 s16, s0, s1");
label_1:
    r0 = *(0x6d9644);
    __asm ("vldr s1, [r0, 8]");
    __asm ("vdiv.f32 s0, s16, s1");
    __asm ("vmov r0, s0");
    __asm ("vldrgt s0, [0x006d964c]");
label_0:
    __asm ("vpop {d8}");
}
