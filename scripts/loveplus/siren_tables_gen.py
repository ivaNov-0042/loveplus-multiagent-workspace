#!/usr/bin/env python3
"""从 FFmpeg 的 libavcodec/siren.c 提取 G.722.1(Siren14 同族) 解码常量表，生成 siren_tables.py。

只做机械提取（不引入任何人工数值），保证与参考实现逐值一致。
用法: ./.venv/bin/python scripts/loveplus/siren_tables_gen.py [siren.c 路径] [输出路径]
"""
import os
import re
import sys

DEFAULT_SRC = '/tmp/ffsrc/ffmpeg-6.1.1/libavcodec/siren.c'
DEFAULT_OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'siren_tables.py')

WANT = [
    ('uint8_t', 'index_table'),
    ('uint8_t', 'vector_dimension'),
    ('uint8_t', 'number_of_vectors'),
    ('uint8_t', 'expected_bits_table'),
    ('int8_t', 'differential_decoder_tree'),
    ('uint16_t', 'decoder_tree0'),
    ('uint16_t', 'decoder_tree1'),
    ('uint16_t', 'decoder_tree2'),
    ('uint16_t', 'decoder_tree3'),
    ('uint16_t', 'decoder_tree4'),
    ('uint16_t', 'decoder_tree5'),
    ('uint16_t', 'decoder_tree6'),
    ('float', 'mlt_quant'),
    ('float', 'noise_category5'),
    ('float', 'noise_category6'),
]


def strip_comments(s):
    s = re.sub(r'/\*.*?\*/', ' ', s, flags=re.S)
    s = re.sub(r'//[^\n]*', ' ', s)
    return s


def grab(src, name):
    """抓 `... name[..][..] = { ... };` 的初始化列表并解析成嵌套 list。"""
    m = re.search(r'\b' + name + r'\s*(\[[^=]*?)?\s*=\s*\{', src)
    if not m:
        raise SystemExit('table not found: ' + name)
    i = m.end() - 1  # 指向 '{'
    depth = 0
    for j in range(i, len(src)):
        if src[j] == '{':
            depth += 1
        elif src[j] == '}':
            depth -= 1
            if depth == 0:
                body = src[i:j + 1]
                break
    else:
        raise SystemExit('unterminated: ' + name)
    # 把数值 token 换成 python 字面量：去掉多余括号/逗号，保留嵌套结构
    body = body.replace('{', '[').replace('}', ']')
    body = re.sub(r'([0-9.]+)f\b', r'\1', body)      # 1.5f -> 1.5
    body = re.sub(r'/\*\s*(-?[0-9]+)\s*\*/', r'\1,', body)  # /* -3 */ 0 -> -3, 0
    body = re.sub(r',\s*]', ']', body)
    body = body.replace('[', '[').replace(']', ']')
    return eval(body, {'__builtins__': {}}, {})


def fmt(v, indent=1):
    if isinstance(v, list):
        if all(not isinstance(x, list) for x in v):
            one = '[' + ', '.join(repr(x) for x in v) + ']'
            if len(one) <= 96:
                return one
            pad = '    ' * indent
            lines, cur = [], pad + '    '
            for x in v:
                t = repr(x) + ', '
                if len(cur) + len(t) > 96:
                    lines.append(cur.rstrip())
                    cur = pad + '    '
                cur += t
            lines.append(cur.rstrip().rstrip(','))
            return '[\n' + '\n'.join(lines) + '\n' + pad + ']'
        return '[\n' + '\n'.join('    ' * indent + fmt(x, indent + 1) + ',' for x in v) + '\n' + '    ' * (indent - 1) + ']'
    return repr(v)


def main():
    src_path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_SRC
    out_path = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_OUT
    src = strip_comments(open(src_path).read())
    out = ['"""G.722.1 / Siren14 解码常量表（由 siren_tables_gen.py 从 FFmpeg libavcodec/siren.c 机械提取）。',
           '',
           '来源: FFmpeg 6.1.1 (LGPL) libavcodec/siren.c —— 与 ITU-T G.722.1 参考实现同源。',
           '请勿手工修改本文件；如需更新请重跑 scripts/loveplus/siren_tables_gen.py。',
           '"""',
           '']
    got = {}
    for typ, name in WANT:
        val = grab(src, name)
        got[name] = val
        out.append('%s = %s' % (name.upper(), fmt(val)))
        out.append('')
    out.append('DECODER_TREES = [DECODER_TREE0, DECODER_TREE1, DECODER_TREE2, DECODER_TREE3,')
    out.append('                 DECODER_TREE4, DECODER_TREE5, DECODER_TREE6]')
    out.append('')
    out.append('# 对应 FFmpeg 的 decoder_tables_elements[] = sizeof(tree)/sizeof(tree[0])')
    out.append('DECODER_TABLES_ELEMENTS = [len(t) for t in DECODER_TREES]')
    out.append('')
    open(out_path, 'w').write('\n'.join(out))
    print('[ok] %d tables -> %s' % (len(got), out_path))
    for name, val in got.items():
        shape = []
        v = val
        while isinstance(v, list):
            shape.append(len(v))
            v = v[0]
        print('   %-28s %s' % (name, 'x'.join(map(str, shape))))


if __name__ == '__main__':
    main()
