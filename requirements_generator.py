#!/usr/bin/env python
import subprocess
import os
import sys
import tempfile
import json
from typing import Dict, Set, List, Tuple

def get_project_dependencies(project_path: str) -> Dict[str, str]:
    """使用pipreqs获取项目直接依赖"""
    with tempfile.NamedTemporaryFile(mode='w+', suffix='.txt', delete=False) as temp_file:
        temp_path = temp_file.name
    
    try:
        # 在Windows上使用python -m pipreqs.pipreqs
        pipreqs_cmd = [sys.executable, '-m', 'pipreqs.pipreqs']
        result = subprocess.run(pipreqs_cmd + [project_path, '--force', '--savepath', temp_path], 
                      check=True, capture_output=True, text=True)
        
        if result.stderr:
            print("pipreqs 输出:", result.stderr)
        
        with open(temp_path, 'r') as f:
            requirements = [line.strip() for line in f if line.strip()]
        
        # 解析依赖和版本
        deps = {}
        for req in requirements:
            if '==' in req:
                name, version = req.split('==')
                deps[name.lower()] = version
            else:
                deps[req.lower()] = None
        
        return deps
    except subprocess.CalledProcessError as e:
        print(f"警告: pipreqs 执行失败: {e.stderr.decode() if e.stderr else str(e)}")
        return {}
    finally:
        try:
            os.unlink(temp_path)
        except:
            pass

def get_package_version(package_name: str) -> str:
    """使用pip show获取包的版本信息"""
    try:
        result = subprocess.run([sys.executable, '-m', 'pip', 'show', package_name],
                              check=True, capture_output=True, text=True)
        for line in result.stdout.splitlines():
            if line.startswith('Version: '):
                return line.split('Version: ')[1].strip()
    except subprocess.CalledProcessError:
        pass
    return ''

def get_dependency_tree() -> Tuple[Dict[str, str], Dict[str, Set[str]]]:
    """使用pipdeptree获取依赖树
    返回: (包名->版本映射, 包名->子依赖集合映射)
    """
    try:
        # 获取JSON格式的依赖树
        json_cmd = [sys.executable, '-m', 'pipdeptree', '--json-tree']
        json_result = subprocess.run(json_cmd, check=True, capture_output=True, text=True)
        tree = json.loads(json_result.stdout)
        
        # 获取版本信息
        freeze_cmd = [sys.executable, '-m', 'pipdeptree', '--freeze']
        freeze_result = subprocess.run(freeze_cmd, check=True, capture_output=True, text=True)
        
        # 解析版本信息
        versions = {}
        for line in freeze_result.stdout.splitlines():
            if '==' in line:
                name, version = line.split('==')
                if not ('/' in version or '\\' in version):  # 过滤本地路径
                    versions[name.strip().lower()] = version.strip()
        
        # 构建依赖关系图
        deps_graph = {}
        
        def process_dependencies(pkg_info):
            pkg_name = pkg_info.get('key', '').lower()
            if not pkg_name:
                return
            
            deps_graph[pkg_name] = set()
            for dep in pkg_info.get('dependencies', []):
                dep_name = dep.get('key', '').lower()
                if dep_name:
                    deps_graph[pkg_name].add(dep_name)
                    # 递归处理子依赖
                    process_dependencies(dep)
        
        # 处理依赖树
        for package in tree:
            process_dependencies(package)
        
        return versions, deps_graph
    except subprocess.CalledProcessError as e:
        print(f"警告: pipdeptree 执行失败: {e.stderr.decode() if e.stderr else str(e)}")
        return {}, {}
    except json.JSONDecodeError:
        print("警告: 无法解析pipdeptree输出")
        return {}, {}
    except Exception as e:
        print(f"警告: 处理依赖时出错: {str(e)}")
        return {}, {}

def get_required_dependencies(direct_deps: Dict[str, str], deps_graph: Dict[str, Set[str]]) -> Set[str]:
    """获取所有必需的依赖（包括子依赖）"""
    required = set()
    to_process = set(direct_deps.keys())
    
    while to_process:
        dep = to_process.pop()
        if dep not in required:
            required.add(dep)
            # 添加子依赖到处理队列
            if dep in deps_graph:
                to_process.update(deps_graph[dep] - required)
    
    return required

def generate_requirements(project_path: str, output_file: str = 'requirements.txt', include_subdeps: bool = True):
    """生成项目依赖文件"""
    print("正在扫描项目直接依赖...")
    direct_deps = get_project_dependencies(project_path)
    
    if not direct_deps:
        print("错误: 未能找到任何项目依赖")
        return
    
    print(f"\n找到 {len(direct_deps)} 个直接依赖:")
    for dep in sorted(direct_deps.keys()):
        print(f"  - {dep}")
    
    print("\n正在获取依赖关系...")
    versions, deps_graph = get_dependency_tree()
    
    if not versions:
        print("错误: 未能获取依赖信息")
        return
    
    # 确定要包含的依赖
    if include_subdeps:
        print("正在分析依赖关系...")
        required_deps = get_required_dependencies(direct_deps, deps_graph)
        subdeps = required_deps - set(direct_deps.keys())
        print(f"项目直接依赖: {len(direct_deps)} 个")
        print(f"必要的子依赖: {len(subdeps)} 个")
    else:
        required_deps = set(direct_deps.keys())
        print("仅包含直接依赖")
    
    # 生成requirements.txt
    print("\n正在生成requirements.txt...")
    with open(output_file, 'w', encoding='utf-8') as f:
        # 首先写入直接依赖
        f.write("# 直接依赖\n")
        for dep in sorted(direct_deps.keys()):
            version = direct_deps[dep] or versions.get(dep, '')
            if not version:
                version = get_package_version(dep)
            if version:
                f.write(f"{dep}=={version}\n")
            else:
                print(f"警告: 未能找到 {dep} 的版本信息")
                f.write(f"{dep}\n")
        
        # 如果包含子依赖，则写入子依赖
        if include_subdeps and subdeps:
            f.write("\n# 子依赖\n")
            for dep in sorted(subdeps):
                version = versions.get(dep, '')
                if not version:
                    version = get_package_version(dep)
                if version:
                    f.write(f"{dep}=={version}\n")
                else:
                    print(f"警告: 未能找到 {dep} 的版本信息")
                    f.write(f"{dep}\n")
    
    print(f"\n依赖已保存到 {output_file}")

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='生成项目依赖文件')
    parser.add_argument('--path', default='.', help='项目路径')
    parser.add_argument('--output', default='requirements.txt', help='输出文件路径')
    parser.add_argument('--no-subdeps', action='store_true', help='不包含子依赖')
    
    args = parser.parse_args()
    generate_requirements(args.path, args.output, not args.no_subdeps) 