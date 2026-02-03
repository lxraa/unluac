#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
unluac 编译脚本
用法: python build.py
"""

import subprocess
import sys
from pathlib import Path

def main():
    # 项目根目录
    root_dir = Path(__file__).parent
    src_dir = root_dir / "src"
    build_dir = src_dir / "build"
    manifest_file = src_dir / "MANIFEST.MF"
    output_jar = root_dir / "unluac.jar"
    
    print("=" * 50)
    print("编译 unluac")
    print("=" * 50)
    
    # 1. 收集所有 Java 源文件
    print("\n[1/3] 收集源文件...")
    java_files = list(src_dir.rglob("*.java"))
    if not java_files:
        print("错误: 没有找到 Java 源文件")
        sys.exit(1)
    print(f"找到 {len(java_files)} 个 Java 文件")
    
    # 写入 sources.txt
    sources_file = src_dir / "sources.txt"
    with open(sources_file, "w") as f:
        for java_file in java_files:
            f.write(str(java_file) + "\n")
    
    # 2. 编译
    print("\n[2/3] 编译 Java 源文件...")
    build_dir.mkdir(exist_ok=True)
    
    result = subprocess.run(
        ["javac", "-d", str(build_dir), f"@{sources_file}"],
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        print("编译失败:")
        print(result.stderr)
        sys.exit(1)
    print("编译成功")
    
    # 3. 打包 JAR
    print("\n[3/3] 打包 JAR...")
    result = subprocess.run(
        ["jar", "cfm", str(output_jar), str(manifest_file), "-C", str(build_dir), "."],
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        print("打包失败:")
        print(result.stderr)
        sys.exit(1)
    
    print(f"打包成功: {output_jar}")
    print("\n" + "=" * 50)
    print("完成!")
    print("=" * 50)


if __name__ == "__main__":
    main()
