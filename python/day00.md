# Day 1：环境与工具链迁移（TS `pnpm` ➡️ Python `Poetry`）

## 目标
*   **🎯 今日目标**：搭建开箱即用的现代化 Python 开发环境，拒绝全局安装。
*   **💡 核心映射**：
    *   **环境管理**：`nvm` ➡️ `pyenv`（切换 Python 版本）。
    *   **依赖与虚拟环境**：Python 没有本地 `node_modules`，全局 `pip install` 会污染系统环境。使用 **Poetry** 统一管理依赖和虚拟环境，它会像 `pnpm` 一样生成 `poetry.lock` 锁文件。
    *   **编辑器**：VS Code 安装 **Python** + **Pylance** (相当于 TS 语言服务) + **Ruff** (集成了 ESLint 和 Prettier 的极速 Linter/Formatter)。
*   **⚠️ 避坑指南**：绝对不要在没有开启虚拟环境（Virtual Environment）的情况下开始写 Python 代码，保持开发环境的纯净。
*   **📚 学习资料**：
    *   [Poetry 官方文档：Basic Usage](https://python-poetry.org/docs/basic-usage/)
    *   [VS Code Pylance 静态类型检查设置](https://code.visualstudio.com/docs/python/editing)

## 已完成👸
### ✅安装`pyenv`
```
# 安装
brew install pyenv
# 依次 运行下面命令配置环境
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.zshrc
echo '[[ -d $PYENV_ROOT/bin ]] && export PATH="$PATH:$PYENV_ROOT/bin"' >> ~/.zshrc
echo 'eval "$(pyenv init -)"' >> ~/.zshrc

# 让配置生效
source ~/.zshrc
```

### 使用方法
```
# 使用 pyenv 安装 Python
pyenv install 3.11
```
### 安装  poetry
```
brew install poetry
# 配置让虚拟环境建在项目内，以后在任何项目里初始化 Poetry，都会直接在你的项目根目录下创建一个 .venv 文件夹。
poetry config virtualenvs.in-project true
```

### ✅理解为什么要在虚拟环境开发，怎么进入虚拟环境

#### 1. 首次如何通过命令行创建和进入虚拟环境？

确保你的终端（Terminal / PowerShell / CMD）已经打开，并切换到了你的项目目录下（使用 `cd 你的项目路径`）。

* 第一步：创建虚拟环境

Python 自带了 `venv` 模块，可以直接用来创建虚拟环境。在终端中运行以下命令：
> **注：** 最后的 `.venv` 是你给虚拟环境文件夹取的名字，通常大家都习惯用 `.venv` 或 `env`。执行后，你会发现项目目录下多了一个叫 `.venv` 的文件夹。里面包含了 Python 解释器的副本以及你安装的所有第三方库的源代码和编译文件。绝对不要提交到git。

* **Mac / Linux:**
```bash
python3 -m venv .venv

```


* 第二步：激活（进入）虚拟环境

创建好后，你必须“激活”它，接下来的安装和运行才会与全局隔离。
* **Mac / Linux:**
```bash
source .venv/bin/activate

```

> **退出方法：** 在终端随时输入 `deactivate` 即可退出当前虚拟环境。

---

#### 2. 实际开发中为什么要使用不同的虚拟环境？

如果不使用虚拟环境，所有的第三方包（如 Django, Pandas）都会被安装在系统的全局 Python 环境中。这会带来三大灾难：

*  避免“版本冲突”的噩梦（最核心原因）

* 保持环境纯净，方便“一键打包”，别人使用的时候能够一件复制

* 权限与安全隐患。

在 Mac/Linux 系统上，往全局环境安装包常常需要 `sudo` 权限。误用最高权限修改系统自带的 Python 环境，极有可能导致操作系统本身的一些工具直接瘫痪（因为很多系统组件依赖特定版本的 Python）。

---

## 3. 什么时候应该使用不同的虚拟环境？

一句话原则：**“一个项目，一个环境。”**

### ✅vscode插件**Python** + **Pylance**+ **Ruff** 

#### 配置

为了让这三个插件完美配合，最好的方式是直接修改 VS Code 的配置文件。

**操作步骤：**

1. 按下 `Ctrl + Shift + P`（Mac 上是 `Cmd + Shift + P`）打开命令面板。
2. 输入 `Open Settings (JSON)`，选择“首选项: 打开用户设置 (JSON)”。
3. 在打开的 `settings.json` 文件中，加入以下配置（如果已有同名配置项，直接修改值即可）：

```json
{
    // === Python 基础设置 ===
    "python.languageServer": "Pylance", 

    // === Pylance 设置 ===
    // 可选值: "off", "basic", "strict"。"basic" 适合大多数日常开发，能检查出大部分基础错误。
    "python.analysis.typeCheckingMode": "basic", 
    // 开启内联提示（非常有用的功能，会在代码里暗色显示推断出的变量类型）
    "python.analysis.inlayHints.variableTypes.enabled": true,
    "python.analysis.inlayHints.functionReturnTypes.enabled": true,

    // === 针对 Python 文件的专用设置 (Ruff) ===
    "[python]": {
        // 将 Ruff 设置为默认的代码格式化工具
        "editor.defaultFormatter": "charliermarsh.ruff",
        // 开启保存时自动格式化
        "editor.formatOnSave": true,
        // 保存时自动执行的操作
        "editor.codeActionsOnSave": {
            // 保存时自动修复 Ruff 能自动修复的 linting 错误
            "source.fixAll": "explicit",
            // 保存时自动整理并排序 import 语句，移除未使用的引入
            "source.organizeImports": "explicit"
        }
    }
}

```

---

#### 使用

配置完成后，这三个插件基本上是“无感且自动化”工作的，不需要你频繁地去手动点击它们：

* **Python 插件（基座）：**
* **核心用法：选择解释器。** 按 `Ctrl + Shift + P`（或 `Cmd + Shift + P`），输入 `Python: Select Interpreter`。在这里选择你项目使用的 Python 环境（比如系统环境、Conda 虚拟环境或 `.venv`）。选对了解释器，另外两个插件才能正确工作。
* 它还在代码编辑器右上角提供了一个“播放”按钮，可以直接点击运行当前 Python 文件。


* **Pylance（大脑）：**
* **核心用法：享受智能提示。** 当你敲代码时，它会极速提供自动补全。


* **Ruff（清洁工）：**
* **核心用法：按 `Ctrl + S`（或 `Cmd + S`）保存文件。** Ruff 会在毫秒级的时间内瞬间把你的代码格式化


