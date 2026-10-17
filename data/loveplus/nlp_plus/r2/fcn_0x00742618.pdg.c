
int fcn.00742618(int param_1)

{
    int iVar1;
    
    iVar1 = fcn.00742530();
    if (iVar1 < 0) {
        iVar1 = 1;
    }
    else {
        iVar1 = *(*(param_1 + 0xc) + iVar1);
    }
    return iVar1;
}

