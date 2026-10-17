
void fcn.00142754(int param_1,int param_2,int param_3)

{
    int iVar1;
    int iVar2;
    int iVar3;
    
    iVar1 = *(param_1 + 0x1464);
    if (param_2 < 2) {
        param_2 = 1;
    }
    iVar2 = 0;
    iVar3 = 1;
    if (1 < param_2 + 1) {
        do {
            func_0x00302b20(*(param_3 + iVar2 * 4),param_1 + iVar2 * 0x500 + 0xa08,iVar1 * 0x1c >> 4);
            iVar3 = iVar3 + 1;
            iVar2 = iVar2 + 1;
        } while (iVar3 < param_2 + 1);
    }
    return;
}

