
void fcn.006d880c(uint param_1)

{
    uint uVar1;
    uint *puVar2;
    uint32_t uVar3;
    int iVar4;
    int iVar5;
    int iVar6;
    uint *puVar7;
    
    puVar2 = fcn.005e0128(param_1,0x6d8998,0);
    uVar1 = *0x6d89a4;
    puVar2[0x1c] = 0x7fffffff;
    *puVar2 = uVar1;
    *(puVar2 + 0x11) = 0;
    puVar2[0x12] = 0;
    puVar2[0x13] = 0;
    puVar2[0x14] = 0;
    puVar2[0x15] = 0;
    puVar2[0x16] = 0;
    *(puVar2 + 0x17) = 0;
    puVar2[0x18] = 0;
    *(puVar2 + 0x19) = 0;
    puVar2[0x1a] = 0;
    puVar2[0x1b] = 0;
    puVar2[0x1d] = 0;
    *(puVar2 + 0x6f) = 0;
    *(puVar2 + 0x1bd) = 0xff;
    *(puVar2 + 0x1be) = 0xff;
    *(puVar2 + 0x1bf) = 0;
    *(puVar2 + 0x70) = 0;
    uVar1 = *0x6d89a8;
    *(puVar2 + 0x1c1) = 0;
    uVar3 = fcn.001000ac(puVar2 + 0x7d,uVar1,0x1c,0x40);
    iVar4 = func_0x0054909c(uVar3,uVar3 >> 0xc);
    puVar7 = iVar4 + -0x720;
    fcn.0011611c(iVar4 + -0x10);
    *(iVar4 + -0x14) = 0x40;
    *(iVar4 + -0x18) = 0;
    *(iVar4 + -0x71c) = iVar4 + -0x718;
    *puVar7 = 0;
    puVar2 = iVar4 + -0x718;
    iVar6 = 1;
    do {
        iVar5 = iVar6 + 1;
        puVar2[5] = puVar7 + iVar6 * 7 + 2;
        puVar2[6] = puVar7 + iVar6 * 7 + -5;
        puVar2 = puVar7 + iVar6 * 7 + 2;
        iVar6 = iVar5;
    } while (iVar5 < *(iVar4 + -0x14));
    fcn.00116288(iVar4 + -0x10);
    *(iVar4 + 8) = 0;
    *(iVar4 + 0xc) = 0;
    *(iVar4 + 0x10) = 0;
    iVar6 = 0;
    do {
        iVar5 = iVar6 + 1;
        iVar6 = iVar4 + -0x90c + iVar6 * 0x14;
        *(iVar6 + 0x80) = 0;
        *(iVar6 + 0x7c) = 0xffffffff;
        *(iVar6 + 0x84) = 0;
        *(iVar6 + 0x8c) = 0;
        *(iVar6 + 0x8e) = 0;
        *(iVar6 + 0x8f) = 0;
        *(iVar6 + 0x88) = 0;
        iVar6 = iVar5;
    } while (iVar5 < 0x10);
    *(iVar4 + -0x728) = 0;
    *(iVar4 + -0x724) = 0;
    *(iVar4 + -0x748) = 0;
    *(iVar4 + -0x744) = 0;
    *(iVar4 + -0x740) = 0;
    *(iVar4 + -0x73c) = 0;
    *(iVar4 + -0x738) = 0;
    *(iVar4 + -0x734) = 0;
    *(iVar4 + -0x730) = 0;
    *(iVar4 + -0x72c) = 0;
    *(iVar4 + -0x894) = 0;
    return;
}

