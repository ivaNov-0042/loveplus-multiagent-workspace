
void fcn.0075e69c(int16_t *param_1,uint param_2,int param_3,uint param_4)

{
    int *piVar1;
    int16_t iVar2;
    int iVar3;
    uint32_t uVar4;
    int iVar5;
    int iVar6;
    uint uVar7;
    int aiStack_208 [28];
    int aiStack_198 [32];
    uchar auStack_118 [112];
    uchar auStack_a8 [132];
    
    if (param_3 == 0xe) {
        iVar6 = 4;
        uVar7 = 0x10;
    }
    else {
        iVar6 = 5;
        uVar7 = 0x20;
    }
    func_0x0075e0c0(param_1,param_3,auStack_a8,auStack_118);
    iVar5 = 0;
    iVar3 = iVar6;
    do {
        iVar2 = param_1[1];
        uVar4 = *param_1 + -1;
        if (uVar4 < 0) {
            uVar4 = 0xf;
            iVar2 = **(param_1 + 2);
            param_1[1] = iVar2;
            *(param_1 + 2) = *(param_1 + 2) + 1;
        }
        iVar3 = iVar3 + -1;
        iVar5 = (iVar2 >> (uVar4 & 0xff) & 1U) + iVar5 * 2;
        *param_1 = uVar4;
    } while (iVar3 != 0);
    iVar2 = param_1[4] - iVar6;
    param_1[4] = iVar2;
    func_0x0075c3dc(param_3,iVar2,uVar7,auStack_118,aiStack_208,aiStack_198);
    iVar6 = 0;
    while ((0 < iVar5 && (iVar6 < 0x1f))) {
        piVar1 = aiStack_198 + iVar6;
        iVar6 = iVar6 + 1;
        if (aiStack_198[*piVar1 + -0x1c] < 7) {
            iVar5 = iVar5 + -1;
            aiStack_198[*piVar1 + -0x1c] = aiStack_198[*piVar1 + -0x1c] + 1;
        }
    }
    func_0x0075e2b8(param_1,param_2,param_3,auStack_a8,aiStack_208,param_4);
    return;
}

