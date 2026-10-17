
uint fcn.006d8bb0(int param_1)

{
    char cVar1;
    int iVar2;
    uchar *puVar3;
    ushort *puVar4;
    uint *puVar5;
    int *piVar6;
    char *pcVar7;
    bool bVar8;
    char *apcStack_a8 [2];
    uint uStack_a0;
    uint uStack_9c;
    uint uStack_98;
    uint uStack_94;
    uint uStack_90;
    uint uStack_8c;
    uint uStack_88;
    uint uStack_84;
    uint uStack_80;
    uint uStack_7c;
    ushort uStack_70;
    uchar uStack_6e;
    ushort uStack_6a;
    
    iVar2 = func_0x00600738();
    if (iVar2 < 0) {
        func_0x00124730();
    }
    iVar2 = func_0x00600d14();
    if (iVar2 < 0) {
        func_0x00124730();
    }
    iVar2 = func_0x00611e08();
    puVar5 = *0x6d8e78;
    if (iVar2 < 0) {
        func_0x00124730();
    }
    *(param_1 + 0x44) = 0;
    pcVar7 = *puVar5;
    func_0x007234e8(apcStack_a8);
    uStack_7c = puVar5[1];
    uStack_a0 = *0x6d8e7c;
    uStack_9c = *0x6d8e80;
    uStack_98 = *0x6d8e84;
    uStack_94 = *0x6d8e88;
    uStack_90 = *0x6d8e8c;
    uStack_8c = *0x6d8e90;
    uStack_88 = *0x6d8e94;
    uStack_84 = *0x6d8e98;
    uStack_70 = 0;
    uStack_6e = 1;
    uStack_80 = *0x6d8e9c;
    uStack_6a = 1;
    apcStack_a8[0] = pcVar7;
    func_0x00677a54(apcStack_a8);
    puVar3 = func_0x00116d5c(*0x6d8ea0,3,0x10);
    if (puVar3 != NULL) {
        *puVar3 = 0x7f;
        puVar3[1] = 0x7f;
        puVar3[2] = 0x7f;
        puVar3[3] = 0x4b;
        puVar3[4] = 1;
    }
    *(param_1 + 0x44) = puVar3;
    iVar2 = 0;
    puVar4 = puVar3 + 8;
    do {
        *(puVar4 + 4) = 0xffffffff;
        *puVar4 = 0;
        puVar4[1] = 0;
        *(puVar4 + 0x18) = 0;
        *(puVar4 + 0x1a) = 0;
        *(puVar4 + 8) = 0xffffffff;
        *(puVar4 + 10) = 0xffffffff;
        *(puVar4 + 0xc) = 0;
        *(puVar4 + 0xe) = 0;
        *(puVar4 + 0x10) = 0;
        *(puVar4 + 0x12) = 0;
        *(puVar4 + 0x14) = 0xffffffff;
        *(puVar4 + 0x16) = 0x7fffffff;
        iVar2 = iVar2 + 1;
        puVar4 = puVar4 + 0x1c;
    } while (iVar2 < 0x10);
    iVar2 = 0;
    puVar5 = *(param_1 + 0x44) + 0x388;
    do {
        *puVar5 = 0xffffffff;
        puVar5[1] = 0;
        *(puVar5 + 2) = 0;
        puVar5[4] = 0xffffffff;
        puVar5[5] = 0xffffffff;
        puVar5[6] = 0;
        puVar5[7] = 0;
        iVar2 = iVar2 + 1;
        puVar5 = puVar5 + 8;
    } while (iVar2 < 0x10);
    *(*(param_1 + 0x44) + 0x588) = 1;
    *(*(param_1 + 0x44) + 0x589) = 0;
    *(*(param_1 + 0x44) + 0x58a) = 0;
    *(*(param_1 + 0x44) + 0x590) = 0xffffffff;
    iVar2 = *(param_1 + 0x44);
    *(iVar2 + 0x598) = 0xffffffff;
    *(iVar2 + 0x59c) = 0xffffffff;
    *(*(param_1 + 0x44) + 0x5a0) = 0;
    *(*(param_1 + 0x44) + 0x58e) = 0;
    *(*(param_1 + 0x44) + 0x58b) = 0;
    *(*(param_1 + 0x44) + 0x58c) = 0;
    *(*(param_1 + 0x44) + 0x5b0) = 0xff;
    *(*(param_1 + 0x44) + 0x58d) = 0;
    *(*(param_1 + 0x44) + 0x5b4) = 0;
    cVar1 = *pcVar7;
    if (cVar1 != '\0') {
        do {
            pcVar7 = pcVar7 + 1;
            bVar8 = cVar1 != '/';
            if (bVar8) {
                cVar1 = *pcVar7;
            }
        } while (bVar8 && cVar1 != '\0');
    }
    iVar2 = func_0x00116d5c(0x920,0,0x10);
    if (iVar2 != 0) {
        piVar6 = func_0x006d880c();
        if ((piVar6 == NULL) || (iVar2 = func_0x00115f98(piVar6,param_1,0xffffffff,0), iVar2 != 0))
        goto code_r0x006d8e3c;
        (**(*piVar6 + 4))(piVar6);
    }
    piVar6 = NULL;
code_r0x006d8e3c:
    *(*(param_1 + 0x44) + 0x5a4) = piVar6;
    func_0x006d6f04(piVar6,0,pcVar7,0);
    return 1;
}

