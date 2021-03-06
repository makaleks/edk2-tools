#!/usr/bin/env python3

import sys
import os
import uuid
import argparse
import re
import glob
from pathlib import Path

NotPassed = None
FlagOnly = ''

ThisFileDirPath = os.path.abspath(os.path.dirname(__file__))
DestDirPath = ''

def print_log(dbg_show, log_str):
    if dbg_show:
        print(log_str)

def my_get_uuid(*args):
    return str(uuid.uuid4())

def get_app_name(args):
    if args.app is not None:
        if args.app is FlagOnly:
            return args.ProjectName
        else:
            return args.app
    else:
        if args.capp is FlagOnly:
            return args.ProjectName
        else:
            return args.capp

def get_driver_name(args):
    if args.driver is FlagOnly:
        return args.ProjectName
    else:
        return args.driver

def get_lib_name(args):
    if args.lib is FlagOnly:
        if args.ProjectName[:3].lower() == 'lib':
            prefix = ''
        else:
            prefix = 'Lib'
        if args.driver is not NotPassed:
            return prefix + get_driver_name(args)
        else:
            return prefix + args.ProjectName
    else:
        return args.lib

def _to_include_guard_base(s):
    result = ''
    for c in s:
        if c.isupper():
            result += '_'
        result += c.upper()
    return result

def get_package_name_macro(args):
    return _to_include_guard_base(get_package_name(args))

def get_lib_include_guard(args):
    return _to_include_guard_base(get_lib_name(args) + 'H')

def get_protocol_include_guard(args):
    return _to_include_guard_base(get_driver_name(args) + 'H')

def get_debug_include_guard(args):
    return _to_include_guard_base(get_package_name(args) + 'Debug' + 'H')

def get_debug_flag(args):
    return _to_include_guard_base(get_package_name(args) + 'Debug')

def get_package_name(args):
    return args.ProjectName
def get_package_prefix(args):
    return args.prefix

single_tag_list = [
    {'tag': 'PackageName',          'replace-by': get_package_name},
    {'tag': 'PackageNameMacro',     'replace-by': get_package_name_macro},
    {'tag': 'PackagePath',          'replace-by': get_package_prefix},
    {'tag': 'Guid',                 'replace-by': my_get_uuid},
    {'tag': 'LibName',              'replace-by': get_lib_name},
    {'tag': 'DriverName',           'replace-by': get_driver_name},
    {'tag': 'AppName',              'replace-by': get_app_name},
    {'tag': 'LibIncludeGuard',      'replace-by': get_lib_include_guard},
    {'tag': 'ProtocolIncludeGuard', 'replace-by': get_protocol_include_guard},
    {'tag': 'DebugIncludeGuard',    'replace-by': get_debug_include_guard},
    {'tag': 'DebugFlag',            'replace-by': get_debug_flag},
]

single_tag_contains_origin = [
    'LibName', 'DriverName', 'AppName'
]

TAG_BLOCK_BEGIN = 'BLOCK-BEGIN'
TAG_BLOCK_END   = 'BLOCK-END'

#tag_block_list = ['lib', 'driver', 'app', 'clib', 'capp', 'protocol']
#tag_block_list = ['lib', 'driver', 'app', 'clib', 'capp']
tag_block_list = ['lib', 'driver', 'app', 'capp']

def get_tag_block_begin (tag_str):
    return '<{} {}>'.format(TAG_BLOCK_BEGIN, tag_str)
def get_tag_block_end ():
    return '<{}>'.format(TAG_BLOCK_END)

def get_line_after_any_only_comment (line, comment_str):
    code_delimiter_comment = line.partition(comment_str)
    if (
        '' != code_delimiter_comment[0].rstrip()
        or '' == code_delimiter_comment[1]
        or '' == code_delimiter_comment[2]
    ):
        return ''
    else:
        return code_delimiter_comment[2].strip()

def line_contains_tag_block_begin (line, comment_str):
    result_match = []
    comment_content = get_line_after_any_only_comment(line, comment_str)
    if not comment_content:
        return result_match
    pattern = re.compile(
        '^{}$'.format(get_tag_block_begin(r'(\w+( +\w+)*)')), re.ASCII
    )
    matched = pattern.match(comment_content)
    if not matched:
        return result_match
    else:
        tags_used = filter(
            None, [s.strip() for s in matched.group(1).split(' ')]
        )
        for tag in tags_used:
            if tag in tag_block_list:
                result_match.append(tag)

    return result_match

