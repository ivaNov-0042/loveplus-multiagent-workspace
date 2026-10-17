
void fcn.0075c500(int *param_1,int param_2,int *param_3,int param_4,uint32_t param_5,int param_6,int param_7)

{
    int *piVar1;
    int iVar2;
    uint32_t uVar3;
    int *piVar4;
    int iVar5;
    int iVar6;
    int iVar7;
    int iVar8;
    int iVar9;
    int iVar10;
    int iVar11;
    int iVar12;
    bool bVar13;
    int aiStack_260 [64];
    int aiStack_160 [28];
    int aiStack_f0 [35];
    int iStack_64;
    int iStack_58;
    int iStack_54;
    int iStack_50;
    int iStack_4c;
    int *piStack_48;
    int *piStack_44;
    int *piStack_34;
    int iStack_30;
    int *piStack_2c;
    int iStack_28;
    
    iVar7 = 0;
    iVar5 = 0;
    iVar6 = 0;
    bVar13 = param_5 == 1;
    if (param_5 < 2) {
        uVar3 = 1;
        iVar2 = param_2;
    }
    else {
        uVar3 = param_5;
        iVar2 = param_5 - 1;
    }
    iVar8 = param_5 - 1;
    if (param_5 >= 2) {
        bVar13 = iVar2 == 0;
        iVar8 = iVar2;
    }
    if (!bVar13 && iVar8 < 0 == (param_5 < 2 && SBORROW4(param_5,1))) {
        piVar1 = param_1 + -1;
        if ((uVar3 & 1) == 0) {
            iVar7 = *(*0x75c7d4 + *param_1 * 4);
            piVar1 = param_1;
        }
        iVar8 = piVar1[1];
        iVar10 = 0;
        for (iVar2 = iVar2 >> 1; iVar2 != 0; iVar2 = iVar2 + -1) {
            iVar11 = iVar8 * 4;
            iVar8 = piVar1[3];
            iVar7 = iVar7 + *(*0x75c7d4 + iVar11);
            iVar10 = iVar10 + *(*0x75c7d4 + piVar1[2] * 4);
            piVar1 = piVar1 + 2;
        }
        iVar7 = iVar7 + iVar10;
    }
    if (-1 < uVar3 - 1) {
        iVar7 = iVar7 + *(*0x75c7d4 + param_1[uVar3 - 1] * 4);
    }
    iStack_58 = param_5 << 2;
    piStack_34 = param_1;
    iStack_30 = param_2;
    piStack_2c = param_3;
    iStack_28 = param_4;
    func_0x0030004c(aiStack_f0,param_1,iStack_58);
    func_0x0030004c(aiStack_160,piStack_34,iStack_58);
    iVar2 = param_6 + -1;
    if (iVar2 < 2) {
        iVar2 = 1;
    }
    iStack_50 = param_6;
    iVar8 = 1;
    iStack_54 = param_6;
    iStack_64 = iVar2 + 1;
    if (1 < iVar2 + 1) {
        iStack_4c = iStack_28 << 1;
        piStack_48 = aiStack_f0 + (param_5 - 0x1e);
        piStack_44 = piStack_2c + (param_5 - 2);
        iVar2 = iVar7;
        do {
            if (iStack_4c < iVar2 + iVar7) {
                iVar11 = param_5 - 1;
                iVar10 = -0x80;
                if ((aiStack_f0[param_5 - 0x1d] < 7) &&
                   (iVar9 = (param_7 - piStack_2c[iVar11]) + aiStack_f0[param_5 - 0x1d] * -2, -0x80 < iVar9)) {
                    iVar10 = iVar9;
                    iVar5 = iVar11;
                }
                if (0 < iVar11) {
                    iVar9 = 0;
                    piVar1 = piStack_48;
                    piVar4 = piStack_44;
                    do {
                        if ((*piVar1 < 7) && (iVar12 = (param_7 - *piVar4) + *piVar1 * -2, iVar10 < iVar12)) {
                            iVar5 = (param_5 - 2) - iVar9;
                            iVar10 = iVar12;
                        }
                        iVar11 = iVar11 + -1;
                        piVar1 = piVar1 + -1;
                        piVar4 = piVar4 + -1;
                        iVar9 = iVar9 + 1;
                    } while (iVar11 != 0);
                }
                aiStack_260[iStack_50] = iVar5;
                iStack_50 = iStack_50 + 1;
                iVar10 = aiStack_f0[iVar5 + -0x1c];
                iVar11 = *(*0x75c7d4 + iVar10 * 4);
                if (iVar10 < 7) {
                    iVar10 = iVar10 + 1;
                }
                aiStack_f0[iVar5 + -0x1c] = iVar10;
                iVar2 = *(*0x75c7d4 + iVar10 * 4) + (iVar2 - iVar11);
            }
            else {
                iVar10 = 0x80;
                uVar3 = param_5;
                if (param_5 < 2) {
                    uVar3 = 1;
                }
                piVar4 = aiStack_f0;
                iVar11 = 0;
                piVar1 = piStack_2c;
                do {
                    if ((0 < *piVar4) && (iVar9 = (param_7 - *piVar1) + *piVar4 * -2, iVar9 < iVar10)) {
                        iVar10 = iVar9;
                        iVar6 = iVar11;
                    }
                    uVar3 = uVar3 - 1;
                    piVar4 = piVar4 + 1;
                    piVar1 = piVar1 + 1;
                    iVar11 = iVar11 + 1;
                } while (uVar3 != 0);
                iStack_54 = iStack_54 + -1;
                aiStack_260[iStack_54] = iVar6;
                iVar10 = aiStack_f0[iVar6];
                iVar11 = *(*0x75c7d4 + iVar10 * 4);
                if (0 < iVar10) {
                    iVar10 = iVar10 + -1;
                }
                aiStack_f0[iVar6] = iVar10;
                iVar7 = *(*0x75c7d4 + iVar10 * 4) + (iVar7 - iVar11);
            }
            iVar8 = iVar8 + 1;
        } while (iVar8 < iStack_64);
    }
    func_0x0030004c(piStack_34,aiStack_f0,iStack_58);
    func_0x0030004c(iStack_30,aiStack_260 + iStack_54,param_6 * 4 + -4);
    return;
}

