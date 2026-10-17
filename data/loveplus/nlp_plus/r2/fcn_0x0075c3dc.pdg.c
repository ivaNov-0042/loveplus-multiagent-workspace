
void fcn.0075c3dc(uint32_t param_1,int param_2,uint param_3,int *param_4,int *param_5,uint param_6)

{
    int iVar1;
    int iVar2;
    int iVar3;
    uint32_t uVar4;
    int *piVar5;
    int iVar6;
    int *piVar7;
    int iVar8;
    int iVar9;
    
    iVar1 = *0x75c4fc;
    iVar2 = param_1 * *0x75c4f8 + (param_1 << 0x20) >> 0x20;
    iVar3 = (iVar2 >> 3) - (iVar2 >> 0x1f);
    iVar2 = iVar3 * 0x140;
    iVar6 = param_2;
    if (iVar2 < param_2) {
        iVar6 = iVar2 + ((param_2 + iVar3 * -0x140) * 5 >> 3);
    }
    iVar3 = -0x20;
    iVar2 = 0x20;
    do {
        iVar9 = 0;
        uVar4 = param_1;
        piVar5 = param_4;
        piVar7 = param_5;
        if (0 < param_1) {
            do {
                iVar8 = (iVar3 + iVar2) - *piVar5 >> 1;
                if (iVar8 < 0) {
                    iVar8 = 0;
                }
                else if (7 < iVar8) {
                    iVar8 = 7;
                }
                *piVar7 = iVar8;
                uVar4 = uVar4 - 1;
                iVar9 = iVar9 + *(iVar1 + iVar8 * 4);
                piVar5 = piVar5 + 1;
                piVar7 = piVar7 + 1;
            } while (uVar4 != 0);
        }
        if (iVar6 + -0x20 <= iVar9) {
            iVar3 = iVar3 + iVar2;
        }
        iVar2 = iVar2 >> 1;
    } while (iVar2 != 0);
    piVar5 = param_4;
    piVar7 = param_5;
    uVar4 = param_1;
    if (0 < param_1) {
        do {
            iVar2 = iVar3 - *piVar5 >> 1;
            if (iVar2 < 0) {
                iVar2 = 0;
            }
            else if (7 < iVar2) {
                iVar2 = 7;
            }
            uVar4 = uVar4 - 1;
            *piVar7 = iVar2;
            piVar5 = piVar5 + 1;
            piVar7 = piVar7 + 1;
        } while (uVar4 != 0);
    }
    func_0x0075c500(param_5,param_6,param_4,iVar6,param_1,param_3,iVar3,param_1,param_2,param_3,param_4);
    return;
}