def line_contains_tag_block_end (line, comment_str):
    code_delimiter_comment = line.partition(comment_str)
    if (
        '' != code_delimiter_comment[0].rstrip()
        or code_delimiter_comment[1] == ''
        or code_delimiter_comment[2] == ''
    ):
        return False
    comment_content = code_delimiter_comment[2].strip()
    pattern = re.compile('^{}$'.format(get_tag_block_end()), re.ASCII)
    if pattern.match(comment_content):
        return True
    else:
        return False

'''
Driver  exists: Driver=<BaseName>, Library=Lib<BaseName>, App=<BaseName>Demo
Library exists: Library=Lib<BaseName>, App=<BaseName>Demo
Only app:       App=<BaseName>
-a --app   - add app
-l --lib   - add library
-ca --capp - add C app
-d --drv   - add driver
'''

def replace_tag_by_itself(tag_entry, args):
    try:
       return str(tag_entry['replace-by'](args) or '')
    except:
        return ''

def replace_tag_in_line (args, line, use_origin = False):
    #origin_line = line
    for tag_candidate in single_tag_list:
        # Split by pattern, include (..) content, exclude (?:..) content
        splitted = re.split(
            r'(<{}(?::\w+)?>)'.format(tag_candidate['tag']), line
        )
        new_line = ''
        tag_extractor = re.compile(
            r'<(?:{})(?::(\w+))?>'.format(tag_candidate['tag'])
        )
        #print("splitted: {}".format(splitted))
        for splitted_entry in splitted:
            is_tag = tag_extractor.match(splitted_entry)
            #print('entry: {}, tag: {}, is_tag: {} ({})'.format(splitted_entry, tag_candidate['tag'], is_tag, True if is_tag else False))
            tag_origin = ''
            if not is_tag:
                new_line += splitted_entry
            else:
                try:
                    tag_origin = is_tag.group(1)
                except:
                    tag_origin = ''
                #print('entry:"{}",match:"{}",group:"{}"'.format(splitted_entry,str(is_tag.groups()),is_tag.group(1)))
                tag_replacement = replace_tag_by_itself(tag_candidate, args)
                if use_origin and tag_origin:
                    tag_replacement = tag_origin
                new_line += tag_replacement

        #print('new_line: {}, line: {}'.format(new_line, line))
        line = new_line

    #print('done\n')
    return line

def process_line_with_comment (
    args, line, comment_str, erase_most = False, use_origin = False, dbg_filename = None
):
    if line == '':
        # Do nothing with empty lines, even removing
        return line

    if not args.verbose and not line.isspace():
        # If line is comment-only, return it
        non_whitespace_ids = len(line) - len(line.lstrip())
        if line[non_whitespace_ids] == comment_str:
            # Delete comment-only line
            return None
        # Remove comment from line
        line = line.split(comment_str)[0].rstrip()
    # Unplug comment to prevent its replacement
    code_hash_comment = line.partition(comment_str)
    if not erase_most:
        line = (
            replace_tag_in_line(args, code_hash_comment[0])
            + code_hash_comment[1]
            + code_hash_comment[2]
        )
    else:
        line = replace_tag_in_line(args, code_hash_comment[0], use_origin=use_origin)
    return line

def is_current_tag_block_requested(tag_stack, requested_targets):
    for target_list in tag_stack:
        if not any(
            [tag_target in requested_targets for tag_target in target_list]
        ):
            return False
    return True

def process_file_content (
    args, file_content, comment_str, requested_targets, dbg_show = None
):
    result_file_content = ''
    tag_stack = []
    print_log(dbg_show, '# Running process_file_content:')
    for line in file_content.splitlines():
        dbg_str = '- Line: {}\n  '.format(line)
        if comment_str in line:
            # Check tag-block comments
            tags_found = line_contains_tag_block_begin(line, comment_str)
            if tags_found:
                tag_stack.append(tags_found)

                dbg_str = '{}Found tag_begin({}), total({})'.format(
                    dbg_str, tags_found, tag_stack
                )
                print_log(dbg_show, dbg_str)
                continue
            if line_contains_tag_block_end(line, comment_str):
                if not tag_stack:
                    print("Warning: unexpected tag_end")
                else:
                    tag_stack.pop()

                    dbg_str = '{}Found tag_end, total({})'.format(
                        dbg_str, tag_stack
                    )
                    print_log(dbg_show, dbg_str)
                continue

        if not tag_stack or is_current_tag_block_requested(
            tag_stack, requested_targets
        ):
            line = process_line_with_comment(args, line, comment_str)
            if line is None:
                continue
            result_file_content += line + '\n'

            dbg_str = '{}Done: {}'.format(dbg_str, line)
        else:
            dbg_str = '{}Not allowed for args: {}'.format(
                dbg_str, args
            )
        print_log(dbg_show, dbg_str)
    return result_file_content

