/* r2dec pseudo code output (r2 6.0.7) */
/* code_text_unpacked.bin @ 0x6d6f04 */
#include <stdint.h>
 
#define BIT_MASK(t,v) ((t)(-((v)!= 0)))&(((t)-1)>>((sizeof(t)*CHAR_BIT)-(v)))
 
void fcn_006d6f04 (int32_t arg1, int32_t arg2) {
    int32_t var_8h;
    int32_t var_ch;
    int32_t var_10h;
    int32_t var_14h;
    int32_t var_18h;
    int32_t var_1ch;
    int32_t var_20h;
    int32_t var_a0h;
    int32_t var_2ach;
    int32_t var_2b4h;
    int32_t var_2b8h;
    int32_t var_2c0h;
    int32_t var_2c8h;
    int32_t var_2cch;
    int32_t var_2d0h;
    int32_t var_2d4h;
    int32_t var_2d8h;
    int32_t var_2dch;
    int32_t var_2ech;
    r0 = arg1;
    r1 = arg2;
    r4 = r0;
    sl = r3;
    void (*0x6d8298)(uint32_t) (r0);
    *((r4 + 0x44)) = fp;
    r0 = *((sp + 0x2ec));
    void (*0x300e60)(uint32_t) (r0);
    sb = *(0x006d73dc);
    r5 = r0 + 1;
    r0 = *(sb);
    r0 = void (*0x300e60)(uint32_t) (r0);
    r0 += r5;
    r6 = r0 + 1;
    r0 = *((sb + 4));
    r0 = void (*0x300e60)(uint32_t) (r0);
    r0 += r5;
    r7 = r0 + 1;
    r0 = *((sb + 8));
    r0 = void (*0x300e60)(uint32_t) (r0);
    r1 = r0 + r5;
    r8 = r1 + 1;
    r0 = r6 + r7;
    r0 += r8;
    r0 += r5;
    r2 = 0x10;
    r1 = 3;
    r0 = void (*0x121ca0)(uint32_t, uint32_t, uint32_t) (r0, r1, r2);
    *((r4 + 0x48)) = r0;
    if (r0 == 0) {
        goto label_1;
    }
    r1 = *((sp + 0x2ec));
    r2 = r6;
    void (*0x1317dc)(uint32_t, uint32_t) (r1, r2);
    r0 = *((r4 + 0x48));
    r1 = *(sb);
    r2 = r6;
    void (*0x1316bc)(uint32_t, uint32_t, uint32_t) (r0, r1, r2);
    r0 = *((r4 + 0x48));
    r2 = r7;
    r0 += r6;
    *((r4 + 0x4c)) = r0;
    r1 = *((sp + 0x2ec));
    void (*0x1317dc)(uint32_t, uint32_t, uint32_t) (r0, r1, r2);
    r0 = *((r4 + 0x4c));
    r1 = *((sb + 4));
    r2 = r7;
    void (*0x1316bc)(uint32_t, uint32_t, uint32_t) (r0, r1, r2);
    r0 = *((r4 + 0x4c));
    r2 = r8;
    r0 += r7;
    *((r4 + 0x50)) = r0;
    r1 = *((sp + 0x2ec));
    void (*0x1317dc)(uint32_t, uint32_t, uint32_t) (r0, r1, r2);
    r0 = *((r4 + 0x50));
    r1 = *((sb + 8));
    r2 = r8;
    void (*0x1316bc)(uint32_t, uint32_t, uint32_t) (r0, r1, r2);
    r0 = *((r4 + 0x50));
    r2 = r5;
    r0 += r8;
    *((r4 + 0x54)) = r0;
    r1 = *((sp + 0x2ec));
    void (*0x1317dc)(uint32_t, uint32_t, uint32_t) (r0, r1, r2);
    r1 = 0;
    *((r4 + 0x5c)) = sl;
    r3 = ~0;
    *((r4 + 0x1bc)) = r1;
    *((r4 + 0x1bd)) = r3;
    r2 = r1;
    *((r4 + 0x1be)) = r3;
    do {
        r0 = r2 + (r2 << 2);
        r2++;
        r0 = r4 + (r0 << 2);
        *((r0 + 0x80)) = r1;
        *((r0 + 0x7c)) = r3;
        *((r0 + 0x84)) = r1;
        *((r0 + 0x8c)) = r1;
        *((r0 + 0x8e)) = r1;
        *((r0 + 0x8f)) = r1;
        *((r0 + 0x88)) = r1;
    } while (r2 < 0x10);
    sl = *(0x006d73e0);
    r6 = 0;
    r7 = r1;
label_0:
    r5 = *(0x6d73e0);
    r4 = r6 + (r6 << 2);
    r0 = r5 + (r4 << 2);
    *((sp + 0x2c8)) = r0;
    *((r0 + 8)) = fp;
    if (r6 == 4) {
        r0 = void (*0x1079f8)(uint32_t) (r0);
        if (r0 != 0) {
            r0 = r5 - 0x1c;
            r2 = 0x80;
            r1 = *((r0 + 0x18));
            r0 = sp + 0x20;
            void (*0x11026c)(uint32_t, uint32_t, uint32_t) (r0, r1, r2);
            r1 = r5 + 0;
            r0 = 2;
            *((r1 + 0x58)) = r0;
        }
    } else {
        r0 = *(0x6d73d8);
        r2 = 0x80;
        r1 = *(0x6d73ec);
        r0 = sp + 0x20;
        void (*0x11026c)(uint32_t, uint32_t, uint32_t) (r0, r1, r2);
    }
    r1 = *((sp + 0x2ec));
    r2 = 0x80;
    r0 = sp + 0x20;
    void (*0x1316bc)(uint32_t, uint32_t, uint32_t) (r0, r1, r2);
    r0 = sp + 0x20;
    r0 = void (*0x300e60)(uint32_t) (r0);
    r1 = r0;
    r2 = sp + 0x20;
    sb = 0x80 - r1;
    r8 = r2 + r1;
    *((sp + 0xc)) = r7;
    *((sp + 0x10)) = r7;
    *((sp + 0x14)) = r7;
    *((sp + 0x18)) = r7;
    *((sp + 0x1c)) = r7;
    r0 = sp + 8;
    *((sp + 8)) = r2;
    r2 = *(0x6d73b4);
    r1 = *(0x6d73f0);
    *((r0 + r2)) = r1;
    offset_0 = r4 << 2;
    r1 = *((r5 + offset_0));
    r2 = sb;
    r0 = r8;
    void (*0x11026c)(uint32_t, uint32_t, uint32_t) (r0, r1, r2);
    r0 = r8;
    void (*0x300e60)(uint32_t) (r0);
    r2 = sb - r0;
    r0 += r8;
    *((sp + 0x2ac)) = r0;
    *((sp + 0x2cc)) = r2;
    r1 = *(0x6d73e4);
    void (*0x11026c)(uint32_t, uint32_t, uint32_t) (r0, r1, r2);
    r0 = 1;
    *((sp + 0x2dc)) = r0;
    r0 = sp + 0xc;
    *((sp + 0x2d8)) = r0;
    sb = sp + 0x20;
    r8 = sp + 0xa0;
    r0 = sp + 0x2d0;
    *((sp + 0x2d0)) = r7;
    *((sp + 0x2d4)) = r7;
    void (*0x100718)(uint32_t) (r0);
    do {
        r2 = sp + 0x2d0;
        r4 = sl;
        r1 = sl;
        r0 = sb;
        r0 = void (*0x10072a)(uint32_t, uint32_t, uint32_t) (r0, r1, r2);
        r5 = r0;
        if (r5 == r0) {
            goto label_2;
        }
        r2 = r0;
        r3 = sp + 0x2d0;
        r1 = sb;
        r0 = r8;
        r0 = void (*0x100748)(uint32_t, uint32_t, uint32_t, uint32_t) (r0, r1, r2, r3);
        if (r0 == 0) {
            r8 += 2;
        }
        if (r0 == 0) {
            sb += r5;
        }
    } while (r0 != 0);
label_2:
    r3 = sp + 0x2d8;
    *(r8) = r7;
    r0 = *(r3);
    r2 = *((r3 + 4));
    r1 = sp + 0xa0;
    *((r0 + 0xc)) = r7;
    *((r0 + 0x10)) = r7;
    *((r0 + 4)) = r7;
    *((r0 + 8)) = r7;
    r0 = void (*0x5ebed0)(uint32_t, uint32_t) (r1, r3);
    r0 >>= 0x1f;
    if (r0 != r0) {
        r0 = *((sp + 0xc));
        r0 = BIT_MASK (r0, 1);
        if (r0 == r0) {
            goto label_3;
        }
        r0 = *((sp + 0xc));
        __asm ("blne 0x124730");
        r0 = *((sp + 0xc));
        r0 = BIT_MASK (r0, 1);
        void (*0x5ec684)() ();
        goto label_4;
    }
    r0 = sp + 0xc;
    r1 = sp + 0x2b8;
    r0 = void (*0x7316a0)(uint32_t, uint32_t) (r0, r1);
    r1 = r0 >> 0x1f;
    r2 = pc;
    if (r1 == r0) {
        r1 = r2;
    }
    __asm ("blne 0x110ccc");
    r1 = *((sp + 0x2c8));
    r0 = *((sp + 0x2b8));
    *((r1 + 0xc)) = r0;
    r0 = *((sp + 0xc));
    r0 = BIT_MASK (r0, 1);
    if (r1 != r0) {
        r0 = *((sp + 0xc));
        __asm ("blne 0x124730");
        r0 = *((sp + 0xc));
        r0 = BIT_MASK (r0, 1);
        void (*0x5ec684)() ();
        *((sp + 0xc)) = r7;
    }
    r0 = *(0x6d73d8);
    r2 = *((sp + 0x2cc));
    r1 = *(0x6d73e8);
    r0 = *((sp + 0x2ac));
    void (*0x1317dc)(uint32_t, uint32_t, uint32_t) (r0, r1, r2);
    r0 = 1;
    *((sp + 0x2b4)) = r0;
    r8 = sp + 0x20;
    sb = sp + 0xc;
    r5 = sp + 0xa0;
    r0 = sp + 0x2d0;
    *((sp + 0x2d0)) = r7;
    *((sp + 0x2d4)) = r7;
    void (*0x100718)(uint32_t) (r0);
    sl = r4;
    do {
        r2 = sp + 0x2d0;
        r1 = sl;
        r0 = r8;
        r0 = void (*0x10072a)(uint32_t, uint32_t, uint32_t) (r0, r1, r2);
        r4 = r0;
        if (r4 == r0) {
            goto label_5;
        }
        r2 = r0;
        r3 = sp + 0x2d0;
        r1 = r8;
        r0 = r5;
        r0 = void (*0x100748)(uint32_t, uint32_t, uint32_t, uint32_t) (r0, r1, r2, r3);
        if (r0 == 0) {
            r5 += 2;
        }
        if (r0 == 0) {
            r8 += r4;
        }
    } while (r0 != 0);
label_5:
    *(r5) = r7;
    r2 = *((sp + 0x2b4));
    *((sb + 0xc)) = r7;
    *((sb + 0x10)) = r7;
    *((sb + 4)) = r7;
    r1 = sp + 0xa0;
    r0 = sb;
    *((sb + 8)) = r7;
    r0 = void (*0x5ebed0)(uint32_t, uint32_t, uint32_t) (r0, r1, r2);
    r0 >>= 0x1f;
    if (r0 != r0) {
        r0 = *((sp + 0xc));
        r0 = BIT_MASK (r0, 1);
        if (r0 == r0) {
            goto label_3;
        }
        r0 = *((sp + 0xc));
        __asm ("blne 0x124730");
        r0 = *((sp + 0xc));
        r0 = BIT_MASK (r0, 1);
        void (*0x5ec684)() ();
    } else {
        r0 = sp + 0xc;
        r1 = sp + 0x2c0;
        r0 = void (*0x7316a0)(uint32_t, uint32_t) (r0, r1);
        r1 = r0 >> 0x1f;
        r2 = pc;
        if (r1 == r0) {
            r1 = r2;
        }
        __asm ("blne 0x110ccc");
        r1 = *((sp + 0x2c8));
        r0 = *((sp + 0x2c0));
        *((r1 + 0x10)) = r0;
        r0 = *((sp + 0xc));
        r0 = BIT_MASK (r0, 1);
        if (r1 != r0) {
            r0 = *((sp + 0xc));
            __asm ("blne 0x124730");
            r0 = *((sp + 0xc));
            r0 = BIT_MASK (r0, 1);
            void (*0x5ec684)() ();
            *((sp + 0xc)) = r7;
        }
        r0 = *((sp + 0xc));
        r0 = BIT_MASK (r0, 1);
        if ((r0 & 1) == 0) {
            goto label_3;
        }
        r0 = *((sp + 0xc));
        __asm ("blne 0x124730");
        r0 = *((sp + 0xc));
        r0 = BIT_MASK (r0, 1);
        void (*0x5ec684)() ();
    }
label_4:
    *((sp + 0xc)) = r7;
label_3:
    r6++;
    if (r6 < 5) {
        goto label_0;
    }
label_1:
}
