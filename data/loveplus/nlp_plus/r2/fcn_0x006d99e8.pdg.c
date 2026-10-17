
//WARNING: Type propagation algorithm not settling

uint fcn.006d99e8(int param_1)

{
    char cVar1;
    bool bVar2;
    float fVar3;
    float fVar4;
    int iVar5;
    uint32_t uVar6;
    int iVar7;
    uint uVar8;
    int16_t *piVar9;
    uint32_t uVar10;
    int iVar11;
    int *piVar12;
    int16_t *piVar13;
    uint *puVar14;
    bool bVar15;
    bool bVar16;
    uint32_t in_fpscr;
    float fVar17;
    float fVar18;
    float fVar19;
    ulong uVar20;
    int64_t iVar21;
    uint uStack_90;
    uint uStack_8c;
    uint uStack_88;
    uint uStack_84;
    uchar auStack_80 [4];
    int iStack_7c;
    int aiStack_78 [11];
    ushort uStack_4c;
    
    if ((*(param_1 + 0x44) != 0) && (iVar5 = func_0x0072080c(), iVar5 != 0)) {
        bVar2 = false;
        func_0x0069dd18(&uStack_88);
        uStack_90 = uStack_88;
        uStack_8c = uStack_84;
        uVar20 = func_0x0069de1c(&uStack_90);
        iVar11 = uVar20 >> 0x20;
        uVar6 = uVar20;
        iVar5 = *(param_1 + 0x44);
        if (*(iVar5 + 0x58b) == '\0') {
            func_0x006d84ec(*(iVar5 + 0x5a4));
            iVar5 = func_0x00742638(*(*(param_1 + 0x44) + 0x5a4),&uStack_8c,&uStack_84);
            if (iVar5 != 0) {
                uVar8 = func_0x00722034(uStack_8c,0,1);
                *(*(param_1 + 0x44) + 0x5a8) = uVar8;
                *(*(param_1 + 0x44) + 0x58b) = 1;
            }
        }
        else if (*(iVar5 + 0x58c) == '\0') {
            func_0x006d7920(*(iVar5 + 0x5a4));
            iVar5 = func_0x007428b0(*(*(param_1 + 0x44) + 0x5a4));
            if (iVar5 != 0) {
                *(*(param_1 + 0x44) + 0x58c) = 1;
            }
        }
        else if ((*(iVar5 + 0x58d) != '\0') &&
                (iVar5 = func_0x007428bc(*(iVar5 + 0x5a4),*(iVar5 + 0x5b0)), iVar5 != 0)) {
            iVar5 = *(param_1 + 0x44);
            piVar12 = *(iVar5 + 0x5b4);
            iVar5 = func_0x007427a8(*(iVar5 + 0x5a4),*(iVar5 + 0x5b0));
            func_0x006779d4(auStack_80);
            aiStack_78[0] = piVar12[4];
            aiStack_78[1] = 0;
            aiStack_78[2] = *piVar12;
            uStack_4c = 0;
            iStack_7c = iVar5;
            func_0x006779ac(auStack_80);
            *(*(param_1 + 0x44) + 0x58d) = 0;
        }
        bVar16 = false;
        iVar5 = 0;
        piVar13 = *(param_1 + 0x44) + 8;
        do {
            if (*(piVar13 + 10) != -1 || *(piVar13 + 8) != -1) {
                iVar7 = func_0x0071ffa8();
                if (iVar7 == 0) {
                    if (piVar13 != NULL) {
                        if (*(piVar13 + 0x1a) != NULL) {
                            (**(piVar13 + 0x1a))(*(piVar13 + 4),*piVar13);
                        }
                        func_0x006d7ac4(*(*(param_1 + 0x44) + 0x5a4),*(piVar13 + 4));
                        aiStack_78[0] = -1;
                        uStack_90 = 0;
                        uStack_8c = 0;
                        piVar13[4] = -1;
                        piVar13[5] = -1;
                        *piVar13 = 0;
                        piVar13[1] = 0;
                        piVar13[0x18] = 0;
                        piVar13[0x19] = 0;
                        piVar13[0x1a] = 0;
                        piVar13[0x1b] = 0;
                        piVar13[8] = -1;
                        piVar13[9] = -1;
                        piVar13[10] = -1;
                        piVar13[0xb] = -1;
                        piVar13[0xe] = 0;
                        piVar13[0xf] = 0;
                        piVar13[0x10] = 0;
                        piVar13[0x11] = 0;
                        piVar13[0xc] = 0;
                        piVar13[0xd] = 0;
                        piVar13[0x12] = 0;
                        piVar13[0x13] = 0;
                        piVar13[0x14] = -1;
                        piVar13[0x15] = -1;
                        piVar13[0x16] = -1;
                        piVar13[0x17] = 0x7fff;
                    }
                    bVar16 = true;
                }
                else {
                    iVar7 = *(piVar13 + 0x16);
                    bVar2 = true;
                    if (iVar11 - (iVar7 + (uVar6 < *(piVar13 + 0x14))) < 0 ==
                        (SBORROW4(iVar11,iVar7) != SBORROW4(iVar11 - iVar7,uVar6 < *(piVar13 + 0x14)))) {
                        func_0x007240fc(*(piVar13 + 8),*(piVar13 + 10),0);
                        piVar13[0x14] = -1;
                        piVar13[0x15] = -1;
                        piVar13[0x16] = -1;
                        piVar13[0x17] = 0x7fff;
                    }
                }
            }
            fVar19 = *0x6d9f50;
            fVar4 = *0x6d9f4c;
            fVar3 = *0x6d9f48;
            iVar5 = iVar5 + 1;
            piVar13 = piVar13 + 0x1c;
        } while (iVar5 < 0x10);
        if (!bVar2) {
            piVar13 = NULL;
            iVar5 = 0;
            piVar9 = *(param_1 + 0x44) + 8;
            uVar10 = *0x6d9f54;
            do {
                if (((*(piVar9 + 4) != -1) && (*(piVar9 + 10) == -1 && *(piVar9 + 8) == -1)) && (piVar9[1] < uVar10)) {
                    piVar13 = piVar9;
                    uVar10 = piVar9[1];
                }
                iVar5 = iVar5 + 1;
                piVar9 = piVar9 + 0x1c;
            } while (iVar5 < 0x10);
            if (piVar13 != NULL) {
                if (bVar16) {
                    *(piVar13 + 0xc) = uVar20;
                }
                iVar5 = *(piVar13 + 0xe) + *(piVar13 + 0x12) + CARRY4(*(piVar13 + 0xc),*(piVar13 + 0x10));
                bVar16 = uVar6 < *(piVar13 + 0xc) + *(piVar13 + 0x10);
                if ((iVar11 - (iVar5 + bVar16) < 0 == (SBORROW4(iVar11,iVar5) != SBORROW4(iVar11 - iVar5,bVar16))) &&
                   (iVar5 = func_0x007429a8(*(*(param_1 + 0x44) + 0x5a4),*(piVar13 + 4)), iVar5 != 0)) {
                    func_0x00722480(aiStack_78);
                    iVar5 = func_0x00742668(*(*(param_1 + 0x44) + 0x5a4),*(piVar13 + 4),&iStack_7c,aiStack_78 + 1);
                    if (iVar5 != 0) {
                        aiStack_78[0] = iStack_7c;
                        uVar10 = *(piVar13 + 4);
                        bVar16 = 0xfffffffe < uVar10;
                        bVar15 = uVar10 == 0xffffffff;
                        if (!bVar15) {
                            uVar10 = uVar10 & 0xff000000;
                            bVar16 = 0xfffffff < uVar10;
                        }
                        aiStack_78[2] = *(param_1 + 0x44);
                        if (!bVar16 || (bVar15 || uVar10 == 0x10000000)) {
                            aiStack_78[2] = *(aiStack_78[2] + 0x5a8);
                        }
                        if (bVar16 && (!bVar15 && uVar10 != 0x10000000)) {
                            aiStack_78[2] = *(aiStack_78[2] + 0x5ac);
                        }
                        iVar21 = func_0x0072314c(aiStack_78,0);
                        if (iVar21 != -1) {
                            *(piVar13 + 8) = iVar21;
                            if (piVar13[2] < 0x7f) {
                                fVar17 = VectorSignedToFloat(piVar13[2],in_fpscr >> 0x15 & 3);
                                fVar17 = fVar17 * fVar4;
                                in_fpscr = in_fpscr & 0xfffffff | (fVar19 <= fVar17) << 0x1d;
                                fVar18 = fVar19;
                                if ((SUB41(in_fpscr >> 0x1d,0)) && (fVar18 = fVar17, 0x3f800000 < fVar17)) {
                                    fVar18 = fVar3;
                                }
                                func_0x00723ad8(fVar18,iVar21,iVar21 >> 0x20,0);
                            }
                            iVar5 = *(param_1 + 0x44);
                            if ((((*(iVar5 + 0x588) != '\0') && (*(iVar5 + 3) < 'd')) && (*(iVar5 + 0x589) == '\0')) &&
                               (*(iVar5 + 0x598) != -1 || *(iVar5 + 0x59c) != -1)) {
                                *(iVar5 + 0x589) = 1;
                                iVar5 = *(param_1 + 0x44);
                                fVar17 = VectorSignedToFloat(*(iVar5 + 3),in_fpscr >> 0x15 & 3);
                                fVar18 = VectorSignedToFloat(*(*0x6d9f5c + iVar5),in_fpscr >> 0x15 & 3);
                                func_0x00723ad8(fVar18 * fVar17 * *0x6d9f58 * fVar4,*(iVar5 + 0x598),*(iVar5 + 0x59c)
                                                ,6);
                            }
                            if (*(piVar13 + 0x18) != NULL) {
                                (**(piVar13 + 0x18))(*(piVar13 + 4),*piVar13);
                            }
                            bVar2 = true;
                        }
                    }
                }
            }
        }
        iVar5 = *(param_1 + 0x44);
        if (((*(iVar5 + 0x589) != '\0') && (!bVar2)) && (*(iVar5 + 0x59c) != -1 || *(iVar5 + 0x598) != -1)) {
            *(iVar5 + 0x589) = 0;
            iVar5 = *(param_1 + 0x44);
            fVar18 = VectorSignedToFloat(*(*0x6d9f5c + iVar5),in_fpscr >> 0x15 & 3);
            fVar18 = fVar18 * fVar4;
            if ((fVar19 <= fVar18) && (fVar19 = fVar18, 0x3f800000 < fVar18)) {
                fVar19 = fVar3;
            }
            func_0x00723ad8(fVar19,*(iVar5 + 0x598),*(iVar5 + 0x59c),6);
        }
        iVar5 = 0;
        puVar14 = *(param_1 + 0x44) + 0x388;
        do {
            cVar1 = *(puVar14 + 2);
            if (cVar1 == '\x01' || cVar1 == '\x02') {
                iVar7 = func_0x0071ffa8(puVar14[4],puVar14[5]);
                if (iVar7 == 0) {
                    *puVar14 = 0xffffffff;
                    puVar14[1] = 0;
                    *(puVar14 + 2) = 0;
                    puVar14[4] = 0xffffffff;
                    puVar14[5] = 0xffffffff;
                    puVar14[6] = 0;
                    puVar14[7] = 0;
                }
            }
            else if ((cVar1 == '\x04') &&
                    (iVar7 = puVar14[7],
                    iVar11 - (iVar7 + (uVar6 < puVar14[6])) < 0 ==
                    (SBORROW4(iVar11,iVar7) != SBORROW4(iVar11 - iVar7,uVar6 < puVar14[6])))) {
                *(puVar14 + 2) = 1;
                uVar20 = func_0x0071fca8(puVar14[1],*(puVar14 + 10));
                *(puVar14 + 4) = uVar20;
            }
            iVar5 = iVar5 + 1;
            puVar14 = puVar14 + 8;
        } while (iVar5 < 0x10);
        if ((*(*(param_1 + 0x44) + 0x59c) != -1 || *(*(param_1 + 0x44) + 0x598) != -1) &&
           (iVar5 = func_0x0071ffa8(), iVar5 == 0)) {
            iVar5 = *(param_1 + 0x44);
            if (*(iVar5 + 0x58a) == '\0') {
                *(iVar5 + 0x598) = 0xffffffff;
                *(iVar5 + 0x59c) = 0xffffffff;
                *(*(param_1 + 0x44) + 0x590) = 0xffffffff;
            }
            else {
                uVar20 = func_0x0071fffc(*(iVar5 + 0x5a0),0);
                *(*(param_1 + 0x44) + 0x598) = uVar20;
            }
        }
        func_0x00723d88();
    }
    return 1;
}