def is_section(line, section_name):
    if section_name:
        # Matchs non-empty section
        section_name = '[{}]'.format(section_name)
    else:
        # Matchs all other sections
        section_name = '['
    return line.lstrip()[0:len(section_name)] == section_name

def line_to_origin_outcome_pair(args, line, comment_str):
    def _rm_project_prefix(args, path):
        prefix = os.path.join(args.prefix, args.ProjectName)
        if os.path.commonpath([path, prefix]):
            #print('# path: {}, prefix: {}, result: {}'.format(path, prefix, os.path.relpath(path, prefix)))
            path = os.path.relpath(path, prefix)
        return path
    def _extract_path(args, line):
        line = line.strip()
        line = line.split('|')[-1]
        line = _rm_project_prefix(args, line)
        return line

    line_origin = process_line_with_comment(
        args, line, comment_str, erase_most=True, use_origin=True
    )
    line_outcome = process_line_with_comment(
        args, line, comment_str, erase_most=True, use_origin=False
    )
    if not line_origin:
        return None

    line_origin  = _extract_path(args, line_origin)
    line_outcome = _extract_path(args, line_outcome)

    #line_origin  = line_origin.strip()
    #line_outcome = line_outcome.strip()
    #line_origin  = line_origin.split('|')[-1]
    #line_outcome = line_outcome.split('|')[-1]

    return {'origin': line_origin, 'outcome': line_outcome}

# Returns
# { "excluded_dirs": [],
#   "path_mappings":  [{"src_path", "dest_path"}] }
def get_dirs_info_from_dsc(
    args, dsc_content, requested_targets, dbg_show = None
):
    # Help someone me to make it Better
    excluded_dirs = []
    path_mappings = []

    is_component = False # [Components] section in .dsc-file
    tag_stack    = []

    print_log(dbg_show, '# Running get_dirs_info_from_dsc:')
    dbg_is_components_section_found = False
    for line in dsc_content.splitlines():
        if not is_component:
            if is_section(line, 'Components'):
                dbg_is_components_section_found = True
                print_log(dbg_show, '[Components] section found')
                is_component = True
        elif is_component:
            if is_section(line, ''):
                is_component = False
                if tag_stack:
                    print(
                        "Warning: unclosed tags at [Components] section end: "
                        + str(tag_stack)
                    )
                break
            dbg_str = '- Line: {}\n  '.format(line)

            tags_found = line_contains_tag_block_begin(line, '#')
            if tags_found:
                tag_stack.append(tags_found)

                dbg_str = '{}Found tag_end, total_list({})'.format(
                    dbg_str, tag_stack
                )
                print_log(dbg_show, dbg_str)
                continue
            if line_contains_tag_block_end(line, '#'):
                if not tag_stack:
                    print("Warning: unexpected tag_end")
                else:
                    tag_stack.pop()

                    dbg_str = '{}Found tag_end, total_list({})'.format(
                        dbg_str, tag_stack
                    )
                    print_log(dbg_show, dbg_str)
                continue

            lines_map = line_to_origin_outcome_pair(args, line, '#')
            if not lines_map:
                continue

            if not is_current_tag_block_requested(
                tag_stack, requested_targets
            ):
                dirname = os.path.dirname(lines_map['origin'])
                excluded_dirs.append(dirname)

                dbg_str = '{}excluded_dirs += {}'.format(
                    dbg_str, excluded_dirs
                )
            else:
                path_mappings.append({ "src_path":  lines_map['origin'],
                                      "dest_path": lines_map['outcome'] })
    result = { 'excluded_dirs': excluded_dirs,
               'path_mappings': path_mappings }
    if not dbg_is_components_section_found:
        print_log(dbg_show, '[Components] section was not found!')
    else:
        print_log(dbg_show, '  Processing result: {}'.format(result))
    return result

