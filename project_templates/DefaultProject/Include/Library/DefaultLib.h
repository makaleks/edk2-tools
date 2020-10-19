/**
 * @file <LibName>.h
 *
 * @brief <your-brief>
 *
 * @copyright <your-copyright>
 */

#ifndef <LibIncludeGuard>
#define <LibIncludeGuard>

#include <Uefi.h>


/**
 * Concatenates 2 string into a new one, allocated in heap.
 *
 * @param[in] in_left_string           - string for the left part
 * @param[in] in_right_string          - string for the right part
 * @param[out] out_concatenated_string - pointer for the concatenated and
 *                                       allocated string
 * @return EFI_STATUS - EFI_SUCCESS in case of success, else
 *                      EFI_INVALID_PARAMETER in case of recieving
 *                      NULL pointer, else
 *                      an error, returned by gBS->AllocatePool()
 */
EFI_STATUS AllocConcatenated (
    CONST CHAR16 *in_left_string,
    CONST CHAR16 *in_right_string,
    CHAR16       **out_concatenated_string
);

#endif // <LibIncludeGuard>
