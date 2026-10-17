
int fcn.0014250c(int param_1,int param_2)

{
    int iVar1;
    int iVar2;
    
    iVar1 = 0;
    iVar2 = 0x20;
    do {
        if (*(param_1 + iVar1 * 4 + 0xf00) == 0) {
            *(*0x142564 + param_2) = 0;
            *(param_1 + iVar1 * 4 + 0xf00) = param_2;
            return iVar1;
        }
        iVar2 = iVar2 + -1;
        iVar1 = iVar1 + 1;
    } while (iVar2 != 0);
    return -1;
}

