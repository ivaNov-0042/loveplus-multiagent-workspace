
void fcn.0075dd2c(int16_t *param_1,uint16_t *param_2,int param_3)

{
    uint32_t uVar1;
    int16_t iVar2;
    uint16_t uVar3;
    uint16_t *puVar4;
    uint16_t *puVar5;
    uint16_t *puVar6;
    uint32_t *puVar7;
    uint16_t *puVar8;
    uint16_t *puVar9;
    uint32_t uVar10;
    int iVar11;
    uint32_t uVar12;
    int iVar13;
    int16_t *piVar14;
    int16_t *piVar15;
    int16_t *piVar16;
    uint32_t uVar17;
    uint16_t *puVar18;
    uint16_t uVar19;
    int iVar20;
    uint16_t *puVar21;
    uchar *puVar22;
    int16_t *piVar23;
    int16_t *piVar24;
    uint16_t uVar25;
    uint32_t uVar26;
    int iVar27;
    int iVar28;
    bool bVar29;
    uint16_t auStack_f80 [640];
    uint16_t auStack_a80 [640];
    uchar auStack_580 [1280];
    uint16_t *puStack_80;
    uint16_t *puStack_6c;
    uint32_t uStack_64;
    int iStack_54;
    uint16_t *puStack_50;
    uint *puStack_4c;
    int16_t *piStack_30;
    uint16_t *puStack_2c;
    int iStack_28;
    
    uVar1 = *0x75e0b4;
    if (param_3 == 0x140) {
        puStack_50 = 0x6;
        puVar7 = *0x75e0ac;
    }
    else {
        puStack_50 = 0x7;
        puVar7 = *0x75e0b0;
    }
    puVar9 = auStack_f80 + param_3;
    uVar10 = 0x1f;
    puVar18 = auStack_f80;
    piStack_30 = param_1;
    puStack_2c = param_2;
    iStack_28 = param_3;
    do {
        uVar26 = *puVar7;
        uVar17 = uVar10 - 1;
        piVar14 = param_1 + 1;
        iVar2 = *param_1;
        uVar12 = uVar10 & 0xff;
        param_1 = param_1 + 2;
        uVar10 = uVar10 - 2;
        iVar27 = iVar2 + *piVar14 + (uVar26 >> uVar12 & 1);
        uVar25 = iVar27 >> 1;
        if (uVar10 < 0) {
            uVar10 = 0x1f;
            puVar7 = puVar7 + 1;
        }
        iVar20 = (iVar2 - *piVar14) + (uVar26 >> (uVar17 & 0xff) & 1);
        uVar19 = iVar20 >> 1;
        uVar3 = *0x75e0b4;
        if (iVar27 >> 0x10 != iVar27 >> 0x1f) {
            uVar25 = uVar3 ^ iVar27 >> 0x1f;
        }
        if (iVar20 >> 0x10 != iVar20 >> 0x1f) {
            uVar19 = uVar3 ^ iVar20 >> 0x1f;
        }
        puVar5 = puVar18 + 1;
        *puVar18 = uVar25;
        puVar9 = puVar9 + -1;
        *puVar9 = uVar19;
        puVar18 = puVar5;
    } while (puVar5 < puVar9);
    puStack_80 = auStack_a80;
    puVar18 = 0x1;
    iVar27 = puStack_50 + -2;
    puStack_6c = auStack_f80;
    do {
        puVar9 = puStack_80;
        iVar20 = 1 << (puVar18 & 0xff);
        puVar5 = puStack_80;
        do {
            puVar4 = puVar5;
            puVar21 = puVar5 + (iStack_28 >> (puVar18 & 0xff));
            do {
                puVar8 = puStack_6c + 1;
                uVar25 = *puStack_6c;
                puStack_6c = puStack_6c + 2;
                uVar12 = uVar25 + *puVar8;
                uVar10 = uVar25 - *puVar8;
                if (uVar12 >> 0xf != uVar12 >> 0x1f) {
                    uVar12 = uVar1 ^ uVar12 >> 0x1f;
                }
                if (uVar10 >> 0xf != uVar10 >> 0x1f) {
                    uVar10 = uVar1 ^ uVar10 >> 0x1f;
                }
                puVar8 = puVar4 + 1;
                *puVar4 = uVar12;
                puVar21 = puVar21 + -1;
                *puVar21 = uVar10;
                puVar4 = puVar8;
            } while (puVar8 < puVar21);
            iVar20 = iVar20 + -1;
            puVar5 = puVar5 + (iStack_28 >> (puVar18 & 0xff));
        } while (iVar20 != 0);
        puVar18 = puVar18 + 1;
        bVar29 = puStack_80 == auStack_f80;
        puStack_6c = puStack_80;
        puStack_80 = auStack_f80;
        if (bVar29) {
            puStack_80 = auStack_a80;
        }
        iVar27 = iVar27 + -1;
    } while (iVar27 != 0);
    puVar22 = auStack_580;
    iVar27 = 1 << (puStack_50 - 1U & 0xff);
    if (iVar27 < 2) {
        iVar27 = 1;
    }
    iVar20 = 1;
    if (1 < iVar27 + 1) {
        do {
            puVar18 = NULL;
            iVar28 = 0;
            do {
                iVar11 = 0;
                iVar13 = 10;
                puVar5 = puVar9;
                piVar14 = *0x75e0b8 + puVar18 * 2;
                do {
                    iVar13 = iVar13 + -1;
                    iVar11 = *puVar5 * *piVar14 + iVar11;
                    puVar5 = puVar5 + 1;
                    piVar14 = piVar14 + 1;
                } while (iVar13 != 0);
                uVar12 = iVar11 + 0x4000;
                puVar18 = puVar18 + 5;
                uVar10 = uVar12 >> 0x1f;
                bVar29 = uVar12 >> 0x1e != uVar10;
                if (bVar29) {
                    uVar12 = uVar1 ^ uVar10;
                }
                iVar11 = iVar28 * 2;
                if (!bVar29) {
                    uVar12 = uVar12 >> 0xf;
                }
                iVar28 = iVar28 + 1;
                *(puVar22 + iVar11) = uVar12;
            } while (iVar28 < 10);
            iVar20 = iVar20 + 1;
            puVar22 = puVar22 + 0x14;
            puVar9 = puVar9 + 10;
        } while (iVar20 < iVar27 + 1);
    }
    func_0x00302b20(puStack_6c,auStack_580,iStack_28 << 1);
    uStack_64 = puStack_50 - 2;
    puStack_4c = *0x75e0bc;
    do {
        puStack_50 = puStack_6c;
        iStack_54 = 1 << (uStack_64 & 0xff);
        if (uStack_64 != 0) {
            puVar18 = puStack_80;
        }
        uVar1 = iStack_28 >> (uStack_64 & 0xff);
        if (uStack_64 == 0) {
            puVar18 = puStack_2c;
        }
        puVar9 = puVar18;
        do {
            puVar18 = puVar9 + uVar1;
            puVar4 = puStack_50 + uVar1;
            piVar23 = (uVar1 & 0xfffffffe) + puStack_50;
            piVar14 = *puStack_4c;
            puVar5 = puVar18;
            do {
                piVar24 = piVar23 + 1;
                puVar8 = puStack_50 + 1;
                puVar21 = puVar5 + -1;
                piVar15 = piVar14 + 2;
                iVar20 = (*piVar14 * *puStack_50 - piVar14[1] * *piVar23) + 0x2000;
                iVar27 = *piVar14 * *piVar23 + piVar14[1] * *puStack_50 + 0x2000;
                if (iVar20 >> 0x1d == iVar20 >> 0x1f) {
                    uVar25 = iVar20 >> 0xe;
                }
                else {
                    uVar25 = uVar3 ^ iVar20 >> 0x1f;
                }
                if (iVar27 >> 0x1d == iVar27 >> 0x1f) {
                    uVar19 = iVar27 >> 0xe;
                }
                else {
                    uVar19 = uVar3 ^ iVar27 >> 0x1f;
                }
                puVar6 = puVar9 + 1;
                *puVar9 = uVar25;
                puVar5 = puVar5 + -2;
                *puVar21 = uVar19;
                piVar16 = piVar14 + 3;
                puStack_50 = puStack_50 + 2;
                piVar23 = piVar23 + 2;
                piVar14 = piVar14 + 4;
                iVar20 = *piVar16 * *piVar24 + *piVar15 * *puVar8 + 0x2000;
                iVar27 = (*piVar16 * *puVar8 - *piVar15 * *piVar24) + 0x2000;
                if (iVar20 >> 0x1d == iVar20 >> 0x1f) {
                    uVar25 = iVar20 >> 0xe;
                }
                else {
                    uVar25 = uVar3 ^ iVar20 >> 0x1f;
                }
                if (iVar27 >> 0x1d == iVar27 >> 0x1f) {
                    uVar19 = iVar27 >> 0xe;
                }
                else {
                    uVar19 = uVar3 ^ iVar27 >> 0x1f;
                }
                puVar9 = puVar9 + 2;
                *puVar6 = uVar25;
                *puVar5 = uVar19;
            } while (puVar9 < puVar5);
            iStack_54 = iStack_54 + -1;
            puVar9 = puVar18;
            puStack_50 = puVar4;
        } while (iStack_54 != 0);
        puVar9 = puStack_6c;
        puStack_6c = puStack_80;
        puStack_4c = puStack_4c + 1;
        uStack_64 = uStack_64 - 1;
        puStack_80 = puVar9;
    } while (-1 < uStack_64);
    return;
}

