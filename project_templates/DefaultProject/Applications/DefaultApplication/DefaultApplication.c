
// <BLOCK-BEGIN lib>
// <BLOCK-END>


// UEFI table of all boot services
extern EFI_BOOT_SERVICES *gBS;

EFI_STATUS
EFIAPI
UefiMain (
    IN EFI_HANDLE       ImageHandle,
    IN EFI_SYSTEM_TABLE *SystemTable
) {
    EFI_STATUS Status = EFI_SUCCESS;

    Print(L"

    // <BLOCK-BEGIN lib>
    CONST CHAR16 left_string[]  = L"Hello, ";
    CONST CHAR16 right_string[] = L"World!";
    CHAR16       *concatenated  = NULL;

    Status = AllocConcatenated(str_left, str_right, &concatenated);
    if (EFI_ERROR(Status)) {
        DbgPrintAscii(
"
AllocateConcatenated returned %r (%a:%u)\n",
            Status,
            __FILE__,
            __LINE__
        );
        return Status;
    }
    Print(L"\n\
Left string:  %s\n
Right string: %s\n
Concatenated: %s\n",
        left_string,
        right_string,
        concatenated
    );
    gBS->FreePool(concatenated);
    concatenated = NULL;
    // <BLOCK-END>

    return Status;
}
