
uint fcn.001420dc(int param_1,int param_2,int param_3)

{
    uint32_t uVar1;
    int iVar2;
    uint uVar3;
    int iVar4;
    int iVar5;
    int16_t *piVar6;
    int iVar7;
    uint32_t uVar8;
    int16_t *piVar9;
    int iVar10;
    uint *puVar11;
    int iVar12;
    int iVar13;
    int iStack_48;
    uint32_t uStack_44;
    uint *puStack_40;
    int iStack_3c;
    
    iVar12 = 0;
    iVar10 = 1;
    iVar2 = param_2;
    if (param_2 < 2) {
        iVar2 = 1;
    }
    if (1 < iVar2 + 1) {
        do {
            func_0x0011a4d4(param_1 + iVar12 * 0x500,0x500);
            iVar10 = iVar10 + 1;
            iVar12 = iVar12 + 1;
        } while (iVar10 < iVar2 + 1);
    }
    uVar1 = *0x14242c;
    iStack_48 = 0;
    uStack_44 = 0;
    iStack_3c = 0x20;
    puStack_40 = param_1 + 0xf00;
    do {
        puVar11 = *puStack_40;
        if ((*(param_1 + 0xf84) >> (uStack_44 & 0xff) & 1) == 0) {
            if (puVar11 != NULL) {
                iVar2 = (**puVar11)(puVar11[1]);
                if (iVar2 != 0) {
                    func_0x00142454(puVar11,0,iVar2,puVar11 + 2);
                    if (*(param_1 + 0xf80) == 0) {
                        if (*(*0x142434 + puVar11) != 0) {
                            uVar3 = (**puVar11)(puVar11[1]);
                            func_0x00142454(puVar11,1,uVar3);
                            iVar2 = 0x280;
                            piVar6 = puVar11 + 2;
                            piVar9 = puVar11 + 0x142;
                            do {
                                iVar2 = iVar2 + -1;
                                *piVar6 = *piVar6 + *piVar9 + 1 >> 1;
                                piVar6 = piVar6 + 1;
                                piVar9 = piVar9 + 1;
                            } while (iVar2 != 0);
                        }
                    }
                    else if (*(*0x142434 + puVar11) == 0) {
                        func_0x0030004c(puVar11 + 0x142,puVar11 + 2,0x500);
                    }
                    else {
                        uVar3 = (**puVar11)(puVar11[1]);
                        func_0x00142454(puVar11,1,uVar3,puVar11 + 0x142);
                    }
                    iVar13 = 0;
                    iVar10 = *(*0x142438 + -0xc + puVar11);
                    iVar2 = *(*0x142438 + puVar11) * 0xe >> 4;
                    iVar12 = param_2;
                    if (*(*0x142438 + puVar11) == 0x140) {
                        iVar10 = iVar10 * *0x14243c >> 0xf;
                    }
                    do {
                        iVar4 = puVar11[iVar13 + 0x517];
                        piVar6 = param_1 + iVar13 * 0x500;
                        iVar5 = iVar2;
                        piVar9 = puVar11 + iVar13 * 0x140 + 2;
                        if (iVar2 < 2) {
                            iVar5 = 1;
                        }
                        do {
                            iVar7 = *piVar9 * iVar4 * iVar10 + 0x2000;
                            if (iVar7 >> 0x1d == iVar7 >> 0x1f) {
                                uVar8 = iVar7 >> 0xe;
                            }
                            else {
                                uVar8 = uVar1 ^ iVar7 >> 0x1f;
                            }
                            uVar8 = uVar8 + *piVar6;
                            if (uVar8 >> 0xf != uVar8 >> 0x1f) {
                                uVar8 = uVar1 ^ uVar8 >> 0x1f;
                            }
                            iVar5 = iVar5 + -1;
                            *piVar6 = uVar8;
                            piVar6 = piVar6 + 1;
                            piVar9 = piVar9 + 1;
                        } while (iVar5 != 0);
                        iVar12 = iVar12 + -1;
                        iVar13 = iVar13 + 1;
                    } while (iVar12 != 0);
                }
                iStack_48 = iStack_48 + 1;
            }
        }
        else {
            if (puVar11 != NULL) {
                *(*0x142430 + puVar11) = 1;
                (**puVar11)(puVar11[1]);
            }
            *(param_1 + 0xf84) = *(param_1 + 0xf84) & ~(1 << (uStack_44 & 0xff));
        }
        uStack_44 = uStack_44 + 1;
        iStack_3c = iStack_3c + -1;
        puStack_40 = puStack_40 + 1;
    } while (iStack_3c != 0);
    iVar2 = 0;
    if (iStack_48 == 0 && *(param_1 + 0xf90) == 0) {
        if (param_2 < 2) {
            param_2 = 1;
        }
        iVar10 = 1;
        if (1 < param_2 + 1) {
            do {
                func_0x0011a4d4(*(param_3 + iVar2 * 4),*(param_1 + 0xf88) << 1);
                iVar10 = iVar10 + 1;
                iVar2 = iVar2 + 1;
            } while (iVar10 < param_2 + 1);
        }
    }
    else {
        do {
            func_0x0076b67c(param_1 + iVar2 * 0x500,param_1 + iVar2 * 0x280 + 0xa00,*(param_3 + iVar2 * 4),
                            *(param_1 + 0xf88));
            param_2 = param_2 + -1;
            iVar2 = iVar2 + 1;
        } while (param_2 != 0);
    }
    *(param_1 + 0xf90) = 0 < iStack_48;
    return *(param_1 + 0xf88);
}

