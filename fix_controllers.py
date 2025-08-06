#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量修复控制器注解
将Springfox注解替换为OpenAPI注解
"""

import os
import re

def fix_controller_file(file_path):
    """修复单个控制器文件"""
    print(f"修复文件: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 替换导入语句
    content = re.sub(r'import io\.swagger\.annotations\.Api;', 'import io.swagger.v3.oas.annotations.tags.Tag;', content)
    content = re.sub(r'import io\.swagger\.annotations\.ApiOperation;', 'import io.swagger.v3.oas.annotations.Operation;', content)
    content = re.sub(r'import io\.swagger\.annotations\.ApiParam;', 'import io.swagger.v3.oas.annotations.Parameter;', content)
    
    # 替换注解
    content = re.sub(r'@Api\(tags = "([^"]+)", description = "([^"]+)"\)', r'@Tag(name = "\1", description = "\2")', content)
    content = re.sub(r'@ApiOperation\(value = "([^"]+)", notes = "([^"]+)"\)', r'@Operation(summary = "\1", description = "\2")', content)
    content = re.sub(r'@ApiParam\(value = "([^"]+)", required = true\)', r'@Parameter(description = "\1", required = true)', content)
    content = re.sub(r'@ApiParam\(value = "([^"]+)", required = true, example = "([^"]+)"\)', r'@Parameter(description = "\1", required = true, example = "\2")', content)
    content = re.sub(r'@ApiParam\(value = "([^"]+)", example = "([^"]+)"\)', r'@Parameter(description = "\1", example = "\2")', content)
    content = re.sub(r'@ApiParam\(value = "([^"]+)"\)', r'@Parameter(description = "\1")', content)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ 修复完成: {file_path}")

def main():
    """主函数"""
    print("🔧 批量修复控制器注解")
    print("=" * 40)
    
    # 控制器文件列表
    controllers = [
        'src/main/java/com/knowledge/controller/ChatController.java',
        'src/main/java/com/knowledge/controller/SearchController.java',
        'src/main/java/com/knowledge/controller/CategoryController.java'
    ]
    
    for controller in controllers:
        if os.path.exists(controller):
            fix_controller_file(controller)
        else:
            print(f"❌ 文件不存在: {controller}")
    
    print("\n✅ 所有控制器修复完成")

if __name__ == "__main__":
    main() 