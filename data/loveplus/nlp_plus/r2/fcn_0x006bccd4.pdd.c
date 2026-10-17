/* r2dec pseudo code output (r2 6.0.7) */
/* code_text_unpacked.bin @ 0x6bccd4 */
#include <stdint.h>
 
#define BIT_MASK(t,v) ((t)(-((v)!= 0)))&(((t)-1)>>((sizeof(t)*CHAR_BIT)-(v)))
 
void fcn_006bccd4 (int32_t arg1) {
    int32_t var_4h;
    int32_t var_8h;
    int32_t var_10h;
    int32_t var_18h;
    int32_t var_28h;
    int32_t var_2ch;
    r0 = arg1;
    r4 = r0;
    r0 = 1;
    r0 = void (*0x6a2844)(uint32_t) (r0);
    r5 = r0;
    r6 = *((r0 += 0x54));
    r1 = *((r4 + 0x48));
    r2 = r1 ^ r6;
    r1 &= r2;
    *((r4 + 0x4c)) = r1;
    r1 = r4 + 0x44;
    r2 &= r6;
    *(r1) = r2;
    *((r1 + 4)) = r6;
    r1 = 0;
    r0 = *((r0 + 8));
    *((r4 + 0x50)) = r0;
    r0 = r5;
    r0 = void (*0x74141c)(uint32_t, uint32_t, uint32_t) (r0, r1, r2);
    r7 = r0;
    r0 = *(r0);
    r1 = 0;
    *((r4 + 0x64)) = r0;
    r0 = *((r7 + 4));
    *((r4 + 0x68)) = r0;
    r0 = r5;
    r0 = void (*0x741404)(uint32_t, uint32_t) (r0, r1);
    r1 = *(r0);
    r5 = r4 + 0x300;
    *((r4 + 0x74)) = r1;
    r3 = *((r0 + 2));
    *((r4 + 0x76)) = r3;
    ip = *((r0 + 4));
    r2 = *((r4 + 0x7c));
    r0 = r2 ^ ip;
    r2 &= r0;
    r0 &= ip;
    *((r4 + 0x7d)) = r0;
    *((r4 + 0x7e)) = r2;
    *((r4 + 0x7c)) = ip;
    r2 = *((r4 + 0x37c));
    r0 = *((r4 + 0x50));
    if (r2 != 0) {
        if (r2 == 2) {
            goto label_1;
        }
        if (r2 == 3) {
            goto label_2;
        }
        r2 = *(r7);
        *((r4 + 0x6c)) = r2;
        r2 = *((r7 + 4));
        *((r4 + 0x70)) = r2;
        if (ip == 0) {
            goto label_3;
        }
        *((r5 + 0x6e)) = r1;
        *((r5 + 0x70)) = r3;
        *((r4 + 0x78)) = r1;
        *((r4 + 0x7a)) = r3;
        goto label_3;
    }
    sb = 0;
    r2 = *(lr);
    r8 = r2;
    if (r8 == r2) {
        goto label_4;
    }
    do {
        if ((r8 & r6) == 0) {
            r8 = *((lr + 4));
        }
        if ((r8 & r6) == 0) {
            sb |= r8;
        }
        r8 = *((lr += 8));
    } while (r8 != 0);
label_4:
    lr = BIT_MASK (r6, 0xf0000000);
    lr = BIT_MASK (lr, 0xf0);
    r6 = sb | lr;
    r8 = 0;
    if (r2 == 0) {
        goto label_5;
    }
    do {
        if ((r2 & r0) == 0) {
            r2 = *((lr + 4));
        }
        if ((r2 & r0) == 0) {
            r8 |= r2;
        }
        r2 = *((lr += 8));
    } while (r2 != 0);
label_5:
    r2 = *((r7 + 4));
    r0 = BIT_MASK (r0, 0xf0000000);
    r0 = BIT_MASK (r0, 0xf0);
    *((r4 + 0x6c)) = r2;
    __asm ("vldr s0, [r7]");
    r0 |= r8;
    __asm ("vneg.f32 s0, s0");
    __asm ("vstr s0, [r4, 0x70]");
    if (ip == 0) {
        goto label_3;
    }
    *((r5 + 0x6e)) = r1;
    r2 = r3 - ;
    *((r5 + 0x70)) = r3;
    *((r4 + 0x78)) = r2;
    *((r4 + 0x7a)) = r1;
    goto label_3;
label_1:
    r2 = *(0x6bd2f8);
    sb = 0;
    r8 = *(0x6bd2f8);
    lr = r8;
    if (lr == r8) {
        goto label_6;
    }
    do {
        if ((lr & r6) == 0) {
        }
        if ((lr & r6) == 0) {
            sb |= lr;
        }
    } while (lr != 0);
label_6:
    r2 = BIT_MASK (r6, 0xf0000000);
    r2 = BIT_MASK (r2, 0xf0);
    r6 = sb | r2;
    r2 = *(0x6bd2f8);
    lr = 0;
    if (r8 == 0) {
        goto label_7;
    }
    do {
        if ((r8 & r0) == 0) {
            r8 = *((r2 + 4));
        }
        if ((r8 & r0) == 0) {
            lr |= r8;
        }
        r8 = *((r2 += 8));
    } while (r8 != 0);
label_7:
    __asm ("vldr s0, [r7, 4]");
    r0 = BIT_MASK (r0, 0xf0000000);
    r0 = BIT_MASK (r0, 0xf0);
    __asm ("vneg.f32 s0, s0");
    r0 |= lr;
    __asm ("vstr s0, [r4, 0x6c]");
    r2 = *(r7);
    *((r4 + 0x70)) = r2;
    if (ip == 0) {
        goto label_3;
    }
    *((r5 + 0x6e)) = r1;
    *((r5 + 0x70)) = r3;
    r2 = r1 - ;
    *((r4 + 0x78)) = r3;
    *((r4 + 0x7a)) = r2;
    goto label_3;
label_2:
    sb = 0;
    r2 = *(lr);
    r8 = r2;
    if (r8 == r2) {
        goto label_8;
    }
    do {
        if ((r8 & r6) == 0) {
            r8 = *((lr + 4));
        }
        if ((r8 & r6) == 0) {
            sb |= r8;
        }
        r8 = *((lr += 8));
    } while (r8 != 0);
label_8:
    lr = BIT_MASK (r6, 0xf0000000);
    lr = BIT_MASK (lr, 0xf0);
    r6 = sb | lr;
    r8 = 0;
    if (r2 == 0) {
        goto label_9;
    }
    do {
        if ((r2 & r0) == 0) {
            r2 = *((lr + 4));
        }
        if ((r2 & r0) == 0) {
            r8 |= r2;
        }
        r2 = *((lr += 8));
    } while (r2 != 0);
label_9:
    __asm ("vldr s0, [r7]");
    r0 = BIT_MASK (r0, 0xf0000000);
    r0 = BIT_MASK (r0, 0xf0);
    __asm ("vneg.f32 s0, s0");
    r0 |= r8;
    __asm ("vstr s0, [r4, 0x6c]");
    __asm ("vldr s0, [r7, 4]");
    __asm ("vneg.f32 s0, s0");
    __asm ("vstr s0, [r4, 0x70]");
    if (ip != 0) {
        *((r5 + 0x6e)) = r1;
        r2 = r1 - ;
        *((r5 + 0x70)) = r3;
        *((r4 + 0x78)) = r2;
        *((r4 + 0x7a)) = ip;
    }
label_3:
    r3 = *((r4 + 0x58));
    *((r4 + 0x60)) = r0;
    *((r4 + 0x58)) = r6;
    r0 = r3 ^ r6;
    r0 &= r3;
    *((r4 + 0x5c)) = r0;
    r1 = *(0x6bd300);
    *((r4 + 0x54)) = ip;
    r7 = 1;
    r2 = r4 + 0x380;
    if (r0 == r0) {
        r0 = 1;
    }
    if (r0 == r0) {
    }
    if (r0 == r0) {
        goto label_10;
    }
    do {
        r3 = *((r4 + 0x5c));
        if ((r3 & lr) != 0) {
            r3 = r0 | 0x20;
            lr = BIT_MASK (lr, r7);
            *((lr + r2)) = r3;
            r3 = *((r4 + 0x3c0));
            r3++;
            r3 &= 0xff;
            *((r4 + 0x3c0)) = r3;
            if (r3 >= 0x40) {
                *((r4 + 0x3c0)) = ip;
                goto label_11;
            }
        }
label_11:
        r0++;
        r0 &= 0xff;
    } while (r0 <= 0xd);
label_10:
    r0 = *((r4 + 0x54));
    if (r0 == 0) {
        r0 = 1;
    }
    if (r0 == 0) {
        lr = 0;
    }
    if (r0 == 0) {
        goto label_12;
    }
    do {
        r3 = *((r4 + 0x54));
        offset_0 = r0 << 2;
        ip = *((r1 + offset_0));
        if ((r3 & ip) != 0) {
            r3 = *((r5 + 0xc2));
            r3 |= (r7 << r0);
            *((r5 + 0xc2)) = r3;
            r3 = *((r4 + 0x3c0));
            *((r3 + r2)) = r0;
            r3 = *((r4 + 0x3c0));
            r3++;
            r3 &= 0xff;
            *((r4 + 0x3c0)) = r3;
            if (r3 >= 0x40) {
                goto label_13;
            }
        }
label_13:
        r0++;
        r0 &= 0xff;
    } while (r0 <= 0xd);
label_12:
    r0 = *((r4 + 0x7c));
    if (r0 == 0) {
        goto label_14;
    }
    r0 = sp + 0x10;
    void (*0x69dd18)(uint32_t) (r0);
    __asm ("ldrd r0, r1, [sp, 0x10]");
    __asm ("strd r0, r1, [sp, 8]");
    r0 = sp + 8;
    r0 = void (*0x69de1c)(uint32_t) (r0);
    r2 = r0;
    r0 = r4 + 0x358;
    r0 = *(r0);
    ip = *((r0 + 4));
    r0 |= ip;
    if (r0 == r0) {
        r0 = *((r4 + 0x78));
        *((r5 + 0x6a)) = r0;
        *((r5 + 0x62)) = r0;
        r0 = *((r4 + 0x7a));
        *((r5 + 0x6c)) = r0;
        *((r5 + 0x64)) = r0;
        *((r4 + 0x35c)) = r1;
        *((r4 + 0x358)) = r2;
    }
    r0 = *((r4 + 0x358));
    r3 = *((r4 + 0x7f));
    *((r4 + 0x84)) = ip;
    if (r3 != 0) {
        *((r4 + 0x7f)) = r7;
    }
    if (r3 == 0) {
        goto label_0;
    }
    if (r3 == 1) {
        goto label_15;
    }
    if (r3 == 3) {
        goto label_16;
    }
    sl = *((r4 + 0x78));
    r6 = 0x190;
    r7 = r4 + 0x178;
    *((sp + 4)) = sl;
    fp = *((r4 + 0x7a));
    *((sp + 8)) = fp;
    r0 = *((r5 + 0x60));
    *((sp + 0x2c)) = r0;
    r0 = r4 + 0x88;
    *((sp + 0x28)) = r0;
    r0 = r4 + 0x100;
    *((sp + 0x18)) = r0;
    r0 = *((sp + 0x2c));
    do {
        r8 = r6 >> 0x1f;
        r0--;
        __asm ("sxth r0, r0");
        if (r0 >= 0) {
            r0 = 0x3b;
        }
        ip = *((ip + 4));
        r3 = r2 - lr;
        __asm ("sbc ip, r1, ip");
        r3 = r6 - r3;
        __asm ("sbcs ip, r8, ip");
        if (r3 < r6) {
            goto label_17;
        }
        ip = *((sp + 0x28));
        r3 = *((sp + 0x18));
        r3 += (r0 << 1);
        ip = *(ip);
        r3 = *(r3);
        r3 = fp - r3;
        __asm ("mla ip, r3, r3, ip");
        if (ip > 0x40) {
            goto label_0;
        }
        r3 = *((sp + 0x2c));
    } while (r0 != r3);
label_17:
    r0 = 3;
    *((r4 + 0x7f)) = r0;
    r0 = *((sp + 4));
    *((r5 + 0x6a)) = r0;
    r0 = *((sp + 8));
    *((r5 + 0x6c)) = r0;
    do {
label_0:
        r3 = *((r5 + 0x60));
        r0 = *((r4 + 0x78));
        r3 = r4 + (r3 << 1);
        *((r3 + 0x88)) = r0;
        r0 = *((r5 + 0x60));
        r3 = *((r4 + 0x7a));
        r0 = r4 + (r0 << 1);
        r0 += 0x100;
        *(r0) = r3;
        r0 = *((r5 + 0x60));
        r0 = r4 + (r0 << 3);
        *((r0 += 0x178)) = r2;
        *((r0 + 4)) = r1;
        r0 = *((r5 + 0x60));
        r0++;
        __asm ("sxth r0, r0");
        *((r5 + 0x60)) = r0;
        if (r0 < 0x3c) {
            r0 = 0;
        }
        __asm ("strhge r0, [r5, 0x60]");
        goto label_18;
label_15:
        r3 = *((r4 + 0x78));
        r6 = *((r5 + 0x62));
        r0 = *((r4 + 0x7a));
        r3 -= r6;
        __asm ("smulbb r3, r3, r3");
        r0 -= lr;
        __asm ("smlabb r0, r0, r0, r3");
        if (r0 < 0x40) {
            r0 = 2;
        }
        if (r0 >= 0x40) {
            goto label_19;
        }
        if (ip < 0x190) {
            r0 = 3;
        }
        if (ip < 0x190) {
            *((r4 + 0x7f)) = r0;
        }
    } while (1);
label_16:
    r0 = *((r4 + 0x78));
    r3 = *((r5 + 0x6a));
    ip = *((r4 + 0x7a));
    r3 = r0 - r3;
    __asm ("smulbb r3, r3, r3");
    r0 = ip - lr;
    __asm ("smlabb r0, r0, r0, r3");
    if (r0 >= 0x100) {
        r0 = 4;
        goto label_20;
    }
    if (r0 < 0x100) {
label_20:
        goto label_0;
    }
label_19:
    *((r4 + 0x7f)) = r0;
    goto label_0;
label_14:
    r0 = *((r4 + 0x35c));
    r1 = *((r4 + 0x358));
    r0 |= r1;
    if (r0 != r0) {
        r2 = *((r5 + 0x6e));
        r0 = 0;
        r3 = r4 + 0x358;
        *((r5 + 0x72)) = r2;
        r2 = *((r5 + 0x70));
        r1 = r0;
        *((r5 + 0x74)) = r2;
        r2 = *((r4 + 0x78));
        *((r5 + 0x66)) = r2;
        r2 = *((r4 + 0x7a));
        *((r5 + 0x68)) = r2;
        r2 = *((r4 + 0x84));
        r2++;
        *((r4 + 0x84)) = r2;
        *(r3) = r0;
        *((r3 + 4)) = r1;
    }
    r0 = 0;
    r1 = *((r4 + 0x7f));
    *((r4 + 0x7f)) = r0;
    *((r4 + 0x80)) = r1;
label_18:
    r0 = 1;
}
