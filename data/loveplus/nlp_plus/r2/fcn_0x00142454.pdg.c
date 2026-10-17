
int64_t fcn.00142454(int param_1,int param_2,ushort *param_3,uint32_t *param_4)

{
    int iVar1;
    int iVar2;
    uint32_t *puVar3;
    uint32_t *puVar4;
    uint32_t extraout_r1;
    uint32_t *puVar5;
    uint8_t *puVar6;
    uint32_t uVar7;
    uint8_t uVar8;
    uint8_t uVar9;
    ushort uVar10;
    uint32_t uVar11;
    uint32_t uVar12;
    uint32_t uVar13;
    uint32_t uVar14;
    uint32_t uVar15;
    uint32_t uVar16;
    uint32_t uVar17;
    uint32_t uVar18;
    bool bVar19;
    bool bVar20;
    
    iVar2 = param_1 + param_2 * 0xc;
    *(*0x1424ec + iVar2) = param_3;
    iVar1 = *0x1424f0;
    *(iVar2 + 0x140a) = *param_3;
    *(iVar2 + 0x1408) = 0;
    *(iVar2 + 0x1410) = *(iVar1 + param_1);
    func_0x0075e69c(iVar2 + 0x1408,param_1 + param_2 * 0x10 + 0x1420,*(*0x1424f4 + param_1),param_4);
    if (*(*0x1424f8 + param_1) == 0) {
        return extraout_r1 << 0x20;
    }
    param_1 = param_1 + param_2 * 0x500;
    puVar3 = param_1 + 0xa08;
    uVar7 = 0x500;
    uVar17 = puVar3 & 3;
    uVar18 = uVar17;
    if (uVar17 != 0) {
        uVar8 = *param_4;
        puVar5 = param_4 + 1;
        if (uVar17 < 3) {
            puVar5 = param_4 + 2;
            uVar18 = *(param_4 + 1);
        }
        *puVar3 = uVar8;
        param_4 = puVar5;
        if (uVar17 < 2) {
            param_4 = puVar5 + 1;
            uVar8 = *puVar5;
        }
        puVar5 = param_1 + 0xa09;
        if (uVar17 < 3) {
            puVar5 = param_1 + 0xa0a;
            *(param_1 + 0xa09) = uVar18;
        }
        uVar7 = uVar17 + 0x4fc;
        puVar3 = puVar5;
        if (uVar17 < 2) {
            puVar3 = puVar5 + 1;
            *puVar5 = uVar8;
        }
    }
    uVar17 = param_4 & 3;
    if (uVar17 == 0) {
        uVar18 = uVar7 - 0x20;
        uVar17 = 0;
        if (0x1f < uVar7) {
            uVar17 = *param_4;
            uVar7 = param_4[1];
            uVar11 = param_4[2];
            uVar12 = param_4[3];
            HintPreloadData(param_4 + 0x14);
            uVar13 = param_4[4];
            uVar14 = param_4[5];
            uVar15 = param_4[6];
            uVar16 = param_4[7];
            param_4 = param_4 + 8;
            while( true ) {
                *puVar3 = uVar17;
                puVar3[1] = uVar7;
                puVar3[2] = uVar11;
                puVar3[3] = uVar12;
                bVar19 = 0x1f < uVar18;
                uVar18 = uVar18 - 0x20;
                puVar3[4] = uVar13;
                puVar3[5] = uVar14;
                puVar3[6] = uVar15;
                puVar3[7] = uVar16;
                puVar3 = puVar3 + 8;
                if (bVar19) {
                    uVar17 = *param_4;
                    uVar7 = param_4[1];
                    uVar11 = param_4[2];
                    uVar12 = param_4[3];
                    param_4 = param_4 + 4;
                }
                HintPreloadData(param_4 + 0x10);
                if (!bVar19) break;
                uVar13 = *param_4;
                uVar14 = param_4[1];
                uVar15 = param_4[2];
                uVar16 = param_4[3];
                param_4 = param_4 + 4;
            }
        }
        if (uVar18 >> 4 & 1) {
            uVar17 = *param_4;
            uVar7 = param_4[1];
            uVar11 = param_4[2];
            uVar12 = param_4[3];
            param_4 = param_4 + 4;
            *puVar3 = uVar17;
            puVar3[1] = uVar7;
            puVar3[2] = uVar11;
            puVar3[3] = uVar12;
            puVar3 = puVar3 + 4;
        }
        if (uVar18 << 0x1c < 0) {
            uVar17 = *param_4;
            uVar7 = param_4[1];
            param_4 = param_4 + 2;
            *puVar3 = uVar17;
            puVar3[1] = uVar7;
            puVar3 = puVar3 + 2;
        }
        puVar4 = puVar3;
        puVar5 = param_4;
        if (uVar18 >> 2 & 1) {
            puVar5 = param_4 + 1;
            uVar17 = *param_4;
            puVar4 = puVar3 + 1;
            *puVar3 = uVar17;
        }
        uVar10 = uVar17;
        if ((uVar18 & 3) == 0) {
            return CONCAT44(puVar5,puVar4);
        }
        bVar20 = uVar18 >> 1 & 1;
        uVar18 = uVar18 << 0x1f;
        bVar19 = uVar18 < 0;
        puVar3 = puVar5;
        if (bVar20) {
            puVar3 = puVar5 + 2;
            uVar10 = *puVar5;
        }
        puVar5 = puVar3;
        if (bVar19) {
            puVar5 = puVar3 + 1;
            uVar18 = *puVar3;
        }
        puVar3 = puVar4;
        if (bVar20) {
            puVar3 = puVar4 + 2;
            *puVar4 = uVar10;
        }
        puVar4 = puVar3;
        if (bVar19) {
            puVar4 = puVar3 + 1;
            *puVar3 = uVar18;
        }
        return CONCAT44(puVar5,puVar4);
    }
    while( true ) {
        uVar8 = uVar18;
        if (uVar7 < 8) break;
        puVar5 = param_4 + 1;
        uVar17 = *param_4;
        param_4 = param_4 + 2;
        uVar18 = *puVar5;
        *puVar3 = uVar17;
        puVar3[1] = uVar18;
        puVar3 = puVar3 + 2;
        uVar7 = uVar7 - 8;
    }
    puVar4 = puVar3;
    puVar5 = param_4;
    if (-1 < uVar7 - 4) {
        puVar5 = param_4 + 1;
        uVar17 = *param_4;
        puVar4 = puVar3 + 1;
        *puVar3 = uVar17;
    }
    uVar9 = uVar17;
    bVar20 = uVar7 - 4 >> 1 & 1;
    uVar7 = uVar7 << 0x1f;
    bVar19 = uVar7 < 0;
    if (bVar20) {
        puVar6 = puVar5 + 1;
        uVar9 = *puVar5;
        puVar5 = puVar5 + 2;
        uVar8 = *puVar6;
    }
    puVar3 = puVar5;
    if (bVar19) {
        puVar3 = puVar5 + 1;
        uVar7 = *puVar5;
    }
    if (bVar20) {
        puVar6 = puVar4 + 1;
        *puVar4 = uVar9;
        puVar4 = puVar4 + 2;
        *puVar6 = uVar8;
    }
    puVar5 = puVar4;
    if (bVar19) {
        puVar5 = puVar4 + 1;
        *puVar4 = uVar7;
    }
    return CONCAT44(puVar3,puVar5);
}

