#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试中文编码问题
"""

import sys
import locale

print("=== 系统编码信息 ===")
print(f"Python版本: {sys.version}")
print(f"默认编码: {sys.getdefaultencoding()}")
print(f"文件系统编码: {sys.getfilesystemencoding()}")
print(f"标准输入编码: {sys.stdin.encoding}")
print(f"标准输出编码: {sys.stdout.encoding}")
print(f"标准错误编码: {sys.stderr.encoding}")
print(f"区域设置: {locale.getdefaultlocale()}")

print("\n=== 测试中文输出 ===")
print("测试中文输出 - 直接输出")
print("测试中文输出 - encoded".encode('utf-8').decode('utf-8'))

# 测试不同编码
test_str = "测试中文输出"
print(f"\n原始字符串: {test_str}")
print(f"UTF-8编码: {test_str.encode('utf-8')}")
print(f"GB2312编码: {test_str.encode('gb2312')}")

print("\n=== 解决方案测试 ===")
# 方案1: 强制设置标准输出编码
if sys.stdout.encoding != 'utf-8':
    print(f"警告: 标准输出编码不是UTF-8，当前是: {sys.stdout.encoding}")
    # 尝试重新打开stdout为UTF-8
    try:
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        print("已重新打开stdout为UTF-8编码")
        print("重新测试中文: 测试中文输出")
    except Exception as e:
        print(f"重新打开stdout失败: {e}")