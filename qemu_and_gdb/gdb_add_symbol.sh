#!/bin/sh

# CONFIG HERE #################

# required
CONFIG_QEMU_DEBUG_PATH="../debug.log"

# optional, can be changed 
# when calling this script
CONFIG_EFI_FILE="Shell.efi"

# optional, can be changed 
# when calling this script
CONFIG_IMAGE_ENTRY_NUM=1

# ADJUST HERE #################

# these defaults are strong, but 
# who knows, if gdb or qemu 
# will change their output format

ADJUST_QEMU_DEBUG_POS_ADDRESS=4
ADJUST_GDB_LEAST_LINES=3
ADJUST_GDB_LINE_OFFSET=2
ADJUST_GDB_TEXT_ADDRES_WORD_NUM=1
ADJUST_GDB_DATA_ADDRES_WORD_NUM=3

# SCRIPT STARTS ###############

QEMU_DEBUG_PATH="$CONFIG_QEMU_DEBUG_PATH"
EFI_FILE="$CONFIG_EFI_FILE"
IMAGE_ENTRY_NUM="$CONFIG_IMAGE_ENTRY_NUM"

IS_VERBOSE_MODE=0

IS_CONFIG_EFI_FILE=" (preset value)"
IS_CONFIG_QEMU_DEBUG_PATH="$IS_CONFIG_EFI_FILE"
IS_CONFIG_IMAGE_ENTRY_NUM="$IS_CONFIG_EFI_FILE"

# Check if help is required
for arg in "$@"; do
    if [ "$arg" = 'help' ] || [ "$arg" = '-h' ] || [ "$arg" = '--help' ]; then
        printf "\
Generate 'add-symbol-file' command for gdb.
usage: $(basename -- $0) [EFI_FILE.efi [IMAGE_ENTRY_NUM [../QEMU_DEBUG_PATH.log]]] [BE_VERBOSE]
        -h, --help, help - print this message and do nothing

        Pass 'BE_VERBOSE' flag at the end to get more output
"
        exit
    elif [ "$arg" = "BE_VERBOSE" ]; then
        IS_VERBOSE_MODE=1
    fi
done

# Check if EFI_FILE is provided
if [ -n "$1" ] && [ "$1" != "BE_VERBOSE" ]; then
    EFI_FILE="$1"
    IS_CONFIG_EFI_FILE=""
    # Check if IMAGE_ENTRY_NUM provided
    if [ -n "$2" ] && [ "$2" != "BE_VERBOSE" ]; then
        IMAGE_ENTRY_NUM="$2"
        IS_CONFIG_IMAGE_ENTRY_NUM=""
        # Check if QEMU_DEBUG_PATH provided
        if [ -n "$3" ] && [ "$3" != "BE_VERBOSE" ]; then
            QEMU_DEBUG_PATH="$3"
            IS_CONFIG_QEMU_DEBUG_PATH=""
        fi
    fi
fi

# Check config
MUST_EXIT=0
if [ ! -f "$EFI_FILE" ]; then
    printf "# ERROR: EFI_FILE '%s'%s not found!\n" "$EFI_FILE" "$IS_CONFIG_EFI_FILE"
    MUST_EXIT=1
fi
if [ ! -f "$EFI_FILE" ]; then
    printf "# ERROR: QEMU_DEBUG_PATH '%s'%s not found!\n" "$QEMU_DEBUG_PATH" "$IS_CONFIG_QEMU_DEBUG_PATH"
    MUST_EXIT=1
fi
if [ "$MUST_EXIT" -eq 1 ]; then
    exit
fi
# Log
if [ "$IS_VERBOSE_MODE" -eq 1 ]; then
    printf "\
EFI_FILE       : '$EFI_FILE'
QEMU_DEBUG_PATH: '$QEMU_DEBUG_PATH'
IMAGE_ENTRY_NUM: $IMAGE_ENTRY_NUM
\n"
fi

# Get EFI image loading address
GREG_DEBUG=`grep --max-count=$IMAGE_ENTRY_NUM " $EFI_FILE" "$QEMU_DEBUG_PATH" | tr -d "\r"`
if [ $(echo "$GREG_DEBUG" | wc -l) -lt "$IMAGE_ENTRY_NUM" ]; then
    printf "# ERROR: number of entries is less than IMAGE_ENTRY_NUM='%s'%s!\n" "$IMAGE_ENTRY_NUM" "$IS_CONFIG_IMAGE_ENTRY_NUM"
    exit
