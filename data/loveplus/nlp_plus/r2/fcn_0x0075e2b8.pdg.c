
void fcn.0075e2b8(int16_t *param_1,uint32_t *param_2,int param_3,int param_4,int param_5,int param_6)

{
    int16_t iVar1;
    uint32_t uVar2;
    int16_t *piVar3;
    uint16_t uVar4;
    int iVar5;
    ushort *puVar6;
    int iVar7;
    int iVar8;
    int iVar9;
    ushort *puVar10;
    uint *puVar11;
    uint32_t uVar12;
    int *piVar13;
    uint32_t uVar14;
    uint32_t uVar15;
    uint32_t unaff_r8;
    int iVar16;
    int iVar17;
    bool bVar18;
    int iStack_78;
    ushort *puStack_68;
    int iStack_64;
    int iStack_5c;
    int aiStack_58 [5];
    int iStack_44;
    int iStack_40;
    int iStack_3c;
    int16_t *piStack_34;
    uint32_t *puStack_30;
    int iStack_2c;
    int iStack_28;
    
    uVar2 = *0x75e684;
    iStack_3c = 0;
    iStack_5c = 0;
    iStack_44 = param_3;
    piStack_34 = param_1;
    puStack_30 = param_2;
    iStack_2c = param_3;
    iStack_28 = param_4;
    do {
        piVar3 = piStack_34;
        iStack_78 = *(param_5 + iStack_5c * 4);
        iVar5 = *(iStack_28 + iStack_5c * 4);
        puVar6 = param_6 + iStack_5c * 0x28;
        if (iStack_78 < 7) {
            iVar7 = *(*0x75e688 + iStack_78 * 4);
            iVar8 = *(*0x75e68c + iStack_78 * 4);
            iVar16 = *(*0x75e690 + iStack_78 * 4);
            iStack_3c = 0;
            uVar14 = 0;
            uVar15 = 0;
            iStack_64 = 0;
            if (0 < iVar7) {
                unaff_r8 = *0x75e694 + iStack_78 * 0x40;
                puStack_68 = puVar6;
                iStack_40 = iStack_78;
code_r0x0075e378:
                iVar9 = 0;
                do {
                    if (piVar3[4] < 1) goto code_r0x0075e550;
                    iVar1 = piVar3[1];
                    uVar12 = *piVar3 + -1;
                    if (uVar12 < 0) {
                        uVar12 = 0xf;
                        iVar1 = **(piVar3 + 2);
                        piVar3[1] = iVar1;
                        *(piVar3 + 2) = *(piVar3 + 2) + 1;
                    }
                    *piVar3 = uVar12;
                    piVar3[4] = piVar3[4] + -1;
                    iVar9 = *(iVar16 + ((iVar1 >> (uVar12 & 0xff) & 1U) + iVar9 * 2) * 4);
                } while (0 < iVar9);
                iVar9 = func_0x00766338(-iVar9,aiStack_58,iStack_40);
                if (iVar9 <= piVar3[4]) break;
code_r0x0075e550:
                iStack_3c = 1;
                iVar7 = (iStack_2c - iStack_5c) - 1;
                if (0 < iVar7) {
                    puVar11 = param_5 + iStack_5c * 4;
                    if ((iStack_2c - iStack_5c & 1U) == 0) {
                        puVar11 = puVar11 + 1;
                        *puVar11 = 7;
                    }
                    for (iVar7 = iVar7 >> 1; iVar7 != 0; iVar7 = iVar7 + -1) {
                        puVar11[1] = 7;
                        puVar11 = puVar11 + 2;
                        *puVar11 = 7;
                    }
                }
                iStack_78 = 7;
                goto code_r0x0075e50c;
            }
        }
code_r0x0075e500:
        if (4 < iStack_78) {
code_r0x0075e50c:
            iVar7 = 0;
            iVar5 = *(*0x75e698 + iStack_78 * 4 + -0x14) * iVar5 + 0x4000;
            if (iVar5 >> 0x1e == iVar5 >> 0x1f) {
                uVar4 = iVar5 >> 0xf;
            }
            else {
                uVar4 = uVar2 ^ iVar5 >> 0x1f;
            }
            do {
                iVar8 = 5;
                uVar12 = param_2[2];
                uVar14 = *param_2;
                iVar5 = param_2[3] + uVar14;
                uVar15 = iVar5 - (iVar5 * 0x10000 >> 0x1f) & 0xffff;
                param_2[2] = param_2[1];
                param_2[3] = uVar12;
                *param_2 = uVar15;
                param_2[1] = uVar14;
                puVar10 = puVar6 + -1;
                do {
                    if (iStack_78 != 7) {
                        unaff_r8 = puVar10[1];
                    }
                    if (iStack_78 == 7 || unaff_r8 == 0) {
                        if ((uVar15 & 1) == 0) {
                            puVar10[1] = -uVar4;
                        }
                        else {
                            puVar10[1] = uVar4;
                        }
                        uVar15 = uVar15 >> 1;
                        if (iStack_78 != 7) goto code_r0x0075e5f0;
code_r0x0075e618:
                        bVar18 = (uVar15 & 1) != 0;
                        if (bVar18) {
                            puVar10[2] = uVar4;
                        }
                        uVar15 = uVar15 >> 1;
                        if (!bVar18) {
                            puVar10[2] = -uVar4;
                        }
                    }
                    else {
code_r0x0075e5f0:
                        unaff_r8 = puVar10[2];
                        if (unaff_r8 == 0) goto code_r0x0075e618;
                    }
                    iVar8 = iVar8 + -1;
                    puVar10 = puVar10 + 2;
                } while (iVar8 != 0);
                iVar7 = iVar7 + 1;
                puVar6 = puVar6 + 10;
            } while (iVar7 < 2);
        }
        iStack_5c = iStack_5c + 1;
        iStack_44 = iStack_44 + -1;
        if (iStack_44 == 0) {
            if (iStack_3c != 0) {
                piStack_34[4] = piStack_34[4] + -1;
            }
            return;
        }
    } while( true );
    if (iVar9 != 0) {
        uVar14 = 0;
        uVar15 = uVar14;
        if (0 < iVar9) {
            do {
                iVar1 = piVar3[1];
                uVar12 = *piVar3 + -1;
                if (uVar12 < 0) {
                    uVar12 = 0xf;
                    iVar1 = **(piVar3 + 2);
                    piVar3[1] = iVar1;
                    *(piVar3 + 2) = *(piVar3 + 2) + 1;
                }
                *piVar3 = uVar12;
                uVar15 = uVar15 + 1;
                uVar14 = (iVar1 >> (uVar12 & 0xff) & 1U) + uVar14 * 2;
                piVar3[4] = piVar3[4] + -1;
            } while (uVar15 < iVar9);
        }
        uVar15 = 1 << (iVar9 - 1U & 0xff);
    }
    if (0 < iVar8) {
        puVar10 = puStack_68;
        iVar9 = iVar8;
        piVar13 = aiStack_58;
        do {
            iVar17 = *(unaff_r8 + *piVar13 * 4) * iVar5 + 0x800;
            if (iVar17 >> 0x1b == iVar17 >> 0x1f) {
                uVar12 = iVar17 >> 0xc;
            }
            else {
                uVar12 = uVar2 ^ iVar17 >> 0x1f;
            }
            if (0 < uVar12) {
                if ((uVar14 & uVar15) == 0) {
                    uVar12 = -uVar12;
                }
                uVar15 = uVar15 >> 1;
            }
            iVar9 = iVar9 + -1;
            *puVar10 = uVar12;
            puVar10 = puVar10 + 1;
            piVar13 = piVar13 + 1;
        } while (iVar9 != 0);
        puStack_68 = puStack_68 + iVar8;
    }
    iStack_64 = iStack_64 + 1;
    if (iVar7 <= iStack_64) goto code_r0x0075e500;
    goto code_r0x0075e378;
}

