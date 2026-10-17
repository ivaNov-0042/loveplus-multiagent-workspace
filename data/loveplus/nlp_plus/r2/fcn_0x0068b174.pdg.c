
void fcn.0068b174(int param_1,uint32_t param_2,uint param_3)

{
    int iVar1;
    uint32_t uVar2;
    uint uVar3;
    
    if ((*(param_1 + 0x356ac) & 1 << (param_2 & 0xff)) != 0) {
        iVar1 = param_1 + param_2 * 0x14;
        uVar3 = *(param_1 + param_2 * 4 + 0x34c18);
        fcn.00142568(uVar3,*(iVar1 + 0x3409c),*(iVar1 + 0x34098),1 < *(iVar1 + 0x340a0));
        iVar1 = param_1 + param_2 * 0x48;
        uVar2 = fcn.00142440(uVar3);
        *(iVar1 + 0x34348) = 0xffffffff;
        *(iVar1 + 0x34344) = 0;
        *(iVar1 + 0x34320) = uVar2 >> 1;
        *(iVar1 + 0x34328) = 0xffffffff;
        *(iVar1 + 0x34354) = *(param_1 + 0x356a8);
        *(iVar1 + 0x34358) = uVar3;
        fcn.001424fc(uVar3,param_3);
        *(iVar1 + 0x3435c) = param_3;
    }
    return;
}

