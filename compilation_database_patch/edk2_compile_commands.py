import glob
import os
import json

def update_compile_commands_file(TargetDict, AutoGenObject, Macros):
    # process only compilation, not linkage or whatever else
    if not TargetDict['cmd'].startswith('"$(CC)"'):
        return

    # Need to fild compiler and his flags for this project
    cc = ''
    cc_flags = ''
    for p in glob.glob(os.path.join(Macros['BIN_DIR'], 'TOOLS_DEF.*')):
        try:
            content = open(p, 'r').read()
            done = {'CC': False, 'CC_FLAGS': False}
            for line in content.splitlines():
                if line.startswith('CC_FLAGS = '):
                    done['CC_FLAGS'] = True
                    cc_flags = line[len('CC_FLAGS = '):]
                    if all(v == True for v in done.values()):
                        break
                elif line.startswith('CC = '):
                    done['CC'] = True
                    cc = line[len('CC = '):]
                    if all(v == True for v in done.values()):
                        break
            if all(v == True for v in done.values()):
                break
        except:
            continue
    if not cc or not cc_flags:
        print ('Error: cc or cc_flags is not defined!')
        return

    project_path    = AutoGenObject.Macros['PLATFORM_DIR']
    directory_field = Macros['BIN_DIR']
    command_field   = TargetDict['cmd'].replace('$(CC)', cc, 1).replace(
                          '$(CC_FLAGS)', cc_flags, 1
                      ).replace(
                          '$(INC)', '-I' + ' -I'.join(
                              AutoGenObject.IncludePathList
                          ), 1
                      )
    file_field      = TargetDict['cmd'].split()[-1]

    return common_update_compile_commands_file(
        project_path, directory_field, command_field, file_field
    )

# spec.url: https://clang.llvm.org/docs/JSONCompilationDatabase.html
# project_path    - path to compile_commands.json, path to project root
# directory_field - "directory" from spec., not really used here, because nearly all paths are absolute
# command_field   - "command" from spec.
# file_field      - "file" from spec.
def common_update_compile_commands_file (
    project_path, directory_field, command_field, file_field
):
    result_path = os.path.join(project_path, 'compile_commands.json')
    content = []
    try:
        f = open(result_path, 'r')
        candidate_content_raw = f.read()
        f.close()
        candidate_content = json.loads(candidate_content_raw)
        content = candidate_content
    except IOError:
        print ('Can\'t read {}, creating new..'.format(result_path))
    except ValueError:
        # ValueError is inherited by json.decoder.JSONDecodeError
        print ('Error at parsing {}, creating new..'.format(result_path))
    except:
        print ('Unexpected error')
        raise

    obj = {
        'directory': directory_field,
        'command':   command_field,
        'file':      file_field
    }
    try:
        i = next(i for i,entry in enumerate(content) if entry['file'] == file_field)
        content[i] = obj
    except StopIteration:
        content.append(obj)

    f = open(result_path, 'w')
    # Save to file
    json.dump(content, f, indent=2)
    f.close()
