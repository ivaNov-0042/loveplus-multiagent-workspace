
uint fcn.006d87a4(int param_1)

{
    uint uVar1;
    
    if (*(param_1 + 0x1c0) == '\0') {
        if (*(param_1 + 0x1bc) == '\0') {
            fcn.00106f9c(param_1 + 0x1d4,*(*0x6d8808 + 8),0x10,0,*(param_1 + 0x5c),param_1 + 0x1ec);
            *(param_1 + 0x1bc) = 5;
            uVar1 = 1;
        }
        else {
            uVar1 = 0;
        }
    }
    else {
        uVar1 = 1;
    }
    return uVar1;
}

