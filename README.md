# Requirements Generator

一个智能的Python项目依赖生成工具，可以自动分析项目代码并生成完整的`requirements.txt`文件。

## 功能特点

- 自动扫描项目代码，识别直接依赖
- 分析依赖关系树，识别必要的子依赖
- 自动获取并记录依赖包的版本信息
- 生成格式化的`requirements.txt`文件
- 支持Windows和类Unix系统

## 安装

1. 克隆此仓库：
```bash
git clone https://github.com/sup798/requirements-generator.git
cd requirements-generator
```

2. 安装依赖：
```bash
pip install pipreqs pipdeptree
```

## 使用方法

### 基本用法

```bash
python requirements_generator.py --path /path/to/your/project
```

### 最佳实践

为了获得最准确的依赖分析结果，建议将`requirements_generator.py`放在项目根目录下运行。这样可以确保工具能够正确扫描整个项目结构，不会遗漏任何依赖。

```bash
# 将工具复制到项目根目录
cp requirements_generator.py /path/to/your/project/
cd /path/to/your/project/

# 在项目根目录下运行
python requirements_generator.py
```

### 命令行参数

- `--path`: 指定项目路径（默认为当前目录）
- `--output`: 指定输出文件路径（默认为`requirements.txt`）
- `--no-subdeps`: 不包含子依赖，仅生成直接依赖

### 示例

生成包含所有依赖的requirements.txt：
```bash
python requirements_generator.py --path ./my_project
```

仅生成直接依赖：
```bash
python requirements_generator.py --path ./my_project --no-subdeps
```

指定输出文件：
```bash
python requirements_generator.py --path ./my_project --output custom_requirements.txt
```

## 工作原理

1. 使用`pipreqs`扫描项目代码，识别直接依赖
2. 使用`pipdeptree`分析依赖关系树
3. 获取所有依赖包的版本信息
4. 生成格式化的`requirements.txt`文件

## 依赖项

- Python 3.6+
- pipreqs
- pipdeptree

## 注意事项

- 工具需要访问网络以获取包版本信息
- 某些本地包可能无法正确识别版本
- 建议在虚拟环境中使用此工具
- 为了获得最佳结果，请在项目根目录下运行此工具

## 贡献

欢迎提交问题和拉取请求！

## 许可证

MIT