def get_requested_targets(args):
    requestable = tag_block_list
    #print(args)
    requested_targets = {
            field_name for field_name in requestable
            if getattr(args, field_name) is not None
    }
    #print('requested tags: {}'.format(requested_targets))
    return requested_targets

def is_file_must_be_ignored(relative_path, dirs_info):
    if os.path.commonpath(['Include/', relative_path]):
        # excluding from Include/ is a special case
        for d in dirs_info['excluded_dirs']:
            dirname = os.path.basename(d)
            #print('dirname: ' + dirname + ', relative_path ' + relative_path + ' is ' + str(dirname in relative_path))
            if dirname in relative_path:
                return True
    else:
        for d in dirs_info['excluded_dirs']:
            if os.path.commonpath([d, relative_path]):
                return True
    return False

def replace_to_dest_if_src_exists(dirs_info, relative_path):
    if os.path.commonpath(['Include/', relative_path]):
        # excluding from Include/ is a special case
        (path_before_ext, path_ext) = os.path.splitext(os.path.basename(relative_path))
        for pair in dirs_info['path_mappings']:
            key = os.path.basename(os.path.dirname(pair['src_path']))
            if key in path_before_ext:
                value = os.path.basename(os.path.dirname(pair['dest_path']))
                # replace all matching path nodes:
                result_path = ''
                while path_before_ext:
                    path_node = os.path.basename(path_before_ext)
                    if path_node == key:
                        path_node = value
                    result_path = os.path.join(result_path, path_node)
                    path_before_ext = os.path.dirname(path_before_ext)
                result_path = os.path.join(
                    os.path.dirname(relative_path), result_path + path_ext
                )
                return result_path
    else:
        (path_before_ext, path_ext) = os.path.splitext(relative_path)
        #print('path: {}, mappings: {}'.format(relative_path, dirs_info['path_mappings']))
        for pair in dirs_info['path_mappings']:
            (src_before_ext, _) = os.path.splitext(pair['src_path'])
            if src_before_ext == path_before_ext:
                return os.path.splitext(pair['dest_path'])[0] + path_ext
    return relative_path

def create_file_from_template(
    args, relative_path, requested_targets, dirs_info, replace_filename = None
):
    if is_file_must_be_ignored(relative_path, dirs_info):
        return

    src_path = os.path.abspath(os.path.join(
        ThisFileDirPath, args.template, relative_path
    ))
    #print('src_path: {}'.format(src_path))
    src_content = Path(src_path).read_text()
    dest_path = os.path.abspath(os.path.join(
        DestDirPath, replace_to_dest_if_src_exists(dirs_info, relative_path)
    ))
    #print('dest_path: "{}", dirs_info: "{}"\n'.format(dest_path, dirs_info))
    #print('relative_path: {}, src_path: {}, dest_path: {}\n'.format(relative_path, src_path, dest_path))
    if replace_filename:
        dest_path = os.path.join(
            os.path.dirname(dest_path),
            replace_filename + os.path.splitext(dest_path)[1]
        )

    _, extension = os.path.splitext(src_path)
    extensions_for_c = ['.c', '.h']
    if extension in extensions_for_c:
        comment_str = '//'
    else:
        comment_str = '#'

    dbg_show = False
    #if src_path.endswith('DefaultApplication.c'):
    #    dbg_show = True

    dest_content = process_file_content(
        args, src_content, comment_str, requested_targets, dbg_show
    )
    Path(os.path.dirname(dest_path)).mkdir(parents = True, exist_ok = True)
    dest_content = Path(dest_path).write_text(dest_content)

