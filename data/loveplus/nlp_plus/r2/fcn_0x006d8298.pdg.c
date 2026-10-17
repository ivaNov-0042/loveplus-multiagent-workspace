
void fcn.006d8298(int param_1)

{
    char cVar1;
    int *piVar2;
    int iVar3;
    int iVar4;
    int iVar5;
    int *piVar6;
    int *piVar7;
    
    if (*(param_1 + 0x1bc) != '\0' && *(param_1 + 0x1bc) != '\x02') {
        func_0x0011611c(param_1 + 0x8fc);
        iVar4 = *(param_1 + 0x8f4);
        func_0x00116288(param_1 + 0x8fc);
        if (0 < iVar4) {
            cVar1 = *(param_1 + 0x1bc);
            if (cVar1 == '\x03') {
                if (-1 < *(*0x6d84e4 + param_1)) goto code_r0x006d830c;
            }
            else if ((cVar1 == '\x06' || cVar1 == '\a') || cVar1 == '\x01') {
code_r0x006d830c:
                func_0x0066e114(*(param_1 + 0x78));
                *(param_1 + 0x1bd) = 0xff;
                *(param_1 + 0x1bc) = 0;
                if (*(param_1 + 0x58) != 0) {
                    func_0x002fcd88(*(param_1 + 0x58));
                    *(param_1 + 0x58) = 0;
                }
            }
        }
    }
    iVar4 = 0;
    piVar7 = *0x6d84e8 + 0x1c6;
    piVar6 = *0x6d84e8 + 0x1c2;
    do {
        iVar5 = param_1 + iVar4 * 0x14;
        if (*(iVar5 + 0x88) != 0) {
            func_0x0069683c(*(iVar5 + 0x88),*0x6d84e8);
            piVar2 = *0x6d84e8;
            func_0x0011611c(piVar7);
            func_0x0011611c(piVar2 + 0x1c4);
            *piVar6 = piVar2[0x1c2] + -1;
            iVar3 = *piVar2;
            *piVar2 = *(iVar3 + 0x14);
            if (*(iVar3 + 0x14) != 0) {
                *(*(iVar3 + 0x14) + 0x18) = *(iVar3 + 0x18);
            }
            if (*(iVar3 + 0x18) != 0) {
                *(*(iVar3 + 0x18) + 0x14) = *(iVar3 + 0x14);
            }
            *(iVar3 + 0x14) = 0;
            *(iVar3 + 0x18) = 0;
            if (piVar2[1] == 0) {
                piVar2[1] = iVar3;
            }
            else {
                *(iVar3 + 0x14) = piVar2[1];
                *(piVar2[1] + 0x18) = iVar3;
                piVar2[1] = iVar3;
            }
            func_0x00116288(piVar2 + 0x1c4);
            func_0x00116288(piVar2 + 0x1c8);
        }
        if (*(iVar5 + 0x80) != 0) {
            func_0x002fcd88();
            *(iVar5 + 0x80) = 0;
        }
        iVar4 = iVar4 + 1;
        *(iVar5 + 0x7c) = 0xffffffff;
    } while (iVar4 < 0x10);
    iVar4 = *(param_1 + 0x60);
    if (iVar4 == 0) goto code_r0x006d849c;
    iVar5 = 0;
    if (*(param_1 + 100) < 1) {
code_r0x006d848c:
        func_0x002fcd88(*(param_1 + 0x60));
        *(param_1 + 0x60) = 0;
    }
    else {
        do {
            if (*(iVar4 + 0x13) != '\0') {
                if (*(iVar4 + 4) != 0) {
                    func_0x002fcd88();
                    *(iVar4 + 4) = 0;
                }
                if (*(iVar4 + 8) != 0) {
                    func_0x00129ed4(*(iVar4 + 8),3);
                    *(iVar4 + 8) = 0;
                }
            }
            iVar5 = iVar5 + 1;
            iVar4 = iVar4 + 0x14;
        } while (iVar5 < *(param_1 + 100));
        if (*(param_1 + 0x60) != 0) goto code_r0x006d848c;
    }
    *(param_1 + 100) = 0;
code_r0x006d849c:
    if (*(param_1 + 0x48) != 0) {
        func_0x002fcd88();
        *(param_1 + 0x48) = 0;
    }
    *(param_1 + 0x4c) = 0;
    *(param_1 + 0x50) = 0;
    if (*(param_1 + 0x58) != 0) {
        func_0x002fcd88();
        *(param_1 + 0x58) = 0;
    }
    *(param_1 + 0x68) = 0;
    *(param_1 + 0x6c) = 0;
    *(param_1 + 0x70) = 0x7fffffff;
    *(param_1 + 0x74) = 0;
    return;
}