fi
LOADING_STR=`echo "$GREG_DEBUG" | tail -n 1`
LOADING_ADDRESS=`echo "$LOADING_STR" | cut -d ' ' -f "$ADJUST_QEMU_DEBUG_POS_ADDRESS"`
# Check address exists
if [ -z "$LOADING_ADDRESS" ]; then
    printf "\
# ERROR: Could not find address string in file '%s'. 
         Are you sure you loaded image '%s' before running this script?
" "$QEMU_DEBUG_PATH" "$EFI_FILE"
    exit
fi
# remove leading zeros
LOADING_ADDRESS=`printf '0x%x' "$LOADING_ADDRESS"`
# Log
if [ "$IS_VERBOSE_MODE" -eq 1 ]; then
    printf "Address source: '%s'\nAddress value:  '%s'\n\n" "$LOADING_STR" "$LOADING_ADDRESS"
fi

# Get single line from gdb output
GDB_SOURCE=`gdb -q -ex "file $EFI_FILE" -ex 'info files' -ex 'quit' | tail -n "$ADJUST_GDB_LEAST_LINES"`

TEXT_ADDRESS_BASE=`echo "$GDB_SOURCE" | head -n 1 | cut -d ' ' -f "$ADJUST_GDB_TEXT_ADDRES_WORD_NUM"`
DATA_ADDRESS_BASE=`echo "$GDB_SOURCE" | head -n 1 | cut -d ' ' -f "$ADJUST_GDB_DATA_ADDRES_WORD_NUM"`
# Check address for gdb .text and .data
if [ -z "$TEXT_ADDRESS_BASE" ]; then
    printf "# ERROR: something got wrong, so TEXT_ADDRESS_BASE can't be got from GDB\n"
    MUST_EXIT=1
fi
if [ -z "$DATA_ADDRESS_BASE" ]; then
    printf "# ERROR: something got wrong, so DATA_ADDRESS_BASE can't be got from GDB\n"
    MUST_EXIT=1
fi
if [ "$MUST_EXIT" -eq 1 ]; then
    exit
fi
# remove leading zeros
TEXT_ADDRESS_BASE=`printf '0x%x' "$TEXT_ADDRESS_BASE"`
DATA_ADDRESS_BASE=`printf '0x%x' "$DATA_ADDRESS_BASE"`
# Log
if [ "$IS_VERBOSE_MODE" -eq 1 ]; then
    printf "\
GDB source: \n%s
GDB result: 
	text_address: '%s'
	data_address: '%s'
\n" "$GDB_SOURCE" "$TEXT_ADDRESS_BASE" "$DATA_ADDRESS_BASE"
fi

TEXT_ADDRESS_EXPR=`printf '%s + %s' "$LOADING_ADDRESS" "$TEXT_ADDRESS_BASE"`
DATA_ADDRESS_EXPR=`printf '%s + %s + %s' "$LOADING_ADDRESS" "$TEXT_ADDRESS_BASE" "$DATA_ADDRESS_BASE"`

TEXT_ADDRESS=`printf '0x%x' "$(($TEXT_ADDRESS_EXPR))"`
DATA_ADDRESS=`printf '0x%x' "$(($DATA_ADDRESS_EXPR))"`

if [ "$IS_VERBOSE_MODE" -eq 1 ]; then
    DATA_EXPR_LENGTH=`echo -n "$DATA_ADDRESS_EXPR" | wc -m`
    TEXT_FORMAT=`printf '%%-%ss' "$DATA_EXPR_LENGTH"`
    TEXT_ADDRESS_EXPR=`printf "$TEXT_FORMAT" "$TEXT_ADDRESS_EXPR"`
    printf "\
text = $TEXT_ADDRESS_EXPR = $TEXT_ADDRESS
data = $DATA_ADDRESS_EXPR = $DATA_ADDRESS
\n"
    echo "Result gdb command:"
fi

echo "add-symbol-file ${EFI_FILE%.*}.debug $TEXT_ADDRESS -s .data $DATA_ADDRESS"

