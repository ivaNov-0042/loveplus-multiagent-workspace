/* r2dec pseudo code output (r2 6.0.7) */
/* code_text_unpacked.bin @ 0x300e60 */
#include <stdint.h>
 
uint32_t fcn_00300e60 (int32_t arg1) {
    r0 = arg1;
    r3 = r0 + 1;
    while ((r0 & 3) != 0) {
        r1 = *(r0);
        r0++;
        if (r1 != 0) {
            r0 -= r3;
        }
        if (r1 != 0) {
            return r0;
        }
        if ((r0 & 3) != 0) {
            r2 = *(0x00300ebc);
        }
    }
    do {
        r1 = *(r0);
        r0 += 4;
        __asm ("uqsub8 r1, r2, r1");
    } while (r1 == 0);
    r2 = r1 << 0x18;
    r0 -= r3;
    if (r2 == r1) {
        r0 -= 3;
    }
    if (r2 == r1) {
        return r0;
    }
    r2 = r1 << 0x10;
    if (r2 == r1) {
        r0 -= 2;
    }
    if (r2 == r1) {
        return r0;
    }
    r1 <<= 8;
    if (r1 == r1) {
        r0--;
    }
    return r0;
}
