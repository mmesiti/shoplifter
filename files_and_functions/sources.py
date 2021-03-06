#!/usr/bin/env python3
import re
from multiline_comments import next_comment_state


def is_preprocessor_line(line):
    directive_patterns = [
        r"#\s*if", r"#\s*ifdef", r"#\s*ifndef", r"#\s*else", r"#\s*endif",
        r"#\s*define", r"#\s*include"
    ]
    return any(re.search(dp, line) for dp in directive_patterns)


def level_after_line(level, line):
    return level + line.count('{') - line.count('}')


def line_start_unused_function_definition(i, line, unused_functions):
    line = line[:line.find('//')] if '//' in line else line
    for funcname in unused_functions:
        match = re.search(r"(^|\W)" + funcname + "(\W|$)", line)
        if match:
            return True

    return False


def remove_unused_functions_from_lines(unused_functions,
                                       lines,
                                       represent_line=lambda i, line: line,
                                       *args,
                                       **kwargs):
    new_lines = []
    include_line = True
    level = 0
    in_unused_function_header = False
    in_multiline_comment = False
    for i, line in enumerate(lines):
        in_multiline_comment = next_comment_state(line, in_multiline_comment)
        if is_preprocessor_line(line):
            new_lines.append(represent_line(i, line, *args, **kwargs))
        elif level > 0:
            if include_line:
                new_lines.append(represent_line(i, line, *args, **kwargs))
            else:
                pass
                # new_lines.append(f'//{i}\n')
            level = level_after_line(level, line)
            if level == 0:
                include_line = True
        elif level == 0:
            if (not in_multiline_comment
                    and line_start_unused_function_definition(
                        i, line, unused_functions)):
                include_line = False
                in_unused_function_header = True
            elif not in_unused_function_header:
                include_line = True
            if in_unused_function_header and ';' in line:
                in_unused_function_header = False
            if include_line:
                new_lines.append(represent_line(i, line, *args, **kwargs))
            else:
                pass
                # new_lines.append(f'//{i}\n')
            level = level_after_line(level, line)
            if level > 0:
                in_unused_function_header = False

    return new_lines


def remove_print_compiling_info(lines):
    def _filter(line):
        return not (re.search("(\W|^)print_compiling_info(\W|$)", line) or
                    re.search("(\W|^)print_compiling_info_short(\W|$)", line))

    return [line for line in lines if _filter(line)]
