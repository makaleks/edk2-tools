#ifndef <DebugIncludeGuard>
#define <DebugIncludeGuard>

#include <Library/UefiLib.h>

#define <PackageNameMacro>_DEBUG

#ifdef <PackageNameMacro>_DEBUG
#define DbgPrintAscii( ...) AsciiPrint( __VA_ARGS__ )
#define DbgPrintUnicode(...) Print(__VA_ARGS__ )
#else
#define DbgPrintAscii(...)
#define DbgPrintUnicode(...)
#endif // <PackageNameMacro>_DEBUG


#endif // <DebugIncludeGuard>
