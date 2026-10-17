
uint fcn.00106f9c(uint param_1,uint param_2,uint param_3,uint param_4,uint32_t param_5,int param_6)

{
    int iVar1;
    uint uVar2;
    bool bVar3;
    uint uStack_20;
    int iStack_1c;
    uint uStack_18;
    uint uStack_14;
    
    if (param_5 == 0) {
        param_5 = *(*0x107024 + 0x98);
    }
    bVar3 = param_6 == 0;
    if (bVar3) {
        param_6 = *0x107028;
    }
    iVar1 = *(*0x107028 + param_5 * 4);
    if (bVar3) {
        param_6 = *(param_6 + 0x1c);
    }
    if (iVar1 == 0) {
        uStack_20 = 1;
        iStack_1c = 2;
        uStack_18 = 0;
        uStack_14 = 0;
        fcn.00122908(param_6,&uStack_20,0);
        return 0;
    }
    uStack_20 = param_4;
    iStack_1c = param_6;
    uVar2 = fcn.0010d6f8(iVar1,param_1,param_2,param_3);
    return uVar2;
}

