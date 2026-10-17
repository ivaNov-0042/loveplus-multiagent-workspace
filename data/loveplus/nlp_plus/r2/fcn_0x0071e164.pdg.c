
void fcn.0071e164(uchar param_1,uint param_2,uint param_3,uint param_4,uint param_5,uint param_6,uint param_7,
                 uint param_8,uint param_9,ushort param_10,uint param_11,uint param_12,char param_13)

{
    int16_t iVar1;
    int iVar2;
    int iVar3;
    uchar *puVar4;
    uint uVar5;
    uint16_t uVar6;
    code *UNRECOVERED_JUMPTABLE_00;
    uint in_stack_00000040;
    uint in_stack_00000044;
    uint in_stack_00000048;
    uint in_stack_0000004c;
    uint in_stack_00000050;
    uint in_stack_00000054;
    uint in_stack_00000058;
    
    iVar3 = fcn.0066e744(*0x71e264);
    iVar2 = *0x71e268;
    uVar5 = 0;
    if (iVar3 != 0) {
        iVar1 = *(*0x71e268 + 2);
        uVar6 = iVar1 + 1;
        puVar4 = *0x71e26c + iVar1 * 0x70;
        if (0x3f < uVar6) {
            uVar6 = iVar1 - 0x3f;
        }
        if (*(*0x71e268 + 4) == uVar6 || puVar4 == NULL) {
            fcn.0066e7b4(*0x71e264);
    //WARNING: Could not recover jumptable at 0x0071e260. Too many branches
    //WARNING: Treating indirect jump as call
            (*UNRECOVERED_JUMPTABLE_00)(0);
            return;
        }
        *(puVar4 + 8) = param_3;
        *(puVar4 + 0xc) = param_4;
        *puVar4 = param_1;
        *(puVar4 + 0x14) = param_6;
        *(puVar4 + 0x18) = param_7;
        *(puVar4 + 0x1c) = param_8;
        *(puVar4 + 0x20) = param_9;
        *(puVar4 + 0x24) = param_10;
        *(puVar4 + 0x28) = param_11;
        *(puVar4 + 0x2c) = param_12;
        *(puVar4 + 0x50) = in_stack_00000040;
        *(puVar4 + 0x54) = in_stack_00000044;
        *(puVar4 + 0x58) = in_stack_00000048;
        *(puVar4 + 0x5c) = in_stack_0000004c;
        *(puVar4 + 0x60) = in_stack_00000050;
        *(puVar4 + 100) = in_stack_00000054;
        *(puVar4 + 0x68) = in_stack_00000058;
        if (param_13 != '\0') {
            fcn.00302a48(puVar4 + 0x30,&param_13);
        }
        if (uVar6 < 0x40) {
            *(iVar2 + 2) = uVar6;
        }
        fcn.0066e7b4(*0x71e264);
        uVar5 = 1;
    }
    //WARNING: Could not recover jumptable at 0x0071e24c. Too many branches
    //WARNING: Treating indirect jump as call
    (*UNRECOVERED_JUMPTABLE_00)(uVar5);
    return;
}

