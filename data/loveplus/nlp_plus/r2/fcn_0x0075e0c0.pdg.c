
void fcn.0075e0c0(int16_t *param_1,uint32_t param_2,uint *param_3,int *param_4)

{
    int16_t iVar1;
    int *piVar2;
    uint *puVar3;
    int iVar4;
    int *piVar5;
    int iVar6;
    int iVar7;
    int unaff_r9;
    uint32_t uVar8;
    int aiStack_90 [28];
    
    aiStack_90[0] = 0;
    piVar5 = aiStack_90;
    iVar7 = 0;
    do {
        iVar1 = param_1[1];
        uVar8 = *param_1 + -1;
        if (uVar8 < 0) {
            uVar8 = 0xf;
            iVar1 = **(param_1 + 2);
            param_1[1] = iVar1;
            *(param_1 + 2) = *(param_1 + 2) + 1;
        }
        *param_1 = uVar8;
        iVar7 = iVar7 + 1;
        aiStack_90[0] = (iVar1 >> (uVar8 & 0xff) & 1U) + aiStack_90[0] * 2;
    } while (iVar7 < 5);
    aiStack_90[0] = aiStack_90[0] + -7;
    if (1 < param_2) {
        unaff_r9 = *0x75e2b0;
    }
    param_1[4] = param_1[4] + -5;
    iVar7 = 1;
    if (1 < param_2) {
        do {
            iVar6 = 0;
            do {
                iVar1 = param_1[1];
                uVar8 = *param_1 + -1;
                if (uVar8 < 0) {
                    uVar8 = 0xf;
                    iVar1 = **(param_1 + 2);
                    param_1[1] = iVar1;
                    *(param_1 + 2) = *(param_1 + 2) + 1;
                }
                *param_1 = uVar8;
                iVar6 = *(unaff_r9 + iVar7 * 0xb8 + iVar6 * 8 + (iVar1 >> (uVar8 & 0xff) & 1U) * 4);
                param_1[4] = param_1[4] + -1;
            } while (0 < iVar6);
            aiStack_90[iVar7] = -iVar6;
            iVar7 = iVar7 + 1;
        } while (iVar7 < param_2);
    }
    *param_4 = aiStack_90[0];
    if (0 < param_2 - 1) {
        piVar2 = param_4 + -1;
        if ((param_2 & 1) == 0) {
            piVar5 = aiStack_90 + 1;
            param_4[1] = aiStack_90[0] + aiStack_90[1] + -0xc;
            piVar2 = param_4;
        }
        for (iVar7 = param_2 - 1 >> 1; iVar7 != 0; iVar7 = iVar7 + -1) {
            iVar6 = piVar2[1] + piVar5[1] + -0xc;
            piVar2[2] = iVar6;
            piVar5 = piVar5 + 2;
            piVar2[3] = iVar6 + *piVar5 + -0xc;
            piVar2 = piVar2 + 2;
        }
    }
    iVar7 = *0x75e2b4;
    if (0 < param_2) {
        puVar3 = param_3 + -1;
        piVar5 = param_4 + -1;
        if ((param_2 & 1) != 0) {
            iVar6 = *param_4 + 0x18;
            if (0x35 < iVar6) {
                iVar6 = 0x35;
            }
            *param_3 = *(*0x75e2b4 + iVar6 * 4);
            puVar3 = param_3;
            piVar5 = param_4;
        }
        for (iVar6 = param_2 >> 1; iVar6 != 0; iVar6 = iVar6 + -1) {
            iVar4 = piVar5[1] + 0x18;
            if (0x35 < iVar4) {
                iVar4 = 0x35;
            }
            puVar3[1] = *(iVar7 + iVar4 * 4);
            piVar5 = piVar5 + 2;
            iVar4 = *piVar5 + 0x18;
            if (0x35 < iVar4) {
                iVar4 = 0x35;
            }
            puVar3 = puVar3 + 2;
            *puVar3 = *(iVar7 + iVar4 * 4);
        }
    }
    return;
}

