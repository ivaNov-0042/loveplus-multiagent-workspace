
uint fcn.0072314c(int param_1,uint param_2)

{
    uint uVar1;
    int iVar2;
    int iVar3;
    uchar auStack_e8 [96];
    uint uStack_88;
    uint uStack_84;
    ulong uStack_80;
    uchar auStack_78 [16];
    uint uStack_68;
    uint uStack_5c;
    int aiStack_34 [8];
    
    if (*(param_1 + 8) < 0) {
        uVar1 = 0;
    }
    else {
        uStack_80 = func_0x00721db0(*(param_1 + 8),&uStack_88);
        uVar1 = uStack_80;
        if (uStack_80 != -1) {
            uStack_88 = CONCAT31(uStack_88._1_3_,4);
            uStack_68 = *0x72320c;
            uStack_5c = param_2;
            iVar2 = func_0x0071efe0(aiStack_34,param_1);
            iVar3 = 0;
            if (iVar2 != 0) {
                iVar3 = aiStack_34[0];
            }
            if (iVar2 != 0 && iVar3 != 0) {
                func_0x0030004c(auStack_e8,auStack_78,0x60);
                iVar3 = func_0x0071e164(uStack_88,uStack_84,uStack_80,uStack_80._4_4_);
                if (iVar3 != 0) {
                    return uVar1;
                }
            }
        }
        uVar1 = 0xffffffff;
    }
    return uVar1;
}

