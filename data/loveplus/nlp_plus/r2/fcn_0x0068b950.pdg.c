
void fcn.0068b950(int param_1,int param_2,int *param_3)

{
    int iVar1;
    uint32_t uVar2;
    int iVar3;
    
    uVar2 = param_3[2];
    iVar3 = param_3[3];
    iVar1 = *0x68b9a8 << (param_3[1] & 0xffU);
    param_1 = param_1 + param_2 * 0x14;
    *(param_1 + 0x34098) = *param_3 * 800;
    *(param_1 + 0x3409c) = iVar1;
    *(param_1 + 0x340a0) = uVar2 & 0xff;
    *(param_1 + 0x340a4) = iVar3;
    *(param_1 + 0x340a8) = (uVar2 << 0x10) >> 0x18;
    return;
}

