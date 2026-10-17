
uint fcn.006d84ec(int param_1)

{
    uint uVar1;
    
    if (*(param_1 + 0x1bf) == '\0') {
        if (*(param_1 + 0x1bc) == '\0') {
            fcn.00106f9c(param_1 + 0x1c4,*(param_1 + 0x50),0x10,0,*(param_1 + 0x44),param_1 + 0x1ec);
            *(param_1 + 0x1bc) = 4;
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

