
void fcn.0076b67c(uint param_1,int16_t *param_2,uint16_t *param_3,uint32_t param_4)

{
    int16_t iVar1;
    int16_t iVar2;
    int16_t *piVar3;
    int16_t *extraout_r1;
    int16_t *piVar4;
    int16_t *piVar5;
    int16_t *extraout_r2;
    int16_t *piVar6;
    int16_t *piVar8;
    int16_t *piVar9;
    uint16_t *puVar10;
    int iVar11;
    int iVar12;
    uint16_t uVar13;
    int iVar14;
    int16_t *piVar15;
    bool bVar16;
    int16_t aiStack_548 [640];
    int iStack_48;
    uint uStack_44;
    int iStack_40;
    int iStack_3c;
    int iStack_38;
    int16_t *piVar7;
    
    func_0x0075dd2c(param_1,aiStack_548,param_4);
    piVar15 = aiStack_548 + (param_4 & 0xfffffffe);
    iStack_48 = param_4 >> 1;
    bVar16 = iStack_48 == 0x140;
    piVar3 = extraout_r2;
    if (bVar16) {
        piVar3 = *0x76b7a8;
    }
    piVar6 = *0x76b7ac;
    piVar4 = extraout_r1;
    if (bVar16) {
        piVar4 = piVar3 + 0x280;
        piVar6 = piVar3;
    }
    uStack_44 = 0x1000;
    if (!bVar16) {
        piVar4 = piVar6 + 0x140;
    }
    piVar3 = param_2 + iStack_48;
    piVar9 = piVar15 + -iStack_48;
    iStack_40 = iStack_48;
    if (iStack_48 < 2) {
        iStack_40 = 1;
    }
    iStack_40 = iStack_40 + 1;
    iVar11 = 1;
    piVar8 = piVar9;
    puVar10 = param_3 + iStack_48;
    if (1 < iStack_40) {
        do {
            piVar7 = piVar6 + 1;
            iVar1 = *piVar6;
            piVar15 = piVar15 + -1;
            piVar5 = piVar4 + 1;
            iVar2 = *piVar4;
            piVar6 = piVar6 + 2;
            iVar11 = iVar11 + 1;
            iStack_3c = iVar1 * *piVar15;
            piVar9 = piVar8 + 1;
            piVar4 = piVar4 + 2;
            iStack_38 = iVar2 * *piVar8;
            piVar3 = piVar3 + -1;
            iVar14 = *piVar7 * *param_2 + iVar1 * *piVar15 + 0x1000;
            iVar12 = (iVar2 * *piVar8 - *piVar5 * *piVar3) + 0x1000;
            if (iVar14 >> 0x1c == iVar14 >> 0x1f) {
                uVar13 = iVar14 >> 0xd;
            }
            else {
                uVar13 = *0x76b7b0 ^ iVar14 >> 0x1f;
            }
            iVar14 = iVar12 >> 0x1c;
            bVar16 = iVar14 != iVar12 >> 0x1f;
            if (bVar16) {
                iVar14 = *0x76b7b0;
            }
            *param_3 = uVar13;
            if (bVar16) {
                uVar13 = iVar14 ^ iVar12 >> 0x1f;
            }
            else {
                uVar13 = iVar12 >> 0xd;
            }
            *puVar10 = uVar13;
            piVar8 = piVar9;
            param_3 = param_3 + 1;
            param_2 = param_2 + 1;
            puVar10 = puVar10 + 1;
        } while (iVar11 < iStack_40);
    }
    func_0x00302b20(piVar3,piVar9,iStack_48 << 1);
    return;
}

