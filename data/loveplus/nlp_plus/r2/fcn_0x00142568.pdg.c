
int fcn.00142568(int param_1,int param_2,int param_3,int param_4)

{
    int iVar1;
    uint uVar2;
    int iVar3;
    int iVar4;
    int iVar5;
    int iVar6;
    
    uVar2 = 0;
    if (param_1 == 0) {
        param_1 = func_0x0075c3b8(1,*0x1426b8);
        uVar2 = 1;
        if (param_1 == 0) {
            return 0;
        }
    }
    iVar5 = *0x1426bc * param_3 >> 0x20;
    *(*0x1426c0 + param_1) = uVar2;
    *(param_1 + 0x1440) = param_3;
    *(param_1 + 0x1448) = (iVar5 >> 4) - (iVar5 >> 0x1f);
    *(param_1 + 0x1444) = param_2;
    *(param_1 + 0x1450) = param_4;
    if (param_2 == 7000) {
        *(param_1 + 0x144c) = 0xe;
        *(param_1 + 0x1464) = 0x140;
    }
    else if (param_2 == 14000) {
        iVar5 = *0x1426c4 + 0x18;
        *(*0x1426c4 + param_1) = 0x1c;
        *(iVar5 + param_1) = 0x280;
    }
    else {
        func_0x00124730();
    }
    iVar4 = *(param_1 + 0x1450);
    iVar6 = 1;
    iVar5 = iVar4 + 1;
    if (iVar5 < 2) {
        iVar5 = 1;
    }
    if (1 < iVar5 + 1) {
        do {
            iVar3 = param_1 + iVar4 * 0x10;
            *(*0x1426c8 + iVar3) = 1;
            iVar1 = iVar4 * 4;
            *(iVar3 + 0x1424) = 1;
            *(iVar3 + 0x1428) = 1;
            iVar6 = iVar6 + 1;
            *(iVar3 + 0x142c) = 1;
            iVar4 = iVar4 + -1;
            *(param_1 + iVar1 + 0x145c) = 0x7f;
        } while (iVar6 < iVar5 + 1);
    }
    *(*0x1426cc + param_1) = 0x7f;
    return param_1;
}

