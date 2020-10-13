## @file
#  
#  TODO: Copyright for Package <PackageName>
#  
#  TODO: License for Package <PackageName>
#  
##

[Defines]
  PLATFORM_NAME                  = <PackageName>
  PLATFORM_GUID                  = <Guid>
  PLATFORM_VERSION               = 1.0
  DSC_SPECIFICATION              = 0x00010005
  OUTPUT_DIRECTORY               = Build/<PackagePath><PackageName>
  SUPPORTED_ARCHITECTURES        = IA32|IPF|X64|EBC|ARM
  BUILD_TARGETS                  = DEBUG|RELEASE|NOOPT
  SKUID_IDENTIFIER               = DEFAULT

[LibraryClasses]
# <BLOCK-BEGIN app lib driver>
  UefiApplicationEntryPoint|MdePkg/Library/UefiApplicationEntryPoint/UefiApplicationEntryPoint.inf
  UefiBootServicesTableLib|MdePkg/Library/UefiBootServicesTableLib/UefiBootServicesTableLib.inf
  UefiLib|MdePkg/Library/UefiLib/UefiLib.inf
  UefiRuntimeServicesTableLib|MdePkg/Library/UefiRuntimeServicesTableLib/UefiRuntimeServicesTableLib.inf
  MemoryAllocationLib|MdePkg/Library/UefiMemoryAllocationLib/UefiMemoryAllocationLib.inf
  DevicePathLib|MdePkg/Library/UefiDevicePathLib/UefiDevicePathLib.inf
  BaseLib|MdePkg/Library/BaseLib/BaseLib.inf
  BaseMemoryLib|MdePkg/Library/BaseMemoryLib/BaseMemoryLib.inf
  PrintLib|MdePkg/Library/BasePrintLib/BasePrintLib.inf
  DebugLib|MdePkg/Library/UefiDebugLibStdErr/UefiDebugLibStdErr.inf
  DebugPrintErrorLevelLib|MdePkg/Library/BaseDebugPrintErrorLevelLib/BaseDebugPrintErrorLevelLib.inf
  PcdLib|MdePkg/Library/BasePcdLibNull/BasePcdLibNull.inf
# <BLOCK-END>

# <BLOCK-BEGIN clib capp>
# Uefi C-main() Minimum START
  ShellCEntryLib|ShellPkg/Library/UefiShellCEntryLib/UefiShellCEntryLib.inf
# Required by ShellCEntryLib
  UefiApplicationEntryPoint|MdePkg/Library/UefiApplicationEntryPoint/UefiApplicationEntryPoint.inf
# Required by LibC
  UefiLib|MdePkg/Library/UefiLib/UefiLib.inf
# Required by LibC
  BaseLib|MdePkg/Library/BaseLib/BaseLib.inf
# Required by LibC
  BaseMemoryLib|MdePkg/Library/BaseMemoryLib/BaseMemoryLib.inf
# Required by LibC
  MemoryAllocationLib|MdePkg/Library/UefiMemoryAllocationLib/UefiMemoryAllocationLib.inf
# Required by UefiMemoryAllocationLib
  UefiBootServicesTableLib|MdePkg/Library/UefiBootServicesTableLib/UefiBootServicesTableLib.inf
# Required by UefiMemoryAllocationLib
  DebugLib|MdePkg/Library/UefiDebugLibStdErr/UefiDebugLibStdErr.inf
# Required by UefiLib
  UefiRuntimeServicesTableLib|MdePkg/Library/UefiRuntimeServicesTableLib/UefiRuntimeServicesTableLib.inf
# Required by UefiDebugLibStdErr
  PrintLib|MdePkg/Library/BasePrintLib/BasePrintLib.inf
# Required by UefiDebugLibStdErr
  DebugPrintErrorLevelLib|MdePkg/Library/BaseDebugPrintErrorLevelLib/BaseDebugPrintErrorLevelLib.inf
# Required by UefiDebugLibStdErr
  PcdLib|MdePkg/Library/BasePcdLibNull/BasePcdLibNull.inf
# Required by UefiShellLib
  HiiLib|MdeModulePkg/Library/UefiHiiLib/UefiHiiLib.inf
# Required by HiiLib
  UefiHiiServicesLib|MdeModulePkg/Library/UefiHiiServicesLib/UefiHiiServicesLib.inf
# Required by UefiShellLib
  DevicePathLib|MdePkg/Library/UefiDevicePathLib/UefiDevicePathLib.inf
# Required by StdLib
  UefiRuntimeLib|MdePkg/Library/UefiRuntimeLib/UefiRuntimeLib.inf
# Required by StdLib
  UefiDriverEntryPoint|MdePkg/Library/UefiDriverEntryPoint/UefiDriverEntryPoint.inf
# Uefi C-Std Minimum End
# <BLOCK-END>

# <BLOCK-BEGIN lib clib>
# Provided libraries
  <LibName>|<PackagePath><PackageName>/Library/<LibName:DefaultLib>/<LibName:DefaultLib>.inf
# <BLOCK-END>

[Components]
# <BLOCK-BEGIN lib clib>
# Library
# Without additional defined
  <LibName>|<PackagePath><PackageName>/Library/<LibName:DefaultLib>/<LibName:DefaultLib>.inf

# With additional defined

#  <LibName>/Library/<LibName>/<LibName>.inf {
#    <BuildOptions>
#    GCC:*_*_X64_CC_FLAGS = -DSOMEFLAG
#  }
# <BLOCK-END>

# <BLOCK-BEGIN app>
  <AppName>|<PackagePath><PackageName>/Applications/<AppName:DefaultApplication>/<AppName:DefaultApplication>.inf
# <BLOCK-END>

[Components.IA32]

[Components.X64]

[Components.IPF]

[Components.EBC]

[Components.ARM]

# <BLOCK-BEGIN capp clib>
##############################################################################
##
##  Include Boilerplate text required for building with the Standard Libraries.
##
###############################################################################
!include StdLib/StdLib.inc
# <BLOCK-END>
