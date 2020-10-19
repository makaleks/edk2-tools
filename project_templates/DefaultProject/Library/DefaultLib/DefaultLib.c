#include <Library/<LibName>.h>
#include <Library/BaseLib.h>

#include "../../Debug/Debug.h"

// UEFI table of all boot services
extern EFI_BOOT_SERVICES *gBS;

EFI_STATUS AllocConcatenated (
    CONST CHAR16 *in_left_string,
    CONST CHAR16 *in_right_string,
    CHAR16       **out_concatenated_string
) {
    EFI_STATUS Status                     = EFI_SUCCESS;
    UINTN      left_string_length         = 0;
    UINTN      right_string_length        = 0;
    CHAR16     *concatenated_string       = NULL;
    UINTN      concatenated_string_length = 0;

    if (
        NULL == in_left_string
        || NULL == in_right_string
        || NULL == out_concatenated_string
    ) {
        return EFI_INVALID_PARAMETER;
    }
    left_string_length  = StrLen(in_left_string);
    right_string_length = StrLen(in_right_string);
    concatenated_string_length = left_string_length + right_string_length;

    Status = gBS->AllocatePool(
        EfiBootServicesData,
        sizeof(*concatenated_string)*(concatenated_string_length + 1),
        (VOID**)&concatenated_string
    );
    if (EFI_ERROR(Status)) {
        DbgPrintAscii(
"# Error %a: gBS->AllocatePool() returned %r (%a:%u)\n",
            __func__,
            Status,
            __FILE__,
            __LINE__
        );
        return Status;
    }
    gBS->SetMem(concatenated_string, concatenated_string_length + 1, 0);
    gBS->CopyMem(
        concatenated_string,
        (CHAR16*)in_left_string,
        sizeof(*in_left_string)*left_string_length
    );
    gBS->CopyMem(
        concatenated_string + left_string_length,
        (CHAR16*)in_right_string,
        sizeof(*in_right_string)*right_string_length
    );

    return EFI_SUCCESS;
}
