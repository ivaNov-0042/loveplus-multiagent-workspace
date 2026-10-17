
void fcn.006d854c(int param_1,uint32_t param_2)

{
    char cVar1;
    uchar uVar2;
    uint32_t uVar3;
    int iVar4;
    int unaff_r5;
    uint uVar5;
    int iVar6;
    int iVar7;
    uint32_t uVar8;
    
    if (0xf < param_2) {
        *(param_1 + 0x1bc) = 8;
        return;
    }
    cVar1 = param_2;
    *(param_1 + 0x1be) = cVar1;
    *(param_1 + 0x1bd) = cVar1;
    uVar3 = *(param_1 + param_2 * 0x14 + 0x7c);
    if (-1 < uVar3) {
        if (((uVar3 & 0xff000000) < 0x10000001) && (*(param_1 + 0x914) != '\0')) {
            iVar7 = *(param_1 + 0x91c);
            if (iVar7 != 0) {
                unaff_r5 = *(param_1 + 0x918);
            }
            if (iVar7 != 0 && unaff_r5 != 0) {
                iVar4 = param_1 + cVar1 * 0x14;
                fcn.00121ccc(param_1 + 0x1e4,iVar7 + uVar3 * 8);
                iVar6 = *(param_1 + 0x1e4);
                uVar5 = *(param_1 + 0x1e8);
                iVar7 = fcn.00121ca0(uVar5,3,0x10);
                *(iVar4 + 0x80) = iVar7;
                if (iVar7 == 0) {
                    *(iVar4 + 0x8f) = 1;
                }
                else {
                    fcn.00302b20(iVar7,*(param_1 + 0x918) + iVar6,uVar5);
                    *(iVar4 + 0x84) = uVar5;
                }
                *(iVar4 + 0x8e) = 1;
                *(param_1 + 0x1bd) = 0xff;
                *(param_1 + 0x1bc) = 0;
                return;
            }
        }
        uVar8 = *(param_1 + 0x70);
        if (((uVar8 <= uVar3) && (uVar3 < *(param_1 + 0x74) + uVar8)) && (*(param_1 + 0x6c) != 0)) {
            iVar6 = param_1 + cVar1 * 0x14;
            fcn.00121ccc(param_1 + 0x1e4,*(param_1 + 0x68) + (uVar3 - uVar8) * 8);
            iVar4 = *(param_1 + 0x1e4);
            uVar5 = *(param_1 + 0x1e8);
            iVar7 = fcn.00121ca0(uVar5,3,0x10);
            *(iVar6 + 0x80) = iVar7;
            if (iVar7 == 0) {
                *(iVar6 + 0x8f) = 1;
            }
            else {
                fcn.00302b20(iVar7,*(param_1 + 0x6c) + iVar4,uVar5);
            }
            *(iVar6 + 0x8e) = 1;
            *(param_1 + 0x1bd) = 0xff;
            *(param_1 + 0x1bc) = 0;
            iVar4 = *(param_1 + 0x1be);
            iVar7 = 0;
            while( true ) {
                iVar4 = iVar4 + 1;
                iVar6 = param_1 + iVar7 * 0x14;
                if (0xf < iVar4) {
                    iVar4 = 0;
                }
                if ((*(iVar6 + 0x7c) != -1) && (*(iVar6 + 0x8e) == '\0')) break;
                iVar7 = iVar7 + 1;
                if (0xf < iVar7) {
                    return;
                }
            }
            fcn.006d854c();
            return;
        }
        if ((((uVar3 & 0xff000000) < 0x10000001) || (uVar3 < 0x10000001)) &&
           ((0x10000000 < (uVar3 & 0xff000000) || (uVar3 < *0x6d879c)))) {
            uVar2 = *(param_1 + 0x44);
            uVar5 = *(param_1 + 0x48);
            *(param_1 + 0x1bc) = 1;
            if (0x10000000 < (uVar3 & 0xff000000)) {
                uVar2 = *(param_1 + 0x5c);
                uVar3 = uVar3 & 0xffffff;
                uVar5 = **0x6d87a0;
            }
            uVar5 = fcn.00106f9c(param_1 + 0x1e4,uVar5,8,uVar3 << 3,uVar2,param_1 + 0x1ec);
            *(param_1 + 0x78) = uVar5;
            return;
        }
    }
    *(param_1 + 0x1bc) = 8;
    return;
}

