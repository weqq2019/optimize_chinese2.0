# Chinese Text Optimizer

一个基于 GPT-3.5 的中文文本优化工具，帮助用户改进中文表达，使其更加简洁、自然、流畅、优雅。

## 功能特点

- 🚀 快速优化：使用热键（F9 或 Ctrl+Alt+Space）即可优化选中文本
- 🎯 智能优化：基于 GPT-3.5 的智能文本优化
- 💡 简单易用：选中文本 -> 按热键 -> 自动替换
- 🔄 状态提示：托盘图标动态显示处理状态
- 📋 剪贴板增强：使用 win32clipboard 实现稳定的剪贴板操作
- 🛡️ 稳定可靠：多重错误处理和重试机制
- 📊 优化反馈：清晰的优化过程和结果展示
- 🌐 网络优化：支持直连和代理配置

## 优化效果展示

程序会以清晰的格式显示优化过程：
```
==================================================
📝 原始文本:
  您输入的文本
--------------------------------------------------
/* API 请求开始 */
处理中...
/* API 请求结束 */
--------------------------------------------------
✨ 优化结果:
  优化后的文本
==================================================
```

## 项目结构

```
chinese_optimizer/
├── config/                 # 配置模块
│   ├── __init__.py
│   └── settings.py        # 全局配置文件
├── core/                  # 核心功能模块
│   ├── __init__.py
│   ├── clipboard.py       # 剪贴板管理（win32clipboard）
│   ├── hotkey.py         # 热键管理
│   ├── optimizer.py      # 文本优化逻辑
│   ├── processor.py      # 文本处理流程
│   └── tray.py          # 托盘图标管理
├── utils/                # 工具模块
│   ├── __init__.py
│   └── logger.py        # 日志工具
├── __init__.py
└── main.py              # 主程序入口
```

## 模块说明

### 配置模块 (config/)

#### settings.py
- API 配置：OpenAI API 密钥和接口地址
- 日志配置：日志级别和格式
- 热键配置：可自定义的热键组合
- 托盘配置：图标大小和颜色设置
- 网络配置：代理设置选项

### 核心模块 (core/)

#### clipboard.py (剪贴板管理)
- `ClipboardManager` 类：使用 win32clipboard 实现稳定的剪贴板操作
  - 线程安全的剪贴板访问
  - 自动重试机制
  - 编码问题处理
  - 错误恢复能力

#### hotkey.py (热键管理)
- `HotkeyManager` 类：管理全局热键
  - 支持多个热键绑定
  - 防重复触发机制
  - 异常处理和日志记录

#### optimizer.py (文本优化)
- `optimize_chinese_text` 函数：调用 GPT API
  - 智能文本优化
  - 清晰的优化过程展示
  - 自动重试机制
  - 错误处理和日志记录

#### processor.py (文本处理)
- `TextProcessor` 类：核心处理流程
  - 文本获取和更新
  - 优化结果展示
  - 状态管理和错误处理

#### tray.py (托盘管理)
- `TrayManager` 类：系统托盘功能
  - 动态状态显示
  - 右键菜单管理
  - 图标创建和更新

### 工具模块 (utils/)

#### logger.py
- `ColorLogger` 类：彩色日志输出
  - 成功/信息/警告/错误等不同级别的日志
  - 美观的状态图标
  - 清晰的颜色区分

## 安装和使用

### 环境要求
- Python 3.7+
- Windows 操作系统

### 依赖安装
```bash
pip install requests colorama pystray pillow keyboard pywin32
```

### 配置
1. 在 `config/settings.py` 中设置你的 OpenAI API 密钥：
```python
API_KEY = "your-api-key"
```

2. (可选) 自定义热键：
```python
HOTKEYS = ["f9", "ctrl+alt+space"]
```

### 运行
```bash
python main.py
```

## 使用方法

1. 运行程序后，托盘区域会出现一个图标
2. 选中需要优化的文本
3. 按 F9 或 Ctrl+Alt+Space
4. 等待处理完成（托盘图标会显示处理状态）
5. 原文本会自动被优化后的文本替换

## 状态说明

托盘图标颜色：
- 🟢 绿色：空闲，可以使用
- 🔴 红色：正在处理

## 错误处理

程序包含多重错误处理机制：
- 剪贴板操作：使用 win32clipboard，更稳定可靠
- API 调用：自动重试 3 次
- 文本处理：完整的错误恢复
- 状态管理：自动重置状态

## 开发说明

### 扩展功能
1. 在 `core/` 添加新的功能模块
2. 在 `config/settings.py` 添加相关配置
3. 在 `main.py` 中集成新功能

### 自定义优化
可以通过修改 `optimizer.py` 中的 prompt 来自定义优化规则：
```python
"content": (
    "你是一位语言优化助手，帮助用户改进中文表达，"
    "使其更加简洁、自然、流畅、优雅..."
)
```

## 注意事项

1. 确保有稳定的网络连接
2. 不要频繁、快速地触发热键
3. 处理大段文本时可能需要等待较长时间
4. 建议定期检查 API 调用额度

## 常见问题

1. Q: 热键没有响应？
   A: 检查是否有其他程序占用了相同的热键

2. Q: 文本没有被替换？
   A: 确保文本已被正确选中，且有足够的权限

3. Q: 托盘图标消失？
   A: 尝试重启程序，检查是否有权限问题

4. Q: 剪贴板操作失败？
   A: 程序使用 win32clipboard，确保系统剪贴板没有被其他程序锁定

## 更新日志

### v1.1.0 (2024-03-30)
- 优化剪贴板操作，使用 win32clipboard 提高稳定性
- 改进输出格式，添加清晰的分隔和状态显示
- 优化网络连接处理
- 改进错误处理和日志记录

### v1.0.0 (2024-03-29)
- 初始版本发布
- 基本的文本优化功能
- 托盘状态显示
- 热键支持

## 贡献指南

欢迎提交 Issue 和 Pull Request！

## 许可证

MIT License
```

这个 README 详细说明了项目的：
1. 功能特点
2. 项目结构
3. 每个模块的具体功能
4. 安装和使用方法
5. 错误处理机制
6. 开发指南
7. 常见问题

需要补充或修改的部分吗？