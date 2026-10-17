
bool fcn.006779ac(int param_1)

{
    int iVar1;
    uint32_t uVar2;
    int iVar3;
    bool bVar4;
    uint uStack_54;
    uint uStack_50;
    uint uStack_4c;
    uint uStack_48;
    uint uStack_44;
    uint uStack_40;
    uint uStack_3c;
    uint uStack_38;
    uint uStack_34;
    uint uStack_30;
    uint uStack_2c;
    uint uStack_28;
    uint uStack_24;
    uint uStack_20;
    uint uStack_1c;
    uint uStack_18;
    uint uStack_14;
    
    bVar4 = *(param_1 + 0x10) != 0;
    iVar1 = 0;
    if (bVar4) {
        iVar1 = *(param_1 + 4);
    }
    if (bVar4 && iVar1 != 0) {
        iVar3 = *(param_1 + 8);
        iVar1 = *(param_1 + 0xc);
        if ((-(iVar1 + (iVar3 != 0)) < 0 != (SBORROW4(0,iVar1) != SBORROW4(-iVar1,iVar3 != 0))) &&
           (((uVar2 = *(param_1 + 0x34), uVar2 < 2 || (uVar2 == 999)) && (uVar2 < 2)))) {
            iVar1 = func_0x00720810(uVar2,0,-iVar3);
            if (iVar1 == 1) {
                func_0x0071e4f8(&uStack_50);
                uStack_54 = 0xffffffff;
            }
            func_0x00302a48(param_1 + 0x14,*(param_1 + 0x10));
            func_0x0071e494(&uStack_50,param_1);
            iVar1 = func_0x0071e3d8(8,uStack_54,uStack_50,uStack_4c,uStack_48,uStack_44,uStack_40,uStack_3c,
                                    uStack_38,uStack_34,uStack_30,uStack_2c,uStack_28,uStack_24,uStack_20,
                                    uStack_1c,uStack_18,uStack_14);
            return iVar1 != 0;
        }
    }
    return false;
}

