// callconv: r0 arm32 (r0, r1);
void fcn.006d6f04 (int32_t arg1, int32_t arg2) {
    loc_0x006d6f04:
        push (r0, r1, r2, r3, r4, r5, r6, r7, r8, sb, sl, fp, lr)
        sp -= 0x2e4
        r4 = r0       // arg1
        sl = r3
        fp = r1       // arg2
        0x6d8298 ()   // 0x6d8298(0x0, 0x0, 0x0, 0x0)
        [r4 + 0x44] = (byte) fp
        r0 = [var_2ech]
        0x300e60 ()   // 0x300e60(0x0, 0x0, 0x0, 0x0)
        sb = [0x006d6f30] // [0x6d73dc:4]=0x8a829c // (pstr 0x00844cc8) "Siren14voice.bin"
        r5 = r0 + 1
        r0 = [sb]     // "Siren14voice.bin"
        0x300e60 ()   // 0x300e60(0x844cc8, 0x0, 0x0, 0x0)
        r0 += r5      // "iren14voice.bin"
        r6 = r0 + 1   // "ren14voice.bin"
        r0 = [sb + 4] // "Siren14Voice.spp"
        0x300e60 ()   // 0x300e60(0x844cfd, 0x0, 0x0, 0x0)
        r0 += r5      // "iren14Voice.spp"
        r7 = r0 + 1   // "ren14Voice.spp"
        r0 = [sb + 8] // "Siren14Voice.dpb"
        0x300e60 ()   // 0x300e60(0x844c88, 0x0, 0x0, 0x0)
        r1 = r0 + r5  // "iren14Voice.dpb"
        r8 = r1 + 1   // "ren14Voice.dpb"
        r0 = r6 + r7
        r0 += r8
        r0 += r5
        r2 = 0x10
        r1 = 3
        0x121ca0 ()   // 0x121ca0(0x18ce654, 0x3, 0x10, 0x0)
        (a, b) = compare (r0, 0)
        [r4 + 0x48] = r0
        je 0x6d73d4   // unlikely
        goto loc_0x006d6f84;
    loc_0x006d73d4:
        sp += 0x2f4
        pop (r4, r5, r6, r7, r8, sb, sl, fp, pc)
        return r0;
    loc_0x006d7024: // orphan
         add r0, r2, r2, lsl 2
         r2 += 1
         add r0, r4, r0, lsl 2
         (a, b) = compare (r2, 0x10)
         [r0 + 0x80] = r1
         [r0 + 0x7c] = r3
         [r0 + 0x84] = r1
         [r0 + 0x8c] = (half) r1
         [r0 + 0x8e] = (byte) r1
         [r0 + 0x8f] = (byte) r1
         [r0 + 0x88] = r1
         blt 0x6d7024             // likely

         goto loc_0x006d7054
    loc_0x006d7054: // orphan
         sl = [0x006d705c]        // [0x6d73e0:4]=261
         r6 = 0
         r7 = r1

         goto loc_0x006d70b0
    loc_0x006d70b0: // orphan
         r0 = [0x006d70b8]        // [0x6d73dc:4]=0x8a829c // (pstr 0x00844cc8) "Siren14voice.bin"
         r2 = 0x80
         r1 = [r0 + 0x14]         // "rom:/"
         r0 = var_20h
         0x11026c ()              // 0x11026c(0x10078020, 0x844c54, 0x80, 0x0)

         goto loc_0x006d71c4
    loc_0x006d71c4: // orphan
         r3 = var_2d8h
         [r8] = (half) r7
         ldm r3, (r0, r2)
         r1 = var_a0h
         [r0 + 0xc] = r7
         [r0 + 0x10] = r7
         [r0 + 4] = r7
         [r0 + 8] = r7
         0x5ebed0 ()              // 0x5ebed0(0x0, 0x100780a0, 0x0, 0x100782d8)
         r0 = r0 >> 0x1f
         je 0x6d7224              // likely

    loc_0x006d7224: // orphan
         r0 = var_ch
         r1 = var_2b8h
         0x7316a0 ()              // 0x7316a0(0x1007800c, 0x100782b8, 0x0, 0x0)
         r1 = r0 >> 0x1f
         r2 = pc
         movne r1, r2
         blne 0x110ccc            // 0x110ccc(0x1007800c, 0x0, 0x6d7234, 0x0)
         r1 = [var_2c8h]
         r0 = [var_2b8h]
         [r1 + 0xc] = r0
         r0 = [var_ch]
         bics r0, r0, 1
         je 0x6d7274              // likely

    loc_0x006d7274: // orphan
         r0 = [0x006d727c]        // [0x6d73dc:4]=0x8a829c // (pstr 0x00844cc8) "Siren14voice.bin"
         r2 = [var_2cch]
         r1 = [r0 + 0x10]         // ".bcsar"
         r0 = [var_2ach]
         0x1317dc ()              // 0x1317dc(0x0, 0x844d53, 0x0, 0x0)
         r0 = 1
         [var_2b4h] = r0
         r8 = var_20h
         sb = var_ch
         r5 = var_a0h
         r0 = var_2d0h
         [var_2d0h] = r7
         [var_2d4h] = r7
         0x100718 ()              // 0x100718(0x100782d0, 0x844d53, 0x0, 0x0)
         sl = r4

         goto loc_0x006d72f0
    loc_0x006d72f0: // orphan
         [r5] = (half) r7
         r2 = [var_2b4h]
         [sb + 0xc] = r7
         [sb + 0x10] = r7
         [sb + 4] = r7
         r1 = var_a0h
         r0 = sb
         [sb + 8] = r7
         0x5ebed0 ()              // 0x5ebed0(0x0, 0x100780a0, 0x1, 0x0)
         r0 = r0 >> 0x1f
         je 0x6d7350              // likely

    loc_0x006d7350: // orphan
         r0 = var_ch
         r1 = var_2c0h
         0x7316a0 ()              // 0x7316a0(0x1007800c, 0x100782c0, 0x0, 0x0)
         r1 = r0 >> 0x1f
         r2 = pc
         movne r1, r2
         blne 0x110ccc            // 0x110ccc(0x1007800c, 0x0, 0x6d7360, 0x0)
         r1 = [var_2c8h]
         r0 = [var_2c0h]
         [r1 + 0x10] = r0
         r0 = [var_ch]
         bics r0, r0, 1
         je 0x6d73a0              // likely

    loc_0x006d73a0: // orphan
         r0 = [var_ch]
         bics r0, r0, 1
         je 0x6d73c8              // likely

    loc_0x006d73c8: // orphan
         r6 += 1
         (a, b) = compare (r6, 5)
         blt 0x6d7060             // likely

    loc_0x006d7060: // orphan
         r5 = [0x006d7068]        // [0x6d73e4:4]=0x8a82b8 // (pstr 0x00844c80) "LP2_CTR"
         add r4, r6, r6, lsl 2
         (a, b) = compare (r6, 4)
         add r0, r5, r4, lsl 2    // (pstr 0x00844c80) "LP2_CTR"
         [var_2c8h] = r0
         [r0 + 8] = (byte) fp
         bne 0x6d70b0             // likely

         goto loc_0x006d73ac
    loc_0x006d73ac: // orphan
         r0 = [var_ch]
         (a, b) = compare (r0, 1)
         blne 0x124730            // 0x124730(0x0, 0x0, 0x0, 0x0)
         r0 = [var_ch]
         bic r0, r0, 1
         0x5ec684 ()              // 0x5ec684(0x0, 0x0, 0x0, 0x0)

         goto loc_0x006d7384
    loc_0x006d7384: // orphan
         r0 = [var_ch]
         (a, b) = compare (r0, 1)
         blne 0x124730            // 0x124730(0x0, 0x0, 0x0, 0x0)
         r0 = [var_ch]
         bic r0, r0, 1
         0x5ec684 ()              // 0x5ec684(0x0, 0x0, 0x0, 0x0)
         [var_ch] = r7

         goto loc_0x006d7320
    loc_0x006d7320: // orphan
         r0 = [var_ch]
         bics r0, r0, 1
         je 0x6d73c8              // likely

         goto loc_0x006d732c
    loc_0x006d732c: // orphan
         r0 = [var_ch]
         (a, b) = compare (r0, 1)
         blne 0x124730            // 0x124730(0x0, 0x0, 0x0, 0x0)
         r0 = [var_ch]
         bic r0, r0, 1
         0x5ec684 ()              // 0x5ec684(0x0, 0x0, 0x0, 0x0)
         
         
    loc_0x006d73c4: // orphan
         // CODE XREFS from fcn.006d6f04 @ 0x6d7220(x), 0x6d734c(x)
         [var_ch] = r7

    loc_0x006d72cc: // orphan
         r2 = r0
         r3 = var_2d0h
         r1 = r8
         r0 = r5
         0x100748 ()              // 0x100748(0x0, 0x0, 0x0, 0x100782d0)
         (a, b) = compare (r0, 0)
         addne r5, r5, 2
         addne r8, r8, r4
         bne 0x6d72b0             // unlikely

    loc_0x006d72b0: // orphan
         r2 = var_2d0h
         r1 = sl
         r0 = r8
         0x10072a ()              // 0x10072a(0x0, 0x0, 0x100782d0, 0x0)
         r4 = r0
         je 0x6d72f0              // likely

         goto loc_0x006d7258
    loc_0x006d7258: // orphan
         r0 = [var_ch]
         (a, b) = compare (r0, 1)
         blne 0x124730            // 0x124730(0x0, 0x0, 0x0, 0x0)
         r0 = [var_ch]
         bic r0, r0, 1
         0x5ec684 ()              // 0x5ec684(0x0, 0x0, 0x0, 0x0)
         [var_ch] = r7

         goto loc_0x006d71f4
    loc_0x006d71f4: // orphan
         r0 = [var_ch]
         bics r0, r0, 1
         je 0x6d73c8              // likely

    loc_0x006d7200: // orphan
         r0 = [var_ch]
         (a, b) = compare (r0, 1)
         blne 0x124730            // 0x124730(0x0, 0x0, 0x0, 0x0)
         r0 = [var_ch]
         bic r0, r0, 1
         0x5ec684 ()              // 0x5ec684(0x0, 0x0, 0x0, 0x0)
         
         
    loc_0x006d71a0: // orphan
         r2 = r0
         r3 = var_2d0h
         r1 = sb
         r0 = r8
         0x100748 ()              // 0x100748(0x0, 0x0, 0x0, 0x100782d0)
         (a, b) = compare (r0, 0)
         addne r8, r8, 2
         addne sb, sb, r5
         bne 0x6d7180             // unlikely

    loc_0x006d7180: // orphan
         r2 = var_2d0h
         r4 = sl
         r1 = sl
         r0 = sb
         0x10072a ()              // 0x10072a(0x0, 0x0, 0x100782d0, 0x0)
         r5 = r0
         je 0x6d71c4              // likely

         goto loc_0x006d707c
    loc_0x006d707c: // orphan
         0x1079f8 ()              // 0x1079f8(0x0, 0x0, 0x0, 0x0)
         (a, b) = compare (r0, 0)
         je 0x6d70b0              // likely

    loc_0x006d708c: // orphan
         r0 = r5 - 0x1c
         r2 = 0x80
         r1 = [r0 + 0x18]
         r0 = var_20h
         0x11026c ()              // 0x11026c(0x10078020, -1, 0x80, 0x0)
         r1 = r5 + 0
         r0 = 2
         [r1 + 0x58] = (byte) r0
         
    loc_0x006d70c4: // orphan
         // CODE XREF from fcn.006d6f04 @ 0x6d70ac(x)
         r1 = [var_2ech]
         r2 = 0x80
         r0 = var_20h
         0x1316bc ()              // 0x1316bc(0x10078020, 0x0, 0x80, 0x0)
         r0 = var_20h
         0x300e60 ()              // 0x300e60(0x10078020, 0x0, 0x80, 0x0)
         r1 = r0
         r2 = var_20h
         rsb sb, r1, 0x80
         r8 = r2 + r1
         r1 = [0x006d70f8]        // [0x6d73e8:4]=0x82bbe0 // (pstr 0x0082bc20) "d~^"
         [var_ch] = r7
         [var_10h] = r7
         [var_14h] = r7
         [var_18h] = r7
         [var_1ch] = r7
         r2 = [r1]
         r0 = var_8h
         [var_8h] = r2
         r2 = [r2 - 0x30]
         r1 = [r1 + 0xc]
         [r0 + r2] = r1
         ldr r1, [r5, r4, lsl 2]
         r2 = sb
         r0 = r8
         0x11026c ()              // 0x11026c(0x200f0040, 0xffff0000, 0xeff88060, 0x0)
         r0 = r8
         0x300e60 ()              // 0x300e60(0x200f0040, 0xffff0000, 0xeff88060, 0x0)
         r1 = [0x006d7144]        // [0x6d73dc:4]=0x8a829c // (pstr 0x00844cc8) "Siren14voice.bin"
         r2 = sb - r0
         r0 += r8
         [var_2ach] = r0
         [var_2cch] = r2
         r1 = [r1 + 0xc]          // ".csidbin"
         0x11026c ()              // 0x11026c(0x401e0080, 0x844cf4, 0xcfe98020, 0x0)
         r0 = 1
         [var_2dch] = r0
         r0 = var_ch
         [var_2d8h] = r0
         sb = var_20h
         r8 = var_a0h
         r0 = var_2d0h
         [var_2d0h] = r7
         [var_2d4h] = r7
         0x100718 ()              // 0x100718(0x100782d0, 0x844cf4, 0xcfe98020, 0x0)

}

