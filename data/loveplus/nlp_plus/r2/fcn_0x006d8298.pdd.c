/* r2dec pseudo code output (r2 6.0.7) */
/* code_text_unpacked.bin @ 0x6d8298 */
#include <stdint.h>
 
void fcn_006d8298 (int32_t arg1) {
    r0 = arg1;
    r4 = r0;
    sb = 0;
    r0 = *((r0 + 0x1bc));
    __asm ("cmpne r0, 2");
    if (r0 != 0) {
        r0 = r4 + 0x800;
        r5 = r4 + 0x1ec;
        r0 += 0xfc;
        void (*0x11611c)(uint32_t) (r0);
        r6 = *((r5 + 0x708));
        r0 = r5 + 0x710;
        void (*0x116288)(uint32_t) (r0);
        if (r6 <= 0) {
            goto label_0;
        }
        r0 = *((r4 + 0x1bc));
        if (r0 != 3) {
            __asm ("cmpne r0, 7");
            __asm ("cmpne r0, 1");
            if (r0 != 6) {
            } else {
                r0 = *(0x6d84e0);
                r0 = *((r0 + r4));
                if (r0 < 0) {
                    goto label_0;
                }
            }
            r0 = *((r4 + 0x78));
            void (*0x66e114)(uint32_t) (r0);
            r1 = *((r4 + 0x58));
            *((r4 + 0x1bd)) = fp;
            *((r4 + 0x1bc)) = sb;
            if (r1 == 0) {
                goto label_0;
            }
            r0 = r1;
            void (*0x2fcd88)(uint32_t) (r0);
            *((r4 + 0x58)) = sb;
        }
    }
label_0:
    r0 = *(0x6d84e4);
    r5 = 0;
    sl = r0 + 0x400;
    r8 = r0 + 0x400;
    sl += 0x318;
    r8 += 0x308;
    do {
        r0 = r5 + (r5 << 2);
        r6 = r4 + (r0 << 2);
        r0 = *((r6 + 0x88));
        if (r0 != 0) {
            r1 = *(0x6d84e4);
            void (*0x69683c)(uint32_t) (r1);
            r7 = *(0x6d84e4);
            r0 = sl;
            void (*0x11611c)(uint32_t) (r0);
            r0 = r7 + 0x710;
            void (*0x11611c)(uint32_t) (r0);
            r0 = *(0x6d8bec);
            r0--;
            *(r8) = r0;
            r0 = *(0x6d84e4);
            r1 = *(0x6d84f8);
            *(r7) = r1;
            r1 = *(0x6d84f8);
            if (r1 == 0) {
                r2 = *((r0 + 0x18));
            }
            if (r1 == 0) {
                *((r1 + 0x18)) = r2;
            }
            r1 = *(0x6d84fc);
            if (r1 == 0) {
                r2 = *((r0 + 0x14));
            }
            if (r1 == 0) {
                *((r1 + 0x14)) = r2;
            }
            *((r0 + 0x14)) = sb;
            *((r0 + 0x18)) = sb;
            r1 = *(0x6d84e8);
            if (r1 != 0) {
                *((r7 + 4)) = r0;
            }
            if (r1 != 0) {
                *((r0 + 0x14)) = r1;
                r1 = *((r7 + 4));
                *((r1 + 0x18)) = r0;
                *((r7 + 4)) = r0;
            }
            r0 = r7 + 0x710;
            void (*0x116288)(uint32_t, uint32_t) (r0, r1);
            r0 = r7 + 0x720;
            void (*0x116288)(uint32_t) (r0);
        }
        r0 = *((r6 + 0x80));
        if (r0 != 0) {
            void (*0x2fcd88)(uint32_t) (r0);
            *((r6 + 0x80)) = sb;
        }
        r5++;
        *((r6 + 0x7c)) = fp;
    } while (r5 < 0x10);
    r5 = *((r4 + 0x60));
    if (r5 == 0) {
        goto label_1;
    }
    r0 = *((r4 + 0x64));
    r6 = 0;
    if (r0 <= 0) {
        goto label_2;
    }
    do {
        r0 = *((r5 + 0x13));
        if (r0 != 0) {
            r0 = *((r5 + 4));
            if (r0 != 0) {
                void (*0x2fcd88)(uint32_t) (r0);
                *((r5 + 4)) = sb;
            }
            r0 = *((r5 + 8));
            if (r0 == 0) {
                goto label_3;
            }
            r1 = 3;
            void (*0x129ed4)(uint32_t) (r1);
            *((r5 + 8)) = sb;
        }
label_3:
        r0 = *((r4 + 0x64));
        r6++;
        r5 += 0x14;
    } while (r0 > r6);
    r0 = *((r4 + 0x60));
    if (r0 != 0) {
label_2:
        r0 = *((r4 + 0x60));
        void (*0x2fcd88)(uint32_t) (r0);
        *((r4 + 0x60)) = sb;
    }
    *((r4 + 0x64)) = sb;
label_1:
    r0 = *((r4 + 0x48));
    if (r0 != 0) {
        void (*0x2fcd88)(uint32_t) (r0);
        *((r4 + 0x48)) = sb;
    }
    r0 = *((r4 + 0x58));
    *((r4 + 0x4c)) = sb;
    *((r4 + 0x50)) = sb;
    if (r0 != 0) {
        void (*0x2fcd88)(uint32_t) (r0);
        *((r4 + 0x58)) = sb;
    }
    *((r4 + 0x68)) = sb;
    *((r4 += 0x6c)) = sb;
    r4 += 4;
    r0 = ~0x80000000;
    *(r4) = r0;
    *((r4 + 4)) = sb;
}
