#include <Uefi.h>

#include "../../Debug/Debug.h"

// UEFI table of all boot services
extern EFI_BOOT_SERVICES *gBS;
// UEFI table of all runtime services
extern EFI_RUNTIME_SERVICES *gRT;

EFIAPI EFI_STATUS (*gGetVariableBackup)(CHAR16*,EFI_GUID*,UINT32*,UINTN*,VOID*);

EFI_STATUS
EFIAPI
get_variable_hook(
    CHAR16   *in_variable_name,
    EFI_GUID *in_variable_vendor_guid,
    UINT32   *optional_in_variable_attributes,
    UINTN    *in_out_variable_data_byte_size,
    VOID     *optional_out_variable_data
) {
    EFI_STATUS Status = EFI_SUCCESS;
    Status = gGetVariableBackup(
        in_variable_name,
        in_variable_vendor_guid,
        optional_in_variable_attributes,
        in_out_variable_data_byte_size,
        optional_out_variable_data
    );
    Print(
        L"Requested variable \"%s\"(%g), Status=\"%r\"\n",
        in_variable_name,
        in_variable_vendor_guid,
        Status
    );
    return Status;
}

EFI_STATUS
EFIAPI
UefiDriverUnload (
  IN EFI_HANDLE ImageHandle
) {
    gRT->GetVariable = gGetVariableBackup;
    return EFI_SUCCESS;
}

/**
  as the real entry point for the application.

  @param[in] ImageHandle    The firmware allocated handle for the EFI image.  
  @param[in] SystemTable    A pointer to the EFI System Table.
  
  @retval EFI_SUCCESS       The entry point is executed successfully.
  @retval other             Some error occurs when executing this entry point.

**/
EFI_STATUS
EFIAPI
UefiDriverMain (
  IN EFI_HANDLE        ImageHandle,
  IN EFI_SYSTEM_TABLE  *SystemTable
) {
    EFI_STATUS Status = EFI_SUCCESS;
    Print(L"Driver starts..\n");

    gGetVariableBackup = gRT->GetVariable;
    gRT->GetVariable = get_variable_hook;
    Print(L"gBS->GetVariable replaced!\n");
    /*
    if (Status) {
        DbgPrintAscii(
"# Error UefiDriverMain(): \
gBS->InstallMultipleProtocolInterfaces() returned %r (%a:%u)\n",
            Status, __FILE__, __LINE__
        );
    }
    */

    Print(L"Driver finishes..\n");
    return Status;
}

