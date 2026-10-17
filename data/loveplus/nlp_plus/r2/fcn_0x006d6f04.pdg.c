
//WARNING: Control flow encountered bad instruction data
//WARNING: Removing unreachable block (ram,0x006d707c)
//WARNING: Removing unreachable block (ram,0x006d708c)

void fcn.006d6f04(int param_1,uchar param_2,uint param_3,uchar param_4)

{
    uint *puVar1;
    int iVar2;
    int iVar3;
    int iVar4;
    int iVar5;
    int iVar6;
    
    func_0x006d8298();
    *(param_1 + 0x44) = param_2;
    iVar2 = func_0x00300e60(param_3);
    puVar1 = *0x6d73dc;
    iVar2 = iVar2 + 1;
    iVar3 = func_0x00300e60(**0x6d73dc);
    iVar4 = iVar3 + iVar2 + 1;
    iVar3 = func_0x00300e60(puVar1[1]);
    iVar5 = iVar3 + iVar2 + 1;
    iVar3 = func_0x00300e60(puVar1[2]);
    iVar6 = iVar3 + iVar2 + 1;
    iVar3 = func_0x00121ca0(iVar4 + iVar5 + iVar6 + iVar2,3,0x10);
    *(param_1 + 0x48) = iVar3;
    if (iVar3 != 0) {
        func_0x001317dc(iVar3,param_3,iVar4);
        func_0x001316bc(*(param_1 + 0x48),*puVar1,iVar4);
        iVar4 = *(param_1 + 0x48) + iVar4;
        *(param_1 + 0x4c) = iVar4;
        func_0x001317dc(iVar4,param_3,iVar5);
        func_0x001316bc(*(param_1 + 0x4c),puVar1[1],iVar5);
        iVar5 = *(param_1 + 0x4c) + iVar5;
        *(param_1 + 0x50) = iVar5;
        func_0x001317dc(iVar5,param_3,iVar6);
        func_0x001316bc(*(param_1 + 0x50),puVar1[2],iVar6);
        iVar6 = *(param_1 + 0x50) + iVar6;
        *(param_1 + 0x54) = iVar6;
        func_0x001317dc(iVar6,param_3,iVar2);
        *(param_1 + 0x5c) = param_4;
        *(param_1 + 0x1bc) = 0;
        *(param_1 + 0x1bd) = 0xff;
        *(param_1 + 0x1be) = 0xff;
        iVar2 = 0;
        do {
            iVar4 = iVar2 + 1;
            iVar2 = param_1 + iVar2 * 0x14;
            *(iVar2 + 0x80) = 0;
            *(iVar2 + 0x7c) = 0xffffffff;
            *(iVar2 + 0x84) = 0;
            *(iVar2 + 0x8c) = 0;
            *(iVar2 + 0x8e) = 0;
            *(iVar2 + 0x8f) = 0;
            *(iVar2 + 0x88) = 0;
            iVar3 = *0x6d73e4;
            iVar2 = iVar4;
        } while (iVar4 < 0x10);
        *(*0x6d73e4 + 8) = param_2;
        *(iVar3 + 0x10) = 0;
    //WARNING: Bad instruction - Truncating control flow here
        halt_baddata();
    }
    software_interrupt(0xbd);
    //WARNING: Bad instruction - Truncating control flow here
    halt_baddata();
}

