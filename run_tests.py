#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
unluac 测试脚本
用法: python run_tests.py <luac路径>
示例: python run_tests.py D:\code\lua-5.4.7\lua-5.4.7\src\luac.exe
"""

import sys
import os
import subprocess
import tempfile
from pathlib import Path

# 配置
UNLUAC_JAR = Path(__file__).parent / "unluac.jar"
TEST_DIR = Path(__file__).parent / "test" / "src"

def run_test(luac_path: Path, lua_file: Path, out_dir: Path) -> tuple[bool, str]:
    """
    运行单个测试
    返回: (是否成功, 错误信息)
    """
    basename = lua_file.stem
    luac_file = out_dir / f"{basename}.luac"
    
    # 1. 用 luac 编译
    try:
        result = subprocess.run(
            [str(luac_path), "-o", str(luac_file), str(lua_file)],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode != 0:
            return None, f"编译失败: {result.stderr}"
    except subprocess.TimeoutExpired:
        return None, "编译超时"
    except Exception as e:
        return None, f"编译异常: {e}"
    
    # 2. 用 unluac 反编译
    try:
        result = subprocess.run(
            ["java", "-jar", str(UNLUAC_JAR), str(luac_file)],
            capture_output=True,
            text=True,
            timeout=60
        )
        if result.returncode != 0:
            error_msg = result.stderr.strip()
            # 提取关键错误信息
            if "IllegalStateException" in error_msg:
                lines = error_msg.split('\n')
                for line in lines:
                    if "given:" in line or "expected:" in line:
                        return False, line.strip()
                return False, "IllegalStateException"
            return False, error_msg[:100] if error_msg else "未知错误"
        return True, ""
    except subprocess.TimeoutExpired:
        return False, "反编译超时"
    except Exception as e:
        return False, f"反编译异常: {e}"


def main():
    if len(sys.argv) < 2:
        print("用法: python run_tests.py <luac路径>")
        print("示例: python run_tests.py D:\\code\\lua-5.4.7\\lua-5.4.7\\src\\luac.exe")
        sys.exit(1)
    
    luac_path = Path(sys.argv[1])
    
    # 验证路径
    if not luac_path.exists():
        print(f"错误: luac 路径不存在: {luac_path}")
        sys.exit(1)
    
    if not UNLUAC_JAR.exists():
        print(f"错误: unluac.jar 不存在: {UNLUAC_JAR}")
        sys.exit(1)
    
    if not TEST_DIR.exists():
        print(f"错误: 测试目录不存在: {TEST_DIR}")
        sys.exit(1)
    
    # 获取 luac 版本
    try:
        result = subprocess.run([str(luac_path), "-v"], capture_output=True, text=True, timeout=5)
        luac_version = result.stdout.strip() or result.stderr.strip() or "未知版本"
    except:
        luac_version = "未知版本"
    
    print("=" * 60)
    print(f"unluac 测试")
    print("=" * 60)
    print(f"luac 路径: {luac_path}")
    print(f"luac 版本: {luac_version}")
    print(f"unluac: {UNLUAC_JAR}")
    print(f"测试目录: {TEST_DIR}")
    print("=" * 60)
    print()
    
    # 收集测试文件
    lua_files = sorted(TEST_DIR.glob("*.lua"))
    if not lua_files:
        print("错误: 没有找到测试文件")
        sys.exit(1)
    
    print(f"找到 {len(lua_files)} 个测试文件")
    print("-" * 60)
    
    # 创建输出目录
    out_dir = Path(__file__).parent / "test" / "out"
    out_dir.mkdir(parents=True, exist_ok=True)
    
    # 运行测试
    passed = 0
    failed = 0
    skipped = 0
    failed_tests = []
    
    for i, lua_file in enumerate(lua_files, 1):
        name = lua_file.stem
        result, error = run_test(luac_path, lua_file, out_dir)
        
        if result is None:
            # 编译跳过
            print(f"[{i:3d}/{len(lua_files)}] [SKIP] {name}")
            skipped += 1
        elif result:
            print(f"[{i:3d}/{len(lua_files)}] [ OK ] {name}")
            passed += 1
        else:
            print(f"[{i:3d}/{len(lua_files)}] [FAIL] {name} - {error}")
            failed += 1
            failed_tests.append((name, error))
    
    # 打印结果
    print()
    print("=" * 60)
    print("测试结果")
    print("=" * 60)
    print(f"通过: {passed}")
    print(f"失败: {failed}")
    print(f"跳过: {skipped}")
    print(f"总计: {len(lua_files)}")
    print("=" * 60)
    
    if failed_tests:
        print()
        print("失败的测试:")
        print("-" * 60)
        for name, error in failed_tests:
            print(f"  {name}: {error}")
    
    # 返回码
    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    main()
