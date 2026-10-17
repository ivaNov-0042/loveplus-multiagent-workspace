
uint fcn.007427a8(int param_1,int param_2)

{
    uint32_t uVar1;
    int iVar2;
    int iVar3;
    uint32_t uVar4;
    
    iVar2 = *(param_1 + 0x60);
    if (iVar2 != 0) {
        uVar4 = *(param_1 + 100);
        if (uVar4 < 1) {
            uVar1 = 0;
        }
        else {
            uVar1 = uVar4 & 1;
            iVar3 = 0;
            if (uVar1 != 0) {
                do {
                    if ((*(iVar2 + iVar3 * 0x14 + 8) != 0) && (*(iVar2 + iVar3 * 0x14 + 0x12) == param_2)) {
                        return *(iVar2 + iVar3 * 0x14 + 8);
                    }
                    iVar3 = iVar3 + 1;
                } while (iVar3 < uVar1);
            }
        }
        for (; uVar1 < uVar4; uVar1 = uVar1 + 2) {
            if ((*(iVar2 + uVar1 * 0x14 + 8) != 0) && (*(iVar2 + uVar1 * 0x14 + 0x12) == param_2)) {
                iVar3 = uVar1 * 0x14 + 8;
code_r0x0074288c:
                return *(iVar2 + iVar3);
            }
            if ((*(iVar2 + uVar1 * 0x14 + 0x1c) != 0) && (*(iVar2 + uVar1 * 0x14 + 0x26) == param_2)) {
                iVar3 = uVar1 * 0x14 + 0x1c;
                goto code_r0x0074288c;
            }
        }
    }
    return 0;
}

