
uint fcn.006bccd4(int param_1)

{
    char cVar1;
    int16_t iVar2;
    uint8_t uVar3;
    uchar uVar4;
    int16_t iVar5;
    int iVar6;
    float *pfVar7;
    int16_t *piVar8;
    uint32_t uVar9;
    uint32_t uVar10;
    uint8_t uVar11;
    uint32_t uVar12;
    uint32_t uVar13;
    uint32_t uVar14;
    uint32_t *puVar15;
    int iVar16;
    int iVar17;
    bool bVar18;
    ulong uVar19;
    uint uStack_60;
    uint uStack_5c;
    uint uStack_58;
    uint uStack_54;
    
    iVar6 = func_0x006a2844(1);
    uVar13 = *(iVar6 + 0x54);
    uVar9 = *(param_1 + 0x48) ^ uVar13;
    *(param_1 + 0x4c) = *(param_1 + 0x48) & uVar9;
    *(param_1 + 0x44) = uVar9 & uVar13;
    *(param_1 + 0x48) = uVar13;
    *(param_1 + 0x50) = *(iVar6 + 0x5c);
    pfVar7 = func_0x0074141c(iVar6,0);
    *(param_1 + 100) = *pfVar7;
    *(param_1 + 0x68) = pfVar7[1];
    piVar8 = func_0x00741404(iVar6,0);
    iVar5 = *piVar8;
    *(param_1 + 0x74) = iVar5;
    iVar2 = piVar8[1];
    *(param_1 + 0x76) = iVar2;
    uVar11 = *(piVar8 + 2);
    uVar3 = *(param_1 + 0x7c) ^ uVar11;
    *(param_1 + 0x7d) = uVar3 & uVar11;
    *(param_1 + 0x7e) = *(param_1 + 0x7c) & uVar3;
    *(param_1 + 0x7c) = uVar11;
    iVar6 = *(param_1 + 0x37c);
    uVar9 = *(param_1 + 0x50);
    if (iVar6 == 0) {
        uVar12 = 0;
        uVar10 = **0x6bd2f8;
        uVar14 = uVar10;
        puVar15 = *0x6bd2f8;
        while (uVar14 != 0) {
            if ((uVar14 & uVar13) != 0) {
                uVar12 = uVar12 | puVar15[1];
            }
            puVar15 = puVar15 + 2;
            uVar14 = *puVar15;
        }
        uVar13 = uVar12 | uVar13 & 0xfffff0f;
        uVar12 = 0;
        puVar15 = *0x6bd2f8;
        while (uVar10 != 0) {
            if ((uVar10 & uVar9) != 0) {
                uVar12 = uVar12 | puVar15[1];
            }
            puVar15 = puVar15 + 2;
            uVar10 = *puVar15;
        }
        *(param_1 + 0x6c) = pfVar7[1];
        uVar9 = uVar9 & 0xfffff0f | uVar12;
        *(param_1 + 0x70) = -*pfVar7;
        if (uVar11 != 0) {
            *(param_1 + 0x36e) = iVar5;
            *(param_1 + 0x370) = iVar2;
            *(param_1 + 0x78) = -iVar2;
            *(param_1 + 0x7a) = iVar5;
        }
    }
    else if (iVar6 == 2) {
        uVar12 = 0;
        uVar10 = **0x6bd2fc;
        uVar14 = uVar10;
        puVar15 = *0x6bd2fc;
        while (uVar14 != 0) {
            if ((uVar14 & uVar13) != 0) {
                uVar12 = uVar12 | puVar15[1];
            }
            puVar15 = puVar15 + 2;
            uVar14 = *puVar15;
        }
        uVar13 = uVar12 | uVar13 & 0xfffff0f;
        uVar12 = 0;
        puVar15 = *0x6bd2fc;
        while (uVar10 != 0) {
            if ((uVar10 & uVar9) != 0) {
                uVar12 = uVar12 | puVar15[1];
            }
            puVar15 = puVar15 + 2;
            uVar10 = *puVar15;
        }
        uVar9 = uVar9 & 0xfffff0f | uVar12;
        *(param_1 + 0x6c) = -pfVar7[1];
        *(param_1 + 0x70) = *pfVar7;
        if (uVar11 != 0) {
            *(param_1 + 0x36e) = iVar5;
            *(param_1 + 0x370) = iVar2;
            *(param_1 + 0x78) = iVar2;
            *(param_1 + 0x7a) = -iVar5;
        }
    }
    else if (iVar6 == 3) {
        uVar12 = 0;
        uVar10 = **0x6bd300;
        uVar14 = uVar10;
        puVar15 = *0x6bd300;
        while (uVar14 != 0) {
            if ((uVar14 & uVar13) != 0) {
                uVar12 = uVar12 | puVar15[1];
            }
            puVar15 = puVar15 + 2;
            uVar14 = *puVar15;
        }
        uVar13 = uVar12 | uVar13 & 0xfffff0f;
        uVar12 = 0;
        puVar15 = *0x6bd300;
        while (uVar10 != 0) {
            if ((uVar10 & uVar9) != 0) {
                uVar12 = uVar12 | puVar15[1];
            }
            puVar15 = puVar15 + 2;
            uVar10 = *puVar15;
        }
        uVar9 = uVar9 & 0xfffff0f | uVar12;
        *(param_1 + 0x6c) = -*pfVar7;
        *(param_1 + 0x70) = -pfVar7[1];
        if (uVar11 != 0) {
            *(param_1 + 0x36e) = iVar5;
            *(param_1 + 0x370) = iVar2;
            *(param_1 + 0x78) = -iVar5;
            *(param_1 + 0x7a) = -iVar2;
        }
    }
    else {
        *(param_1 + 0x6c) = *pfVar7;
        *(param_1 + 0x70) = pfVar7[1];
        if (uVar11 != 0) {
            *(param_1 + 0x36e) = iVar5;
            *(param_1 + 0x370) = iVar2;
            *(param_1 + 0x78) = iVar5;
            *(param_1 + 0x7a) = iVar2;
        }
    }
    uVar12 = *(param_1 + 0x58);
    *(param_1 + 0x60) = uVar9;
    *(param_1 + 0x58) = uVar13;
    uVar9 = uVar12 ^ uVar13;
    uVar12 = uVar9 & uVar12;
    *(param_1 + 0x5c) = uVar12;
    iVar6 = *0x6bd304;
    *(param_1 + 0x54) = uVar13 & uVar9;
    if (uVar12 != 0) {
        uVar9 = 1;
        do {
            if ((*(param_1 + 0x5c) & *(iVar6 + uVar9 * 4)) != 0) {
                *(param_1 + 0x3c2) = *(param_1 + 0x3c2) & ~(1 << uVar9);
                *(*(param_1 + 0x3c0) + param_1 + 0x380) = uVar9 | 0x20;
                uVar11 = *(param_1 + 0x3c0) + 1;
                *(param_1 + 0x3c0) = uVar11;
                if (0x3f < uVar11) {
                    *(param_1 + 0x3c0) = 0;
                }
            }
            uVar9 = uVar9 + 1 & 0xff;
        } while (uVar9 < 0xd);
    }
    if (*(param_1 + 0x54) != 0) {
        uVar9 = 1;
        do {
            if ((*(param_1 + 0x54) & *(iVar6 + uVar9 * 4)) != 0) {
                *(param_1 + 0x3c2) = *(param_1 + 0x3c2) | 1 << uVar9;
                *(*(param_1 + 0x3c0) + param_1 + 0x380) = uVar9;
                uVar11 = *(param_1 + 0x3c0) + 1;
                *(param_1 + 0x3c0) = uVar11;
                if (0x3f < uVar11) {
                    *(param_1 + 0x3c0) = 0;
                }
            }
            uVar9 = uVar9 + 1 & 0xff;
        } while (uVar9 < 0xd);
    }
    if (*(param_1 + 0x7c) == '\0') {
        if (*(param_1 + 0x35c) != 0 || *(param_1 + 0x358) != 0) {
            *(param_1 + 0x372) = *(param_1 + 0x36e);
            *(param_1 + 0x374) = *(param_1 + 0x370);
            *(param_1 + 0x366) = *(param_1 + 0x78);
            *(param_1 + 0x368) = *(param_1 + 0x7a);
            *(param_1 + 0x84) = *(param_1 + 0x84) + 1;
            *(param_1 + 0x358) = 0;
            *(param_1 + 0x35c) = 0;
        }
        uVar4 = *(param_1 + 0x7f);
        *(param_1 + 0x7f) = 0;
        *(param_1 + 0x80) = uVar4;
        return 1;
    }
    func_0x0069dd18(&uStack_58);
    uStack_60 = uStack_58;
    uStack_5c = uStack_54;
    uVar19 = func_0x0069de1c(&uStack_60);
    uVar9 = uVar19;
    if (*(param_1 + 0x358) == 0 && *(param_1 + 0x35c) == 0) {
        *(param_1 + 0x36a) = *(param_1 + 0x78);
        *(param_1 + 0x362) = *(param_1 + 0x78);
        *(param_1 + 0x36c) = *(param_1 + 0x7a);
        *(param_1 + 0x364) = *(param_1 + 0x7a);
        *(param_1 + 0x358) = uVar19;
    }
    cVar1 = *(param_1 + 0x7f);
    uVar13 = uVar9 - *(param_1 + 0x358);
    *(param_1 + 0x84) = uVar13;
    if (cVar1 == '\0') {
        *(param_1 + 0x7f) = 1;
        goto code_r0x006bd1cc;
    }
    if (cVar1 == '\x01') {
        iVar5 = *(param_1 + 0x78) - *(param_1 + 0x362);
        iVar2 = *(param_1 + 0x7a) - *(param_1 + 0x364);
        if (iVar2 * iVar2 + iVar5 * iVar5 < 0x40) {
            if (399 < uVar13) {
                *(param_1 + 0x7f) = 3;
            }
            goto code_r0x006bd1cc;
        }
        uVar4 = 2;
    }
    else {
        if (cVar1 != '\x03') {
            iVar6 = *(param_1 + 0x360);
            do {
                iVar6 = iVar6 + -1;
                if (iVar6 < 0) {
                    iVar6 = 0x3b;
                }
                puVar15 = param_1 + 0x178 + iVar6 * 8;
                uVar13 = *puVar15;
                iVar16 = (uVar19 >> 0x20) - (puVar15[1] + (uVar9 < uVar13));
                bVar18 = 400 < uVar9 - uVar13;
                if (-(iVar16 + bVar18) < 0 != (SBORROW4(0,iVar16) != SBORROW4(-iVar16,bVar18))) break;
                iVar17 = *(param_1 + 0x78) - *(param_1 + 0x88 + iVar6 * 2);
                iVar16 = *(param_1 + 0x7a) - *(param_1 + 0x100 + iVar6 * 2);
                if (0x40 < iVar16 * iVar16 + iVar17 * iVar17) goto code_r0x006bd1cc;
            } while (iVar6 != *(param_1 + 0x360));
            *(param_1 + 0x7f) = 3;
            *(param_1 + 0x36a) = *(param_1 + 0x78);
            *(param_1 + 0x36c) = *(param_1 + 0x7a);
            goto code_r0x006bd1cc;
        }
        iVar5 = *(param_1 + 0x78) - *(param_1 + 0x36a);
        iVar2 = *(param_1 + 0x7a) - *(param_1 + 0x36c);
        if (iVar2 * iVar2 + iVar5 * iVar5 < 0x100) goto code_r0x006bd1cc;
        uVar4 = 4;
    }
    *(param_1 + 0x7f) = uVar4;
code_r0x006bd1cc:
    *(param_1 + *(param_1 + 0x360) * 2 + 0x88) = *(param_1 + 0x78);
    *(param_1 + *(param_1 + 0x360) * 2 + 0x100) = *(param_1 + 0x7a);
    *(param_1 + *(param_1 + 0x360) * 8 + 0x178) = uVar19;
    iVar5 = *(param_1 + 0x360) + 1;
    *(param_1 + 0x360) = iVar5;
    if (0x3b < iVar5) {
        *(param_1 + 0x360) = 0;
    }
    return 1;
}

