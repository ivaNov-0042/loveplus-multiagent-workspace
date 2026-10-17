/* r2dec pseudo code output (r2 6.0.7) */
/* code_text_unpacked.bin @ 0x1316bc */
#include <stdint.h>
 
void fcn_001316bc (int32_t arg1, int32_t arg2) {
    r0 = arg1;
    r1 = arg2;
    r3 = r1;
    r2 += r0;
    r2--;
    if ((r0 & 3) != 0) {
        goto label_2;
    }
    do {
        if (ip > r2) {
            ip = *(r0);
        }
        __asm ("uqsub8ls ip, lr, ip");
        __asm ("cmpls ip, 0");
        if (ip != r2) {
            r0 += 4;
        }
        if (ip != r2) {
            r3 -= 4;
        }
    } while (ip == r2);
    do {
label_2:
        if (r0 > r2) {
            goto label_3;
        }
        ip = *(r0);
        if (ip == 0) {
            r0++;
        }
        if (ip == 0) {
            r3--;
        }
    } while (ip != 0);
label_3:
    r5 = 0;
    if ((ip & 3) == 0) {
        goto label_4;
    }
    do {
        if (r2 < r0) {
            goto label_5;
        }
        ip = *(r1);
        if (ip == 0) {
            r1++;
        }
        if (ip == 0) {
            *(r0) = ip;
            r0++;
        }
    } while (ip != 0);
label_5:
    *(r0) = r5;
    while (r0 != 0) {
        r0 = *(r1);
        if (r0 == 0) {
            r1++;
        }
    }
label_0:
    r0 = r1 - r3;
    do {
label_4:
        ip = *(r1);
        r4 = r0 + 4;
        __asm ("uqsub8ls r4, lr, ip");
        __asm ("cmpls r4, 0");
        if (r4 != r2) {
            r1 += 4;
        }
        if (r4 != r2) {
            *(r0) = ip;
            r0 += 4;
        }
    } while (r4 == r2);
    do {
        r4 = *(r1);
        __asm ("uqsub8 r4, lr, r4");
        if (r4 != 0) {
            r1 += 4;
        }
    } while (r4 == 0);
    do {
        if (lr == 0) {
            r1++;
        }
    } while (lr != 0);
label_1:
    if (r0 == r2) {
        *(r0) = r5;
        goto label_6;
    }
    if (r0 >= r2) {
label_6:
        goto label_0;
    }
    lr = ip & 0xff;
    if (lr == ip) {
    }
    if (lr != ip) {
        goto label_1;
    }
    goto label_0;
}
