
void fcn.001420a0(int param_1)

{
    bool bVar1;
    int iVar2;
    uint unaff_r4;
    int *piVar3;
    int iVar4;
    uint unaff_lr;
    
    if ((param_1 == 0) || (*(*0x1420c0 + param_1) == 0)) {
        return;
    }
    if (param_1 == 0) {
        return;
    }
    iVar4 = **0x2fd6b0;
    piVar3 = iVar4 + 0x58;
    fcn.001244c8(piVar3);
    fcn.00128f84(iVar4,param_1);
    iVar2 = *(iVar4 + 0x60) + -1;
    *(iVar4 + 0x60) = iVar2;
    if (iVar2 != 0) {
        return;
    }
    *(iVar4 + 0x5c) = 0;
    do {
        iVar4 = *piVar3;
        iVar2 = -iVar4;
        bVar1 = hasExclusiveAccess(piVar3);
    } while (!bVar1);
    *piVar3 = iVar2;
    if (iVar4 != -1 && 0 < iVar2) {
        fcn.00122a40(**0x11b588,piVar3,0,1,0,0,unaff_r4,unaff_lr);
    }
    return;
}

