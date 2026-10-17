/* r2dec pseudo code output (r2 6.0.7) */
/* code_text_unpacked.bin @ 0x6d8bb0 */
#include <stdint.h>
 
void fcn_006d8bb0 (int32_t arg1) {
    int32_t var_4h;
    int32_t var_ch;
    int32_t var_10h;
    int32_t var_18h;
    int32_t var_1ch;
    int32_t var_20h;
    int32_t var_24h;
    int32_t var_28h;
    int32_t var_2ch;
    int32_t var_30h;
    int32_t var_34h;
    int32_t var_38h;
    int32_t var_3ch;
    int32_t var_48h;
    int32_t var_4ah;
    int32_t var_4eh;
    r0 = arg1;
    r5 = r0;
    r0 = void (*0x600738)() ();
    r0 >>= 0x1f;
    __asm ("blne 0x124730");
    r0 = void (*0x600d14)(uint32_t) (r0);
    r0 >>= 0x1f;
    __asm ("blne 0x124730");
    void (*0x611e08)(uint32_t) (r0);
    r7 = *(0x6d8e74);
    r0 >>= 0x1f;
    r6 = 0;
    __asm ("blne 0x124730");
    r0 = 0;
    *((sp + 0xc)) = r0;
    *((sp + 4)) = r0;
    *((r5 + 0x44)) = r6;
    r4 = *(0x6d8e74);
    r0 = sp + 0x10;
    void (*0x7234e8)(uint32_t) (r0);
    *((sp + 0x10)) = r4;
    r1 = *(0x6d8e78);
    r0 = 1;
    *((sp + 0x3c)) = r1;
    r1 = *(0x6d8e78);
    *((sp + 0x18)) = r1;
    r1 = *(0x6d8e7c);
    *((sp + 0x1c)) = r1;
    r1 = *(0x6d8e80);
    *((sp + 0x20)) = r1;
    r1 = *(0x6d8e84);
    *((sp + 0x24)) = r1;
    r1 = *(0x6d8e88);
    *((sp + 0x28)) = r1;
    r1 = *(0x6d8e8c);
    *((sp + 0x2c)) = r1;
    r1 = *(0x6d8e90);
    *((sp + 0x30)) = r1;
    r1 = *(0x6d8e94);
    *((sp + 0x34)) = r1;
    r1 = *(0x6d8e98);
    *((sp + 0x48)) = r6;
    *((sp + 0x4a)) = r0;
    *((sp + 0x38)) = r1;
    *((sp + 0x4e)) = r0;
    r0 = sp + 0x10;
    void (*0x677a54)(uint32_t, uint32_t) (r0, r1);
    r0 = *(0x6d8e9c);
    r2 = 0x10;
    r1 = 3;
    r0 = void (*0x116d5c)(uint32_t, uint32_t, uint32_t) (r0, r1, r2);
    if (r0 != 0) {
        r3 = 0x7f;
        *(r0) = r3;
        *((r0 + 1)) = r3;
        r2 = 0x4b;
        *((r0 + 2)) = r3;
        r1 = 1;
        *((r0 + 3)) = r2;
        *((r0 + 4)) = r1;
    }
    *((r5 + 0x44)) = r0;
    r2 = 0;
    r0 += 8;
    lr = r6;
    do {
        r1 = ~0;
        *((r0 + 8)) = r1;
        r7 = 0;
        r1 = r0;
        r3 = ~0;
        r1 += 0x10;
        r6 = r3;
        r8 = r7;
        sb = r7;
        sl = r7;
        *(r1) = r3;
        *((r1 + 4)) = r6;
        *((r1 + 8)) = r7;
        *((r1 + 12)) = r8;
        *((r1 + 16)) = sb;
        *((r1 + 20)) = sl;
        *((r1 + 24)) = fp;
        *((r1 + 28)) = ip;
        r2++;
        r0 += 4;
    } while (r2 < 0x10);
    r0 = *((r5 + 0x44));
    r2 = 0;
    r1 = ~0;
    r0 += 0x388;
    do {
        r3 = ~0;
        *(r0) = r1;
        *((r0 + 4)) = lr;
        r7 = 0;
        r8 = r0 + 0x10;
        r6 = r3;
        *(r8) = r3;
        *((r8 + 4)) = r6;
        *((r8 + 8)) = r7;
        *((r8 + 12)) = ip;
        r2++;
        r0 += 0x20;
    } while (r2 < 0x10);
    r2 = *((r5 + 0x44));
    r0 = 1;
    *((r2 + 0x588)) = r0;
    r0 = *((r5 + 0x44));
    r2 = *((r5 + 0x44));
    r0 = ~0;
    r3 = *((r5 + 0x44));
    r2 = r0;
    *((r3 + 0x590)) = r1;
    r3 = *((r5 + 0x44));
    r3 += 0x400;
    r3 += 0x198;
    *(r3) = r0;
    *((r3 + 4)) = r2;
    r0 = *((r5 + 0x44));
    r0 = *((r5 + 0x44));
    r0 = *((r5 + 0x44));
    r0 = *((r5 + 0x44));
    r0 = *((r5 + 0x44));
    *((r0 + 0x5b0)) = r1;
    r0 = *((r5 + 0x44));
    r0 = *((r5 + 0x44));
    r0 = *(r4);
    if (r0 == 0) {
        goto label_0;
    }
    do {
        r0 &= 0xff;
        r4++;
        if (r0 == 0x2f) {
            r0 = *(r4);
        }
        __asm ("cmpne r0, 0");
    } while (r0 != 0x2f);
label_0:
    r7 = 0;
    r8 = ~0;
    r2 = 0x10;
    r1 = r7;
    r0 = 0x920;
    r0 = void (*0x116d5c)(uint32_t, uint32_t, uint32_t) (r0, r1, r2);
    if (r0 == 0) {
        goto label_1;
    }
    r0 = void (*0x6d880c)(uint32_t) (r0);
    r6 = r0;
    if (r6 == r0) {
        goto label_2;
    }
    r3 = r7;
    r2 = r8;
    r1 = r5;
    r0 = void (*0x115f98)(uint32_t, uint32_t, uint32_t) (r1, r2, r3);
    if (r0 == 0) {
        goto label_3;
    }
    while (1) {
label_1:
        r6 = 0;
label_2:
        r1 = *((r5 + 0x44));
        r0 = r6;
        r2 = r4;
        *((r1 + 0x5a4)) = r6;
        r1 = *((sp + 0xc));
        r3 = *((sp + 4));
        void (*0x6d6f04)(uint32_t, uint32_t, uint32_t, uint32_t) (r0, r1, r2, r3);
        r0 = 1;
label_3:
        r0 = *(r6);
        r1 = *((r0 + 4));
        r0 = r6;
        uint32_t (*r1)(uint32_t, uint32_t) (r0, r1);
    }
}