def create_project(args, template_dir_path):
    template_abs_dir_path = os.path.join(ThisFileDirPath, template_dir_path)
    #print('template_dir: {}'.format(template_abs_dir_path))
    dsc_src_pattern = os.path.join(template_abs_dir_path, "*.dsc")
    dsc_src_all_paths = glob.glob(dsc_src_pattern)
    # No true need for building in edk2, but simplifies templates
    if 1 != len(dsc_src_all_paths):
        raise LookupError(
            'A single `.dsc` file required, found: ' + dsc_src_all_paths
        )
    dsc_src_path = dsc_src_all_paths[0]
    dsc_relative_path = os.path.relpath(
        dsc_src_path,
        template_abs_dir_path
    )

    requested_targets = get_requested_targets(args)

    dsc_content = Path(dsc_src_path).read_text()
    dirs_info = get_dirs_info_from_dsc(
        args, dsc_content, requested_targets#, dbg_show=True
    )
    #import json
    #print('dirs_info: {}'.format(json.dumps(dirs_info, indent=4)))
    #print('dirs_info: {}'.format(dirs_info))
    # dsc
    create_file_from_template(
        args,
        dsc_relative_path,
        requested_targets,
        dirs_info,
        replace_filename=args.ProjectName
    )
    # dec
    create_file_from_template(
        args,
        os.path.splitext(dsc_relative_path)[0] + '.dec',
        requested_targets,
        dirs_info,
        replace_filename=args.ProjectName
    )

    for root, _, files in os.walk(template_abs_dir_path):
        if root in dirs_info['excluded_dirs']:
            continue
        #print('files: {}'.format(files))
        #print('root: {}'.format(root))
        for file_relative_path in files:
            if any(
                [file_relative_path.endswith(suf) for suf in ['.dsc', 'dec']]
            ):
                continue
            file_relative_path = os.path.relpath(
                os.path.join(root, file_relative_path), template_abs_dir_path
            )
            #file_relative_path = os.path.abspath(os.path.join(
            #    args.prefix, args.ProjectName, file_relative_path
            #))
            #print('relative path: ' + file_relative_path)
            create_file_from_template(
                args, file_relative_path, requested_targets, dirs_info
            )
            #print('\n')

def parse_args (argv):
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description =
"""
Generate EDK2 project from a template.
Template is a tree of text files, that support:
- <TAG> where TAG is one of {}
- {} and {} where TAG_BLOCK is one of {}
""".format(
        str([t['tag'] for t in single_tag_list]),
        get_tag_block_begin('TAG_BLOCK'),
        get_tag_block_end(),
        str(tag_block_list)
    ))
    parser.add_argument(
        'ProjectName', type=str,
        help="a base project name"
    )
    # unimplemented
    #parser.add_argument(
    #    '--edk2-root', nargs=1, type=str, default='./',
    #    help ="set the EDK2 root path"
    #)
    parser.add_argument(
        '--prefix', nargs='?', type=str, default='',
        help ="store the project in subdirectory, set prefix"
    )
    parser.add_argument(
        '-a', '--app', nargs='?', type=str,
        default=NotPassed, const=FlagOnly,
        help="add UEFI app"
    )
    parser.add_argument(
        '-ca', '--capp', nargs='?', type=str,
        default=NotPassed, const=FlagOnly,
        help="add C app"
    )
    parser.add_argument(
        '-l', '--lib', nargs='?', type=str,
        default=NotPassed, const=FlagOnly,
        help="add UEFI library"
    )
    # untested & requires some control that it is not linked with driver
    #parser.add_argument(
    #    '-cl', '--clib', nargs='?', type=str,
    #    default=NotPassed, const=FlagOnly,
    #    help="add C library"
    #)
    parser.add_argument(
        '-d', '--driver', nargs='?', type=str,
        default=NotPassed, const=FlagOnly,
        help="add UEFI driver"
    )
    parser.add_argument(
        '-v', '--verbose', action='store_true',
        help="include non-special comments from templates"
    )
    parser.add_argument(
        '-t', '--template', nargs=1, type=str, default='DefaultProject',
        help="specify directory with template project, relative to this script"
    )
    #parser.add_argument(
    #    '-h', '--help', action='help', # TODO: use 'help' also
    #    help="print the help message"
    #)
    args = parser.parse_args(argv[1:])

    test_path = os.path.isdir(os.path.join(ThisFileDirPath, args.template))
    if not test_path:
        raise LookupError(
            "Directory for with template EDK2 project '{}' not found".format(
                test_path
            )
        )

    if args.ProjectName[:3].lower == 'lib' and args.app is not NotPassed:
        args.app = args.ProjectName[3:]

    if not args.prefix.endswith(os.sep):
        args.prefix += os.sep

    global DestDirPath
    DestDirPath = os.path.abspath(os.path.join(args.prefix, args.ProjectName))
    #print(args)
    return args

def main (argv=None):
    if argv is None:
        argv = sys.argv
    args = parse_args(argv)
    create_project(args, args.template)
    return 0

if __name__ == '__main__':
    sys.exit(main())
