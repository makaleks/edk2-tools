#include <Uefi.h>
#include <Library/UefiLib.h>

#include "../../Debug/Debug.h"

// <BLOCK-BEGIN lib>
#include <Library/<LibName>.h>
// <BLOCK-END>

// UEFI table of all boot services
extern EFI_BOOT_SERVICES *gBS;

// <BLOCK-BEGIN app>
EFI_STATUS
EFIAPI
UefiMain (
    IN EFI_HANDLE       ImageHandle,
    IN EFI_SYSTEM_TABLE *SystemTable
) {
// <BLOCK-END>
    Print(L"EFI-c-app <AppName> starts\n");
// <BLOCK-BEGIN capp>
int main (int argc, char *argv[]) {
    Print(L"EFI-app <AppName> starts\n");
// <BLOCK-END>
    EFI_STATUS Status = EFI_SUCCESS;

    // <BLOCK-BEGIN lib>
    CONST CHAR16 left_string[]  = L"Hello, ";
    CONST CHAR16 right_string[] = L"World!";
    CHAR16       *concatenated  = NULL;

    Status = AllocConcatenated(left_string, right_string, &concatenated);
    if (EFI_ERROR(Status)) {
        DbgPrintAscii(
"# Error %a: AllocateConcatenated returned %r (%a:%u)\n",
            __func__,
            Status,
            __FILE__,
            __LINE__
        );
        return Status;
    }
    Print(L"\n\
Left string:  %s\n\
Right string: %s\n\
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
