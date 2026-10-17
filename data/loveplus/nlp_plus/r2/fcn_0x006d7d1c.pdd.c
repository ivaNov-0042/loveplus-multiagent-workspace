/* r2dec pseudo code output (r2 6.0.7) */
/* code_text_unpacked.bin @ 0x6d7d1c */
#include <stdint.h>
 
#define SWAP32(n) ((uint32_t) (((n & 0x000000ff) << 24) | \
                               ((n & 0x0000ff00) <<  8) | \
                               ((n & 0x00ff0000) >>  8) | \
                               ((n & 0xff000000) >> 24)))
#define BIT_MASK(t,v) ((t)(-((v)!= 0)))&(((t)-1)>>((sizeof(t)*CHAR_BIT)-(v)))
 
void fcn_006d7d1c (int32_t arg1) {
    int32_t var_8h;
    r0 = arg1;
    r4 = r0;
    r8 = r4 + 0x800;
    r0 = *((r0 + 0x1bc));
    r1 = r4 + 0x1ec;
    sb = 0;
    r8 += 0xf4;
    if (r0 == 0) {
        goto label_1;
    }
    if (r0 != 2) {
        r5 = r1;
        r0 = r1 + 0x710;
        void (*0x11611c)(uint32_t) (r0);
        r6 = *((r5 + 0x708));
        r0 = r5 + 0x710;
        void (*0x116288)(uint32_t) (r0);
        if (r6 <= 0) {
            goto label_2;
        }
    }
    r0 = *((r4 + 0x1bc));
    r5 = 0;
    r7 = r4 + 0x100;
    __asm ("cmpne r0, 7");
    if (r0 != 6) {
        r0 = *((r7 + 0xbd));
        if (r0 < 0) {
            goto label_3;
        }
        r0 += (r0 << 2);
        r0 = r4 + (r0 << 2);
        r5 = r0 + 0x7c;
    }
label_3:
    r0 = 0;
    *((sp + 8)) = r0;
    r1 = *((r4 + 0x1bc));
    sl = 1;
    if (r1 == 2) {
        goto label_4;
    }
    if (r1 != 8) {
        r6 = r4 + 0x1ec;
        r0 = fp;
        void (*0x11611c)(uint32_t) (r0);
        r0 = r6 + 0x710;
        void (*0x11611c)(uint32_t) (r0);
        r0 = *((r6 + 0x708));
        r0--;
        *(r8) = r0;
        r0 = *(r6);
        r1 = *((r0 + 0x14));
        r8 = *((r0 + 4));
        fp = *((r0 + 0xc));
        *(r6) = r1;
        r1 = *((r0 + 0x14));
        if (r1 == 0) {
            r2 = *((r0 + 0x18));
        }
        if (r1 == 0) {
            *((r1 + 0x18)) = r2;
        }
        r1 = *((r0 + 0x18));
        if (r1 == 0) {
            r2 = *((r0 + 0x14));
        }
        if (r1 == 0) {
            *((r1 + 0x14)) = r2;
        }
        *((r0 + 0x14)) = sb;
        *((r0 + 0x18)) = sb;
        r1 = *((r6 + 4));
        if (r1 != 0) {
            *((r6 + 4)) = r0;
        }
        if (r1 != 0) {
            *((r0 + 0x14)) = r1;
            r1 = *((r6 + 4));
            *((r1 + 0x18)) = r0;
            *((r6 + 4)) = r0;
        }
        r0 = r6 + 0x710;
        void (*0x116288)(uint32_t, uint32_t) (r0, r1);
        r0 = r6 + 0x720;
        void (*0x116288)(uint32_t) (r0);
        r1 = *((r4 + 0x1bc));
        r0 = fp;
        if (r1 == 2) {
            goto label_4;
        }
        if (r1 == 8) {
            goto label_5;
        }
        if (r8 == 0) {
            goto label_4;
        }
        __asm ("cmpne r1, 7");
        if (r1 == 6) {
            goto label_6;
        }
    }
label_5:
    if (r5 == 0) {
        *((r5 + 0x13)) = sl;
    }
    if (r5 == 0) {
        goto label_7;
    }
    goto label_8;
    do {
label_1:
        r0 = r4 + 0x800;
        r5 = r4 + 0x1ec;
        r0 += 0xfc;
        void (*0x11611c)(uint32_t) (r0);
        r6 = *((r5 + 0x708));
        r0 = r5 + 0x710;
        void (*0x116288)(uint32_t) (r0);
        if (r6 <= 0) {
            goto label_2;
        }
        r5 = r4 + 0x1ec;
        r0 = fp;
        void (*0x11611c)(uint32_t) (r0);
        r0 = r5 + 0x710;
        void (*0x11611c)(uint32_t) (r0);
        r0 = *((r5 + 0x708));
        r0--;
        *(r8) = r0;
        r0 = *(r5);
        r1 = *((r0 + 0x14));
        *(r5) = r1;
        r1 = *((r0 + 0x14));
        if (r1 == 0) {
            r2 = *((r0 + 0x18));
        }
        if (r1 == 0) {
            *((r1 + 0x18)) = r2;
        }
        r1 = *((r0 + 0x18));
        if (r1 == 0) {
            r2 = *((r0 + 0x14));
        }
        if (r1 == 0) {
            *((r1 + 0x14)) = r2;
        }
        *((r0 + 0x14)) = sb;
        *((r0 + 0x18)) = sb;
        r1 = *((r5 + 4));
        if (r1 != 0) {
            *((r5 + 4)) = r0;
        }
        if (r1 != 0) {
            *((r0 + 0x14)) = r1;
            r1 = *((r5 + 4));
            *((r1 + 0x18)) = r0;
            *((r5 + 4)) = r0;
        }
        r0 = r5 + 0x710;
        void (*0x116288)(uint32_t, uint32_t) (r0, r1);
        r0 = r5 + 0x720;
        void (*0x116288)(uint32_t) (r0);
    } while (1);
label_6:
    r2 = *((r4 + 0x64));
    r1 = *((r4 + 0x60));
    r0 = ~0x13;
    r2 += (r2 << 2);
    r0 += (r2 << 2);
    r6 = r1 + r0;
    *(r6) = sb;
    r0 = *((r6 + 4));
    if (r0 != 0) {
        void (*0x2fcd88)(uint32_t) (r0);
        *((r6 + 4)) = sb;
    }
    r0 = *((r6 + 8));
    if (r0 != 0) {
        goto label_9;
    }
    goto label_0;
label_4:
    r1 &= 0xff;
    r8 = r4 + 0x1ec;
    if (r1 >= 8) {
        /* switch table (8 cases) at 0x6d7fa8 */
        offset_0 = r1 << 2;
        pc = *((pc + offset_0));
    }
    goto label_10;
    r1 = *((r4 + 0x78));
    if (r0 != r1) {
        *((r4 + 0x78)) = sb;
    }
    if (r0 != r1) {
        goto label_2;
    }
    fp = *((r4 + 0x1e4));
    r6 = *((r4 + 0x1e8));
    if (r6 == 0) {
        goto label_0;
    }
    r0 = r6;
    r3 = 0x10;
    r1 = r4 + 0x7c;
    r2 = r4 + 0x84;
    do {
        ip = *(r1);
        r1 += 0x14;
        if (ip == 1) {
            ip = *(r2);
        }
        r2 += 0x14;
        if (ip == 1) {
            r0 += ip;
        }
        r3--;
    } while (r3 != r3);
    if (r0 < 0x60000) {
        r0 = 2;
    }
    if (r0 < 0x60000) {
        *((r4 + 0x1bc)) = r0;
    }
    if (r0 >= 0x60000) {
        goto label_2;
    }
    r2 = 0x10;
    r1 = 3;
    r0 = r6;
    r0 = void (*0x121ca0)(uint32_t, uint32_t, uint32_t) (r0, r1, r2);
    *((r5 + 4)) = r0;
    if (r0 != 0) {
        *((r5 + 0x13)) = sl;
    }
    if (r0 != 0) {
        *((r5 + 8)) = r6;
        r3 = *(r5);
        r2 = *((r4 + 0x44));
        r1 = *((r4 + 0x4c));
        if (r3 == 1) {
            r3 &= 0xff000000;
        }
        __asm ("cmpne r3, 0x10000000");
        if (r3 >= 1) {
            r2 = *((r4 + 0x5c));
            r1 = *(0x6d8290);
        }
        *(sp) = r2;
        *((sp + 4)) = r8;
        r3 = fp;
        r2 = r6;
        void (*0x106f9c)(uint32_t, uint32_t, uint32_t) (r1, r2, r3);
        r1 = 3;
        *((r5 + 0xc)) = r0;
        *((r4 + 0x1bc)) = r1;
label_10:
        r0 = *((sp + 8));
        if (r0 == 0) {
            goto label_2;
        }
    }
label_0:
    if (r5 != 0) {
label_8:
        *((r5 + 0x12)) = sl;
    }
label_7:
    r0 = *((r4 + 0x58));
    r1 = 0xff;
    *((r4 + 0x1bd)) = r1;
    *((r4 + 0x1bc)) = sb;
    if (r0 != 0) {
        void (*0x2fcd88)(uint32_t, uint32_t) (r1, r0);
        *((r4 + 0x58)) = sb;
    }
    r2 = *((r7 + 0xbe));
    r0 = r4;
    r1 = 0;
    do {
        r2++;
        r3 = r1 + (r1 << 2);
        r3 = r0 + (r3 << 2);
        if (r2 < 0x10) {
            r2 = 0;
        }
        ip = *((r3 + 0x7c));
        if (ip != 1) {
            r3 = *((r3 + 0x8e));
            if (r3 == 0) {
                goto label_11;
            }
        }
        r1++;
    } while (r1 < 0x10);
    goto label_2;
    r1 = *((r5 + 0xc));
    if (r0 == r1) {
        *((r5 + 0xc)) = sb;
        goto label_12;
    }
    if (r0 == r1) {
label_12:
        goto label_0;
    }
    goto label_2;
    *((r4 + 0x1bf)) = sl;
    goto label_0;
    *((r4 + 0x1c0)) = sl;
    goto label_0;
    r1 = *((r4 + 0x78));
    if (r0 != r1) {
        goto label_2;
    }
    r2 = *((r4 + 0x64));
    r1 = *((r4 + 0x60));
    r0 = ~0x13;
    r2 += (r2 << 2);
    r0 += (r2 << 2);
    r6 = r1 + r0;
    r0 = *((r6 + 4));
    if (r0 != 0) {
        r1 = *(r6);
        if (r1 == 0) {
            goto label_13;
        }
        r1 = *(r0);
        if (r1 != 0x53) {
            goto label_13;
        }
        r1 = *((r0 + 1));
        if (r1 != 0x44) {
            r1 = *((r0 + 2));
        }
        __asm ("cmpeq r1, 0x4e");
        if (r1 != 0x44) {
            r1 = *((r0 + 3));
        }
        __asm ("cmpeq r1, 0x4d");
        if (r1 == 0x44) {
            goto label_14;
        }
    }
label_13:
    r0 = *((r6 + 4));
    *(r6) = sb;
    if (r0 != 0) {
        void (*0x2fcd88)(uint32_t, uint32_t) (r1, r0);
        *((r6 + 4)) = sb;
    }
    r0 = *((r6 + 8));
    if (r0 == 0) {
        goto label_0;
    }
label_9:
    r1 = 3;
    void (*0x129ed4)(uint32_t) (r1);
    *((r6 + 8)) = sb;
    goto label_0;
label_14:
    r2 = *((r0 + 8));
    r1 = *((r0 + 0xb));
    r2 = SWAP32 (r2);
    r2 = BIT_MASK (r2, 0xff);
    r1 |= r2;
    *((r6 + 0xc)) = r1;
    r0 = *((r0 + 0xc));
    __asm ("rev16 r0, r0");
    *((r6 + 0x10)) = r0;
    r0 = *((r7 + 0xbd));
    if (r0 == 0) {
        *((r4 + 0x1c1)) = sl;
        goto label_15;
    }
    if (r0 == 0) {
label_15:
        goto label_0;
    }
    r0 = *(r6);
    r0 = *(r0);
    r0 = void (*0x300e60)(uint32_t) (r0);
    r5 = r0;
    r0 = *((r7 + 0xbd));
    if (r0 >= 0) {
        r0 = *((r4 + 0x54));
        r0 = void (*0x300e60)(uint32_t) (r0);
        r5 += r0;
    }
    r7 = *(0x6d8290);
    r0 = *(0x6d82a0);
    r0 = void (*0x300e60)(uint32_t) (r0);
    r2 = r0 + 1;
    r0 = *((r4 + 0x58));
    r1 = *(0x6d82a0);
    r0 += r5;
    void (*0x1317dc)(uint32_t, uint32_t, uint32_t) (r0, r1, r2);
    r0 = *(r6);
    r3 = 0;
    r1 = *((r0 + 8));
    *(sp) = r1;
    *((sp + 4)) = r8;
    r2 = *((r0 + 0x10));
    r1 = *((r4 + 0x58));
    r0 = *((r6 + 8));
    void (*0x106f9c)(uint32_t, uint32_t, uint32_t, uint32_t) (r0, r1, r2, r3);
    r1 = 7;
    *((r4 + 0x78)) = r0;
    *((r4 + 0x1bc)) = r1;
    goto label_2;
label_11:
    void (*0x6d854c)(uint32_t, uint32_t) (r1, r0);
label_2:
    r0 = 1;
}
