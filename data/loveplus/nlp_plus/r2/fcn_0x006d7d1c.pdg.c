
uint fcn.006d7d1c(int param_1)

{
    uchar uVar1;
    uint32_t uVar2;
    uint32_t uVar3;
    char *pcVar4;
    uint uVar5;
    char cVar6;
    uint uVar7;
    int *piVar8;
    uint32_t uVar9;
    int iVar10;
    uint32_t *puVar11;
    int iVar12;
    int *piVar13;
    int iVar14;
    bool bVar15;
    bool bVar16;
    
    if (*(param_1 + 0x1bc) == '\0') {
        while( true ) {
            func_0x0011611c(param_1 + 0x8fc);
            iVar12 = *(param_1 + 0x8f4);
            func_0x00116288(param_1 + 0x8fc);
            if (iVar12 < 1) break;
            func_0x0011611c(param_1 + 0x904);
            func_0x0011611c(param_1 + 0x8fc);
            *(param_1 + 0x8f4) = *(param_1 + 0x8f4) + -1;
            iVar12 = *(param_1 + 0x1ec);
            *(param_1 + 0x1ec) = *(iVar12 + 0x14);
            if (*(iVar12 + 0x14) != 0) {
                *(*(iVar12 + 0x14) + 0x18) = *(iVar12 + 0x18);
            }
            if (*(iVar12 + 0x18) != 0) {
                *(*(iVar12 + 0x18) + 0x14) = *(iVar12 + 0x14);
            }
            *(iVar12 + 0x14) = 0;
            *(iVar12 + 0x18) = 0;
            if (*(param_1 + 0x1f0) == 0) {
                *(param_1 + 0x1f0) = iVar12;
            }
            else {
                *(iVar12 + 0x14) = *(param_1 + 0x1f0);
                *(*(param_1 + 0x1f0) + 0x18) = iVar12;
                *(param_1 + 0x1f0) = iVar12;
            }
            func_0x00116288(param_1 + 0x8fc);
            func_0x00116288(param_1 + 0x90c);
        }
        return 1;
    }
    if (*(param_1 + 0x1bc) != '\x02') {
        func_0x0011611c(param_1 + 0x8fc);
        iVar12 = *(param_1 + 0x8f4);
        func_0x00116288(param_1 + 0x8fc);
        if (iVar12 < 1) {
            return 1;
        }
    }
    puVar11 = NULL;
    if ((*(param_1 + 0x1bc) != '\x06' && *(param_1 + 0x1bc) != '\a') && (-1 < *(param_1 + 0x1bd))) {
        puVar11 = param_1 + *(param_1 + 0x1bd) * 0x14 + 0x7c;
    }
    uVar2 = 0;
    cVar6 = *(param_1 + 0x1bc);
    if (cVar6 == '\x02') {
code_r0x006d7f94:
    //switch table (8 cases) at 0x6d7fa8
        switch(cVar6) {
        default:
            goto code_r0x006d8090;
        case '\x01':
            if (uVar2 != *(param_1 + 0x78)) {
                return 1;
            }
            *(param_1 + 0x78) = 0;
        case '\x02':
            uVar5 = *(param_1 + 0x1e4);
            uVar2 = *(param_1 + 0x1e8);
            if (uVar2 != 0) {
                iVar12 = 0x10;
                piVar13 = param_1 + 0x7c;
                piVar8 = param_1 + 0x84;
                uVar3 = uVar2;
                do {
                    iVar14 = *piVar13;
                    piVar13 = piVar13 + 5;
                    bVar15 = iVar14 != -1;
                    if (bVar15) {
                        iVar14 = *piVar8;
                    }
                    piVar8 = piVar8 + 5;
                    if (bVar15) {
                        uVar3 = uVar3 + iVar14;
                    }
                    iVar12 = iVar12 + -1;
                } while (iVar12 != 0);
                if (0x5ffff < uVar3) {
                    *(param_1 + 0x1bc) = 2;
                    return 1;
                }
                uVar3 = func_0x00121ca0(uVar2,3,0x10);
                puVar11[1] = uVar3;
                if (uVar3 != 0) {
                    puVar11[2] = uVar2;
                    uVar9 = *puVar11;
                    uVar1 = *(param_1 + 0x44);
                    uVar7 = *(param_1 + 0x4c);
                    bVar15 = 0xfffffffe < uVar9;
                    bVar16 = uVar9 != 0xffffffff;
                    if (bVar16) {
                        uVar9 = uVar9 & 0xff000000;
                        bVar15 = 0xfffffff < uVar9;
                    }
                    if (bVar15 && (bVar16 && uVar9 != 0x10000000)) {
                        uVar1 = *(param_1 + 0x5c);
                        uVar7 = *(*0x6d8290 + 4);
                    }
                    uVar2 = func_0x00106f9c(uVar3,uVar7,uVar2,uVar5,uVar1,param_1 + 0x1ec);
                    puVar11[3] = uVar2;
                    *(param_1 + 0x1bc) = 3;
code_r0x006d8090:
                    return 1;
                }
                *(puVar11 + 0x13) = 1;
            }
            break;
        case '\x03':
            if (uVar2 != puVar11[3]) {
                return 1;
            }
            puVar11[3] = 0;
            break;
        case '\x04':
            *(param_1 + 0x1bf) = 1;
            break;
        case '\x05':
            *(param_1 + 0x1c0) = 1;
            break;
        case '\x06':
            if (uVar2 != *(param_1 + 0x78)) {
                return 1;
            }
            piVar13 = *(param_1 + 0x60) + *(param_1 + 100) * 0x14 + -0x14;
            pcVar4 = piVar13[1];
            if (((pcVar4 != NULL) && (*piVar13 != 0)) && (*pcVar4 == 'S')) {
                cVar6 = pcVar4[1];
                bVar15 = cVar6 == 'D';
                if (bVar15) {
                    cVar6 = pcVar4[2];
                }
                bVar16 = bVar15 && cVar6 == 'N';
                if (bVar15 && cVar6 == 'N') {
                    bVar16 = pcVar4[3] == 'M';
                }
                if (bVar16) {
                    uVar2 = *(pcVar4 + 8);
                    piVar13[3] = pcVar4[0xb] | uVar2 << 0x18 | (uVar2 >> 8 & 0xff) << 0x10 | (uVar2 >> 0x10 & 0xff) << 8
                    ;
                    *(piVar13 + 4) = *(pcVar4 + 0xc) << 8 | *(pcVar4 + 0xc) >> 8;
                    if (*(param_1 + 0x1bd) != '\0') {
                        iVar12 = func_0x00300e60(**piVar13);
                        if (-1 < *(param_1 + 0x1bd)) {
                            iVar14 = func_0x00300e60(*(param_1 + 0x54));
                            iVar12 = iVar12 + iVar14;
                        }
                        iVar14 = *0x6d8294;
                        iVar10 = func_0x00300e60(*(*0x6d8294 + 0x10));
                        func_0x001317dc(*(param_1 + 0x58) + iVar12,*(iVar14 + 0x10),iVar10 + 1);
                        uVar5 = func_0x00106f9c(piVar13[2],*(param_1 + 0x58),*(*piVar13 + 0x10),0,*(*piVar13 + 8),
                                                param_1 + 0x1ec);
                        *(param_1 + 0x78) = uVar5;
                        *(param_1 + 0x1bc) = 7;
                        return 1;
                    }
                    *(param_1 + 0x1c1) = 1;
                    break;
                }
            }
            *piVar13 = 0;
            if (piVar13[1] != 0) {
                func_0x002fcd88();
                piVar13[1] = 0;
            }
            iVar12 = piVar13[2];
            if (iVar12 != 0) goto code_r0x006d81bc;
            break;
        case '\a':
            break;
        }
code_r0x006d809c:
        if (puVar11 != NULL) {
code_r0x006d80a4:
            *(puVar11 + 0x12) = 1;
        }
code_r0x006d80a8:
        *(param_1 + 0x1bd) = 0xff;
        *(param_1 + 0x1bc) = 0;
        if (*(param_1 + 0x58) != 0) {
            func_0x002fcd88();
            *(param_1 + 0x58) = 0;
        }
        iVar14 = *(param_1 + 0x1be);
        iVar12 = 0;
        while( true ) {
            iVar14 = iVar14 + 1;
            iVar10 = param_1 + iVar12 * 0x14;
            if (0xf < iVar14) {
                iVar14 = 0;
            }
            if ((*(iVar10 + 0x7c) != -1) && (*(iVar10 + 0x8e) == '\0')) break;
            iVar12 = iVar12 + 1;
            if (0xf < iVar12) {
                return 1;
            }
        }
        func_0x006d854c();
        return 1;
    }
    if (cVar6 != '\b') {
        func_0x0011611c(param_1 + 0x904);
        func_0x0011611c(param_1 + 0x8fc);
        *(param_1 + 0x8f4) = *(param_1 + 0x8f4) + -1;
        iVar12 = *(param_1 + 0x1ec);
        iVar14 = *(iVar12 + 4);
        uVar2 = *(iVar12 + 0xc);
        *(param_1 + 0x1ec) = *(iVar12 + 0x14);
        if (*(iVar12 + 0x14) != 0) {
            *(*(iVar12 + 0x14) + 0x18) = *(iVar12 + 0x18);
        }
        if (*(iVar12 + 0x18) != 0) {
            *(*(iVar12 + 0x18) + 0x14) = *(iVar12 + 0x14);
        }
        *(iVar12 + 0x14) = 0;
        *(iVar12 + 0x18) = 0;
        if (*(param_1 + 0x1f0) == 0) {
            *(param_1 + 0x1f0) = iVar12;
        }
        else {
            *(iVar12 + 0x14) = *(param_1 + 0x1f0);
            *(*(param_1 + 0x1f0) + 0x18) = iVar12;
            *(param_1 + 0x1f0) = iVar12;
        }
        func_0x00116288(param_1 + 0x8fc);
        func_0x00116288(param_1 + 0x90c);
        cVar6 = *(param_1 + 0x1bc);
        if (cVar6 == '\x02') goto code_r0x006d7f94;
        if (cVar6 == '\b') goto code_r0x006d7e84;
        if (iVar14 == 0) goto code_r0x006d7f94;
        if (cVar6 != '\x06' && cVar6 != '\a') goto code_r0x006d7e84;
        piVar13 = *(param_1 + 0x60) + *(param_1 + 100) * 0x14 + -0x14;
        *piVar13 = 0;
        if (piVar13[1] != 0) {
            func_0x002fcd88();
            piVar13[1] = 0;
        }
        iVar12 = piVar13[2];
        if (iVar12 == 0) goto code_r0x006d809c;
code_r0x006d81bc:
        func_0x00129ed4(iVar12,3);
        piVar13[2] = 0;
        goto code_r0x006d809c;
    }
code_r0x006d7e84:
    if (puVar11 == NULL) goto code_r0x006d80a8;
    *(puVar11 + 0x13) = 1;
    goto code_r0x006d80a4;
}

