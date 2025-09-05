# 自动化AI任务执行系统

🚀 一个基于Python的自动化AI任务执行系统，支持多种任务类型，包括代码生成、代码审查、文档生成、需求审查和自定义任务。

## ✨ 系统特性

- **🤖 多AI服务支持**: 集成Claude、DeepSeek、Gemini、Cursor等主流AI服务，支持服务工厂模式
- **📅 灵活调度**: 支持crontab表达式、间隔调度、指定时间调度
- **🔧 多任务类型**: 编码、审查、文档、需求审查、自定义任务、智能任务生成、多模态AI、机器学习集成
- **⚙️ 工作流引擎**: 支持工作流模板、步骤控制、人工审批模式
- **📊 状态管理**: 完整的任务状态跟踪和持久化
- **🔄 并发执行**: 支持多任务并发执行，可配置最大工作线程数
- **❌ 错误处理**: 智能重试机制，指数退避策略，自定义异常体系
- **🔔 通知系统**: 支持钉钉机器人、邮件、Webhook等多种通知方式
- **💾 Git集成**: 支持GitHub、GitLab平台操作
- **📝 进度跟踪**: 实时任务进度更新和状态监控
- **🖥️ CLI管理**: 完整的命令行管理工具
- **✅ 配置验证**: 自动验证配置文件完整性和有效性
- **🎯 服务工厂**: 统一服务实例创建、缓存和依赖注入
- **📋 模板系统**: 工作流模板继承、AI提示词模板管理
- **🔧 增量修改**: 支持读取现有代码并进行增量修改，保持代码结构
- **🏗️ 复杂重构**: 支持大型项目的复杂重构分析，包括项目结构分析、依赖关系分析、重构计划生成
- **🔧 MCP服务**: 支持Model Context Protocol服务，AI可以使用外部工具和API
- **🧠 机器学习集成**: 预测模型、异常检测、智能调度、A/B测试
- **🎨 多模态AI**: 图像处理、文档解析、媒体内容分析
- **🤖 AI模型管理**: 模型版本控制、自动切换、性能监控
- **💡 智能任务生成**: 基于自然语言的任务配置生成和优化

## 🏗️ 系统架构

```
自动化AI任务执行系统
├── 核心模块 (src/core/)
│   ├── 配置管理器 (ConfigManager) - 全局和任务级配置管理
│   ├── 配置验证器 (ConfigValidator) - 配置文件完整性验证
│   ├── 状态管理器 (StateManager) - 任务状态跟踪和持久化
│   ├── 状态文件管理器 (StateFileManager) - 状态文件清理和归档
│   ├── 任务调度器 (TaskScheduler) - 基于APScheduler的任务调度
│   ├── 任务执行器基类 (TaskExecutor) - 任务执行标准接口
│   ├── 任务执行器工厂 (TaskExecutorFactory) - 任务执行器创建和注册
│   ├── 任务管理器 (TaskManager) - 任务生命周期管理
│   ├── 工作流引擎 (WorkflowEngine) - 工作流模板执行引擎
│   ├── 依赖管理器 (DependencyManager) - 任务依赖关系管理
│   └── 自定义异常 (exceptions) - 系统特定异常类型
├── 服务模块 (src/services/)
│   ├── 服务工厂 (ServiceFactory) - 统一服务实例创建和缓存
│   ├── AI服务 (AIService) - Claude、DeepSeek、Gemini、Cursor等AI服务抽象
│   ├── Git服务 (GitService) - GitHub、GitLab等Git平台抽象
│   ├── 通知服务 (NotifyService) - 多渠道通知服务
│   ├── 增量代码服务 (IncrementalCodeService) - 增量代码修改服务
│   ├── 复杂重构服务 (ComplexRefactorService) - 复杂重构分析服务
│   ├── MCP服务 (MCPService) - Model Context Protocol服务
│   ├── 智能任务服务 (IntelligentTaskService) - 智能任务生成和优化
│   ├── AI模型管理器 (AIModelManager) - AI模型版本控制和性能监控
│   ├── 多模态AI服务 (MultimodalAIService) - 图像、文档等多媒体处理
│   └── 机器学习服务 (MachineLearningService) - 预测模型、异常检测、A/B测试
├── 任务执行器 (src/tasks/)
│   ├── 编码任务执行器 (CodingTaskExecutor)
│   ├── 代码审查任务执行器 (ReviewTaskExecutor)
│   ├── 文档生成任务执行器 (DocTaskExecutor)
│   ├── 需求审查任务执行器 (RequirementReviewTaskExecutor)
│   ├── 自定义任务执行器 (CustomTaskExecutor)
│   ├── 智能任务执行器 (IntelligentTaskExecutor)
│   ├── AI模型管理执行器 (AIModelManagementExecutor)
│   ├── 多模态AI执行器 (MultimodalAIExecutor)
│   └── 机器学习执行器 (MachineLearningExecutor)
├── CLI接口 (src/cli/)
│   └── 命令行管理工具
├── 工作流模板 (workflows/)
│   ├── 基础模板 (base/) - 通用工作流步骤
│   ├── 编码任务模板 (coding/) - 编码任务专用流程
│   ├── 审查任务模板 (review/) - 审查任务专用流程
│   ├── 文档任务模板 (doc/) - 文档任务专用流程
│   ├── 自定义任务模板 (custom/) - 自定义任务流程
│   └── 需求审查模板 (requirement_review/) - 需求审查流程
├── AI提示词模板 (prompts/)
│   ├── 编码任务提示词 (coding/) - 编码相关AI提示
│   ├── 审查任务提示词 (review/) - 审查相关AI提示
│   ├── 文档任务提示词 (doc/) - 文档相关AI提示
│   ├── 自定义任务提示词 (custom/) - 自定义任务AI提示
│   └── 需求审查提示词 (requirement_review/) - 需求审查AI提示
├── 数据存储 (data/)
│   ├── AI模型数据库 (ai_models.db) - AI模型管理数据
│   └── 机器学习数据库 (ml_service.db) - 机器学习相关数据
├── 模型存储 (models/) - 机器学习模型文件
└── 配置和文档
    ├── 全局配置文件 (config/global_config.yaml)
    ├── 任务配置文件 (config/tasks/)
    ├── MCP配置文件 (config/mcp_config.yaml)
    ├── 编码规范模板 (standards/)
    └── 系统设计文档 (docs/)
```

## 📋 任务类型

| 任务类型 | 描述 | 主要功能 |
|---------|------|----------|
| **编码任务** | AI代码生成 | 根据提示生成代码，自动创建Git分支、提交和推送 |
| **代码审查** | 代码质量分析 | 分析代码质量，生成审查报告，支持多种编程语言 |
| **文档生成** | AI文档生成 | 基于提示自动生成文档，支持Markdown、HTML等格式 |
| **需求审查** | 需求与代码一致性分析 | 分析需求文档与代码实现的一致性，生成审查报告 |
| **自定义任务** | 任意AI任务 | 支持任意场景的AI任务执行，灵活配置输出格式 |
| **智能任务生成** | 自然语言任务配置 | 基于自然语言描述自动生成任务配置和优化建议 |
| **AI模型管理** | 模型版本控制 | 注册、切换、监控AI模型，支持性能跟踪和自动切换 |
| **多模态AI** | 多媒体内容处理 | 图像识别、文档解析、媒体内容分析和格式转换 |
| **机器学习集成** | 智能预测和优化 | 任务执行预测、异常检测、A/B测试、智能调度 |

## 🚀 快速开始

### 环境要求

- Python 3.8+
- Windows 10/11
- Git

### 安装依赖

```bash
# 安装基础依赖
pip install -r requirements.txt

# 或者手动安装主要依赖
pip install PyYAML click APScheduler requests GitPython python-dotenv argcomplete
```

### 🔧 Tab补全设置（可选）

为了提升使用体验，可以设置Tab补全功能：

```bash
# 运行补全设置脚本
bash autocomplete_setup.sh

# 重新加载配置
source ~/.bashrc
```

设置后可以使用以下别名和补全：
- `system-manager [TAB]` - 系统管理命令补全

### 🧪 系统自测

系统提供了专门的自测工具 `system_manager.py`，用于验证系统功能和调度机制：

#### 1. 启动系统进行自测

```bash
# 启动系统并持续运行（推荐用于自测）
python system_manager.py run
```

系统启动后会：
- ✅ 自动加载所有任务配置
- ✅ 启动任务调度器
- ✅ 显示任务调度状态
- ✅ 保持进程运行等待任务执行

#### 2. 检查系统状态

在另一个终端窗口检查系统状态：

```bash
# 检查系统运行状态
python system_manager.py status

# 停止系统
python system_manager.py stop
```

#### 3. 自测功能验证

通过自测可以验证：
- ✅ 配置加载和验证
- ✅ 任务调度器启动
- ✅ 定时任务调度
- ✅ 任务执行流程
- ✅ 状态文件管理
- ✅ 通知服务集成
- ✅ AI服务连接
- ✅ Git服务操作

#### 4. 查看执行日志

系统运行时会实时显示详细日志：
```
2025-09-02 18:16:00,001 - apscheduler.executors.default - INFO - Running job "Task_auto-webhook-tool"
2025-09-02 18:16:00,002 - src.services.service_factory - INFO - AI服务创建成功: deepseek
2025-09-02 18:16:00,002 - src.services.service_factory - INFO - Git服务创建成功: github
2025-09-02 18:16:00,004 - src.core.task_executor.auto-webhook-tool - INFO - 服务初始化成功
```

### 配置系统

#### 1. 设置环境变量

创建 `.env` 文件或在系统环境变量中设置：

```bash
# AI服务配置
CLAUDE_API_KEY=your_claude_api_key
DEEPSEEK_API_KEY=your_deepseek_api_key
GEMINI_API_KEY=your_gemini_api_key
CURSOR_API_KEY=your_cursor_api_key
DEFAULT_AI_SERVICE=deepseek

# Git服务配置
GITHUB_TOKEN=your_github_token
GITHUB_USERNAME=your_github_username
GITLAB_TOKEN=your_gitlab_token
GITLAB_BASE_URL=https://gitlab.com
GITLAB_USERNAME=your_gitlab_username
DEFAULT_GIT_SERVICE=github

# 通知服务配置
DINGTALK_WEBHOOK=your_dingtalk_webhook_url
DINGTALK_SECRET=your_dingtalk_secret

# 邮件服务配置
EMAIL_SMTP_SERVER=smtp.gmail.com
EMAIL_USERNAME=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
EMAIL_FROM_EMAIL=your-email@gmail.com
EMAIL_TO_EMAILS=admin@company.com,user1@company.com
```

#### 2. 配置全局设置

编辑 `config/global_config.yaml`：

```yaml
# 系统基本信息
name: "自动化AI任务执行系统"
version: "1.0.0"
max_concurrent_tasks: 5

# AI服务配置
ai_services:
  default: "${DEFAULT_AI_SERVICE}"
  claude:
    api_key: "${CLAUDE_API_KEY}"
    base_url: "https://api.anthropic.com"
    model: "claude-3-sonnet-20240229"
  deepseek:
    api_key: "${DEEPSEEK_API_KEY}"
    base_url: "https://api.deepseek.com"
    model: "deepseek-reasoner"
  gemini:
    api_key: "${GEMINI_API_KEY}"
    base_url: "https://generativelanguage.googleapis.com"
    model: "gemini-1.5-pro"
  cursor:
    api_key: "${CURSOR_API_KEY}"
    base_url: "https://api.cursor.sh"
    model: "cursor-1"

# Git配置
git:
  default: "${DEFAULT_GIT_SERVICE}"
  github:
    token: "${GITHUB_TOKEN}"
    username: "${GITHUB_USERNAME}"
```

#### 3. 创建任务配置

在 `config/tasks/` 目录下创建任务配置文件：

```yaml
# config/tasks/example_coding_task.yaml
task_id: "example_coding_task"
name: "示例编码任务"
description: "使用AI生成示例代码"
type: "coding"
enabled: true

# 任务调度配置
schedule:
  type: "cron"
  cron_expressions: ["0 9 * * *"]  # 每天上午9点执行
  timezone: "UTC+8"

# 编码任务配置
coding:
  # 完整生成模式
  incremental_mode: false  # 完整生成模式
  project_path: "outputs/example_project"
  branch_name: "feature/ai-generated-code"
  prompt: "创建一个Python Web API服务"
  
  # 增量修改模式
  # incremental_mode: true  # 启用增量修改
  # target_file: "src/services/example_service.py"  # 要修改的目标文件
  # language: "python"  # 编程语言
  # prompt: "为现有类添加新的方法"

# 编码任务特定配置
coding:
  project_path: "outputs/example-project"
  branch_name: "feature/ai-generated"
  base_branch: "master"
  prompt: "创建一个简单的Web应用"

# AI配置 - 可选择不同的AI服务
ai:
  provider: "deepseek"  # 可选: claude, deepseek, gemini, cursor
  model: "deepseek-reasoner"
  temperature: 0.1
  max_tokens: 4000

# 通知配置
notifications:
  channels:
    - "dingtalk"
  events:
    - "task_start"
    - "task_complete"
    - "task_error"
```

## 🛠️ 使用指南

### 系统管理命令（推荐）

```bash
# 使用完整路径
python system_manager.py daemon    # 后台启动系统
python system_manager.py status    # 查看系统状态
python system_manager.py stop      # 停止系统

# 使用别名（需要先运行 autocomplete_setup.sh）
system-manager daemon              # 后台启动系统
system-manager status              # 查看系统状态
system-manager stop                # 停止系统
system-manager --help              # 查看帮助
```

### 任务配置示例

#### 编码任务配置

```yaml
task_id: "webhook-tool"
name: "Webhook管理工具"
type: "coding"
enabled: true

schedule:
  type: "cron"
  cron_expressions: ["0 9 * * 1"]  # 每周一上午9点
  timezone: "UTC+8"

coding:
  project_path: "outputs/webhook-tool"
  branch_name: "feature/webhook-management"
  base_branch: "master"
  prompt: "创建一个Webhook管理工具，支持增删改查功能"
```

#### 代码审查任务配置

```yaml
task_id: "code-review"
name: "代码质量审查"
type: "review"
enabled: true

schedule:
  type: "interval"
  seconds: 3600  # 每小时执行一次

review:
  target_path: "outputs/webhook-tool"
  output_format: "markdown"
  check_types: ["quality", "security", "performance"]
```

## 📊 监控和日志

### 日志文件位置

- **系统日志**: `logs/system_manager.log`
- **CLI日志**: `logs/cli.log`
- **任务状态**: `states/<task_id>.json`

### 状态监控

系统提供多种监控方式：

1. **实时日志监控**: 通过 `system_manager.py run` 查看实时执行日志
2. **状态文件检查**: 查看 `states/` 目录下的任务状态文件
3. **CLI状态查询**: 使用 `python system_manager.py status` 查看系统状态

## 🔧 故障排除

### 常见问题

1. **任务调度失败**
   - 检查cron表达式格式
   - 确认时区设置正确
   - 查看调度器日志

2. **AI服务连接失败**
   - 检查API密钥配置
   - 确认网络连接
   - 验证服务配额

3. **Git操作失败**
   - 检查Git凭证配置
   - 确认仓库权限
   - 验证分支名称

4. **通知发送失败**
   - 检查Webhook URL
   - 确认通知服务配置
   - 验证网络连接

### 调试技巧

1. **启用详细日志**:
   ```bash
   python system_manager.py run --verbose
   ```

2. **检查配置文件**:
   ```bash
   python system_manager.py status
   ```

3. **验证任务配置**:
   ```bash
   python system_manager.py status
   ```

## 🤖 AI服务使用指南

### 支持的AI服务

系统目前支持以下AI服务：

| 服务 | 提供商 | 模型 | 特点 |
|------|--------|------|------|
| **Claude** | Anthropic | claude-3-sonnet-20240229 | 代码生成能力强，逻辑清晰 |
| **DeepSeek** | DeepSeek | deepseek-reasoner | 推理能力强，适合复杂任务 |
| **Gemini** | Google | gemini-1.5-pro | 多模态支持，响应速度快 |
| **Cursor** | Cursor | cursor-1 | 代码理解能力强，适合IDE集成 |

### 配置AI服务

#### 1. 设置环境变量

```bash
# 选择默认AI服务
DEFAULT_AI_SERVICE=cursor  # 可选: claude, deepseek, gemini, cursor

# 配置API密钥
CLAUDE_API_KEY=your_claude_api_key
DEEPSEEK_API_KEY=your_deepseek_api_key
GEMINI_API_KEY=your_gemini_api_key
CURSOR_API_KEY=your_cursor_api_key
```

#### 2. 任务级AI配置

在任务配置文件中指定使用的AI服务：

```yaml
# 使用Cursor
ai:
  provider: "cursor"
  model: "cursor-1"
  temperature: 0.1
  max_tokens: 6000

# 使用DeepSeek
ai:
  provider: "deepseek"
  model: "deepseek-reasoner"
  temperature: 0.05
  max_tokens: 4000

# 使用Claude
ai:
  provider: "claude"
  model: "claude-3-sonnet-20240229"
  temperature: 0.1
  max_tokens: 4000
```

### 测试AI服务

#### 测试Cursor API

```bash
# 运行Cursor功能测试
python test_cursor.py
```

#### 测试Gemini API

```bash
# 运行Gemini功能测试
python test_gemini.py
```

#### 测试邮件发送

```bash
# 运行邮件发送测试
python test_email.py
```

### AI服务选择建议

- **代码生成**: 推荐使用 **Cursor** 或 **Claude**，代码质量高
- **代码审查**: 推荐使用 **DeepSeek**，逻辑分析能力强
- **需求分析**: 推荐使用 **DeepSeek**，推理能力优秀
- **文档生成**: 推荐使用 **Claude**，文档结构清晰
- **IDE集成**: 推荐使用 **Cursor**，代码理解能力强
- **自定义任务**: 根据任务特点选择合适的服务

## 🔧 增量代码修改功能

### 功能概述

系统支持**增量代码修改**功能，可以读取现有代码文件，分析代码结构，并根据AI提示进行精确的增量修改，而不是重新生成整个文件。

### 核心特性

- **📖 代码读取**: 自动读取现有代码文件内容
- **🔍 结构分析**: 分析代码结构（类、函数、导入等）
- **🤖 AI智能修改**: 基于现有代码结构进行精确修改
- **💾 自动备份**: 修改前自动创建备份文件
- **📊 差异报告**: 生成详细的代码变更报告
- **✅ 语法验证**: 验证修改后代码的语法正确性
- **🔄 版本控制**: 支持Git版本控制集成

### 使用场景

1. **功能扩展**: 为现有类添加新方法
2. **Bug修复**: 修复现有代码中的问题
3. **性能优化**: 优化现有代码的性能
4. **代码重构**: 重构现有代码结构
5. **依赖更新**: 更新导入和依赖关系

### 配置示例

#### 1. 增量修改模式配置

```yaml
# config/tasks/incremental_coding_example.yaml
task_id: incremental_coding_example
task_type: coding
enabled: true

coding:
  # 启用增量修改模式
  incremental_mode: true
  target_file: "src/services/example_service.py"  # 要修改的目标文件
  language: "python"  # 编程语言
  
  # 项目配置
  project_path: "outputs/incremental_coding_example"
  branch_name: "feature/incremental-update"
  
  # 修改提示
  prompt: |
    请为现有的ExampleService类添加以下功能：
    1. 添加一个新的方法calculate_average，用于计算数字列表的平均值
    2. 在现有的process_data方法中添加错误处理逻辑
    3. 添加一个新的属性max_retries，默认值为3
    4. 确保保持现有的代码结构和风格
```

#### 2. 支持的编程语言

- **Python**: 完整的AST分析支持
- **JavaScript**: 基础结构分析支持
- **Java**: 基础结构分析支持
- **其他语言**: 通用结构分析支持

### 工作流程

1. **读取现有代码**: 系统读取目标文件内容
2. **分析代码结构**: 解析类、函数、导入等结构信息
3. **生成AI提示**: 基于现有代码和修改要求生成精确的AI提示
4. **AI智能修改**: AI根据提示进行增量修改
5. **应用修改**: 将修改应用到原文件
6. **创建备份**: 自动创建备份文件
7. **生成报告**: 生成详细的变更报告
8. **语法验证**: 验证修改后代码的语法正确性

### 安全特性

- **自动备份**: 每次修改前自动创建备份文件
- **差异报告**: 详细记录所有变更内容
- **语法验证**: 确保修改后代码的语法正确性
- **版本控制**: 支持Git版本控制，可回滚变更

### 测试增量修改功能

运行测试脚本验证增量修改功能：

```bash
# 运行增量修改测试
python test_incremental_code.py
```

测试脚本会：
1. 读取示例代码文件
2. 分析代码结构
3. 生成增量修改提示
4. 模拟AI修改过程
5. 应用修改并生成报告
6. 验证语法正确性

## 🏗️ 复杂重构功能

系统支持**复杂重构分析**功能，可以对大型项目进行深度的架构分析，生成详细的重构计划，帮助开发者进行系统性的代码重构。

### 功能特性

- **📊 项目结构分析**: 分析项目文件结构、模块组织
- **🔗 依赖关系分析**: 构建依赖图，识别循环依赖和强连通分量
- **📈 复杂度分析**: 计算代码复杂度指标，识别重构热点
- **📋 重构计划生成**: 基于分析结果生成详细的重构计划
- **⚙️ 重构步骤执行**: 模拟重构步骤的执行过程
- **📊 风险评估**: 评估重构的风险等级和影响范围
- **⏱️ 工作量估算**: 估算重构工作量和时间成本

### 使用场景

1. **架构重构**: 大型项目的架构级重构
2. **模块拆分**: 拆分过大的模块和类
3. **依赖优化**: 优化模块间的依赖关系
4. **性能重构**: 识别和重构性能瓶颈
5. **代码质量提升**: 提升整体代码质量

### 配置示例

#### 1. 复杂重构模式配置

```yaml
# config/tasks/complex_refactor_example.yaml
task_id: complex_refactor_example
task_type: coding
enabled: true

coding:
  # 启用复杂重构模式
  complex_refactor_mode: true
  refactor_request: |
    对项目进行架构级重构，主要包括：
    1. 拆分大型服务类，提高代码的可维护性
    2. 提取公共组件，减少代码重复
    3. 优化数据库访问层，提高性能
    4. 重构API接口，提高一致性
    5. 优化错误处理机制，提高系统稳定性
  
  # 项目配置
  project_path: "outputs/complex_refactor_example"
  branch_name: "feature/architecture-refactor"
  
  # 输出文件配置
  output_file: "refactor_analysis_report.md"
  
  # 编码提示（复杂重构模式下主要用于生成报告）
  prompt: |
    请分析项目结构并生成详细的重构计划，包括：
    - 项目复杂度分析
    - 重构热点识别
    - 分步重构计划
    - 风险评估
    - 工作量估算

# AI服务配置
ai:
  provider: "deepseek"  # 使用DeepSeek AI服务进行复杂分析
  model: "deepseek-chat"
  max_tokens: 4000
  temperature: 0.1

# 任务参数
parameters:
  max_retries: 3
  timeout: 600  # 复杂重构需要更长时间
  backup_enabled: true
  include_patterns: ["*.py", "*.java", "*.js", "*.ts"]  # 包含的文件类型
  exclude_patterns: ["*/node_modules/*", "*/venv/*", "*/__pycache__/*"]  # 排除的目录
```

#### 2. 支持的分析类型

- **Python项目**: 完整的AST分析，支持类、函数、导入分析
- **JavaScript项目**: 基础结构分析，支持ES6+语法
- **Java项目**: 基础结构分析，支持类和包结构
- **混合项目**: 支持多语言混合项目的分析

### 分析能力

#### 1. 项目结构分析

- **文件扫描**: 扫描项目中的所有代码文件
- **模块识别**: 识别项目的模块组织结构
- **依赖图构建**: 构建文件间的依赖关系图
- **复杂度计算**: 计算每个文件的复杂度指标

#### 2. 重构热点识别

- **高复杂度文件**: 识别复杂度过高的文件
- **循环依赖**: 识别模块间的循环依赖
- **重复代码**: 识别重复的代码模式
- **性能瓶颈**: 识别潜在的性能问题

#### 3. 重构计划生成

- **分步重构**: 生成详细的重构步骤
- **风险评估**: 评估每个重构步骤的风险
- **工作量估算**: 估算重构所需的工作量
- **测试策略**: 生成重构后的测试策略

### 工作流程

1. **项目扫描**: 扫描项目文件结构
2. **代码分析**: 分析每个文件的代码结构
3. **依赖分析**: 构建依赖关系图
4. **热点识别**: 识别重构热点
5. **计划生成**: 生成详细的重构计划
6. **风险评估**: 评估重构风险
7. **报告生成**: 生成重构分析报告

### 测试复杂重构功能

运行测试脚本验证复杂重构功能：

```bash
# 运行复杂重构测试
python test_complex_refactor.py
```

测试脚本会：
1. 创建测试项目结构
2. 分析项目结构
3. 生成重构计划
4. 执行重构步骤
5. 生成重构报告

### 输出报告

复杂重构功能会生成详细的重构分析报告，包括：

- **项目概览**: 项目基本信息和统计
- **复杂度分析**: 详细的复杂度指标
- **重构热点**: 识别出的重构热点列表
- **重构计划**: 详细的重构步骤计划
- **风险评估**: 重构风险等级和影响分析
- **工作量估算**: 预估的工作量和时间成本

## 🧠 机器学习集成功能

系统集成了强大的机器学习功能，提供智能预测、异常检测、A/B测试等能力。

### 功能特性

- **📊 任务执行预测**: 基于历史数据预测任务执行时间和成功率
- **🚨 异常检测**: 自动检测任务执行异常，识别性能问题
- **🧪 A/B测试**: 支持A/B测试框架，对比不同配置的效果
- **⚡ 智能调度**: 基于机器学习的智能任务调度优化
- **📈 性能监控**: 实时监控模型性能，自动切换最佳模型

### 使用场景

1. **任务优化**: 预测任务执行时间，优化资源配置
2. **异常监控**: 自动检测异常任务，及时发现问题
3. **配置对比**: 通过A/B测试找到最佳任务配置
4. **智能调度**: 基于历史数据优化任务执行顺序

### 配置示例

```yaml
# 机器学习集成任务配置
task_id: ml_prediction_task
name: "任务执行预测"
type: "machine_learning"
enabled: true

machine_learning:
  operation: "predict_task"
  task_config:
    type: "coding"
    priority: 7
    schedule:
      type: "cron"
      expression: "0 9 * * 1-5"
    dependencies:
      - task_id: "data_preparation"
        type: "required"
    resources:
      cpu: 2
      memory: 2048
      disk: 500
```

## 🎨 多模态AI功能

系统支持强大的多媒体内容处理能力，包括图像、文档等多种媒体类型。

### 功能特性

- **🖼️ 图像处理**: 图像识别、分析、文字提取、图像增强、特征提取
- **📄 文档解析**: PDF、Word文档解析，文本提取、段落分析、表格提取
- **📝 文本处理**: 文本分析、关键信息提取、智能摘要、内容分类
- **🔄 格式转换**: 支持多种媒体格式之间的转换
- **📊 批量处理**: 支持批量处理多个媒体文件

### 支持的媒体类型

- **图像**: JPG, PNG, GIF, BMP, TIFF, WebP
- **PDF文档**: 完整的PDF解析和内容提取
- **Word文档**: DOCX, DOC格式支持
- **文本文件**: TXT, MD, JSON, XML, CSV

### 配置示例

```yaml
# 多模态AI任务配置
task_id: multimodal_analysis_task
name: "多媒体内容分析"
type: "multimodal_ai"
enabled: true

multimodal_ai:
  operation: "process_single_file"
  file_path: "./test_files/sample_image.jpg"
  processing_type: "analysis"
  options:
    use_ai_analysis: true
    max_tokens: 1000
    temperature: 0.3
    prompt: "请分析这张图片的内容"
```

## 🤖 AI模型管理功能

系统提供完整的AI模型版本控制和性能监控能力。

### 功能特性

- **📝 模型注册**: 注册新的AI模型版本
- **🔄 自动切换**: 根据性能自动切换最佳模型
- **📊 性能监控**: 实时监控模型性能指标
- **💾 版本控制**: 完整的模型版本管理
- **📈 统计分析**: 详细的模型使用统计和分析

### 支持的模型类型

- **文本生成**: TEXT_GENERATION
- **代码生成**: CODE_GENERATION
- **文本分析**: TEXT_ANALYSIS
- **多模态**: MULTIMODAL
- **嵌入模型**: EMBEDDING

### 配置示例

```yaml
# AI模型管理任务配置
task_id: model_management_task
name: "AI模型管理"
type: "ai_model_management"
enabled: true

ai_model_management:
  operation: "register_model"
  model_config:
    model_name: "claude-3-sonnet"
    model_type: "text_generation"
    version: "20240229"
    provider: "anthropic"
    api_key: "${ANTHROPIC_API_KEY}"
    parameters:
      max_tokens: 4000
      temperature: 0.7
    set_active: true
```

## 💡 智能任务生成功能

系统支持基于自然语言的智能任务生成和优化。

### 功能特性

- **🗣️ 自然语言理解**: 理解自然语言描述的任务需求
- **⚙️ 自动配置生成**: 自动生成完整的任务配置
- **📊 执行预测**: 预测任务执行时间和成功率
- **🎯 参数优化**: 智能优化任务参数配置
- **📋 模板推荐**: 基于历史数据推荐任务模板

### 使用场景

1. **快速配置**: 用自然语言快速生成任务配置
2. **参数优化**: 自动优化任务参数，提高执行效率
3. **模板学习**: 从历史任务中学习最佳实践
4. **智能建议**: 提供任务配置的优化建议

### 配置示例

```yaml
# 智能任务生成配置
task_id: intelligent_task_generation
name: "智能任务生成"
type: "intelligent_task"
enabled: true

intelligent_task:
  description: "请为我生成一个用户管理系统的API文档生成任务，包括用户注册、登录、信息修改等功能"
  context:
    project_type: "web_application"
    technology_stack: ["Spring Boot", "MySQL", "Redis"]
    output_format: "markdown"
```

## 🔧 MCP服务功能

系统支持**Model Context Protocol (MCP)** 服务，允许AI使用外部工具和API，大大扩展了AI的能力范围。

### 功能特性

- **🔧 工具集成**: 集成各种外部工具和API
- **🛠️ 自定义工具**: 支持注册自定义工具函数
- **🔍 工具发现**: 自动发现和注册MCP服务器工具
- **⚡ 工具调用**: AI可以直接调用MCP工具
- **🔒 安全控制**: 支持工具调用权限和安全沙箱
- **📊 工具管理**: 统一的工具管理和调用接口
- **🔄 自动加载**: 系统启动时自动读取并注册配置的MCP服务

### 自动配置加载

- **全局配置**: `config/mcp_config.yaml` 定义全局MCP服务
- **任务级配置**: 任务YAML文件中的 `mcp` 部分定义任务特定服务
- **自动加载**: 系统启动时自动读取并注册配置的MCP服务
- **环境变量**: 支持在配置中使用环境变量替换

### 支持的MCP服务器类型

#### 1. 文件系统服务器
- **read_file**: 读取文件内容
- **write_file**: 写入文件内容
- **list_directory**: 列出目录内容

#### 2. 数据库服务器
- **query_database**: 执行数据库查询
- **execute_sql**: 执行SQL语句

#### 3. 网络服务器
- **http_request**: 发送HTTP请求
- **api_call**: 调用外部API

#### 4. 自定义服务器
- **自定义工具**: 支持任意自定义工具函数

### 使用场景

1. **文件操作**: AI可以读取、写入、分析文件
2. **数据查询**: AI可以查询数据库获取信息
3. **API调用**: AI可以调用外部API服务
4. **代码分析**: AI可以使用代码分析工具
5. **项目管理**: AI可以执行Git操作等

### 配置示例

#### 1. MCP服务配置

```yaml
# config/mcp_config.yaml
mcp_services:
  # 文件系统MCP服务器
  filesystem_server:
    type: "filesystem"
    enabled: true
    root_path: "./workspace"
    allowed_extensions: [".py", ".js", ".java", ".md", ".txt", ".json", ".yaml", ".yml"]
    max_file_size: 10485760  # 10MB
    
  # 数据库MCP服务器
  database_server:
    type: "database"
    enabled: false
    connection_string: "sqlite:///./data.db"
    allowed_tables: ["users", "projects", "tasks"]
    
  # 自定义MCP服务器
  custom_server:
    type: "custom"
    enabled: true
    script_path: "./mcp_scripts/custom_server.py"
    environment_variables:
      CUSTOM_API_KEY: "${CUSTOM_API_KEY}"
      CUSTOM_BASE_URL: "https://api.custom.com"

# MCP工具配置
mcp_tools:
  # 默认启用的工具
  default_tools:
    - "filesystem_server.read_file"
    - "filesystem_server.write_file"
    - "filesystem_server.list_directory"
    
  # 自定义工具
  custom_tools:
    code_analyzer:
      description: "分析代码质量和复杂度"
      parameters:
        file_path: {"type": "string", "description": "要分析的代码文件路径"}
        analysis_type: {"type": "string", "description": "分析类型", "default": "quality"}
```

#### 2. MCP任务配置

```yaml
# config/tasks/mcp_tool_example.yaml
task_id: mcp_tool_example
task_type: custom
enabled: true

custom:
  # 启用MCP工具模式
  mcp_tool_mode: true
  
  # 要使用的MCP工具
  mcp_tools:
    - "filesystem_server.read_file"
    - "filesystem_server.write_file"
    - "filesystem_server.list_directory"
    - "custom.code_analyzer"
    - "custom.project_scanner"
  
  # 任务提示
  prompt: |
    请使用MCP工具完成以下任务：
    1. 扫描当前项目结构
    2. 分析主要代码文件的质量
    3. 生成项目分析报告
    4. 将报告保存到outputs目录

# MCP服务配置
mcp:
  servers:
    filesystem_server:
      type: "filesystem"
      root_path: "./"
      allowed_extensions: [".py", ".js", ".java", ".md", ".txt"]
    
    custom:
      type: "custom"
      tools:
        code_analyzer:
          description: "分析代码质量"
          parameters:
            file_path: {"type": "string", "description": "要分析的代码文件路径"}
            analysis_type: {"type": "string", "description": "分析类型", "default": "quality"}
```

### 工具调用方式

#### 1. 通过AI服务调用

```python
# AI服务可以直接调用MCP工具
result = ai_service.call_mcp_tool('filesystem_server.read_file', {
    'path': 'src/main.py'
})

# 获取可用工具
tools = ai_service.get_available_mcp_tools()
```

#### 2. 通过工具管理器调用

```python
# 直接使用工具管理器
tool_manager = MCPToolManager()

# 调用MCP工具
result = tool_manager.call_tool('filesystem_server.read_file', {
    'path': 'src/main.py'
})

# 注册自定义工具
def custom_analyzer(file_path: str):
    return {'quality_score': 85, 'suggestions': ['添加注释']}

tool_manager.register_tool('custom_analyzer', custom_analyzer, "分析代码质量")

# 调用自定义工具
result = tool_manager.call_tool('custom_analyzer', {
    'file_path': 'src/main.py'
})
```

### 安全特性

- **权限控制**: 每个工具都有明确的权限配置
- **沙箱执行**: 工具在安全沙箱中执行
- **审计日志**: 记录所有工具调用操作
- **超时控制**: 防止工具执行时间过长
- **资源限制**: 限制内存和网络访问

### 测试MCP功能

运行测试脚本验证MCP功能：

```bash
# 运行MCP服务测试
python test_mcp_service.py
```

测试脚本会：
1. 创建MCP服务实例
2. 注册文件系统MCP服务器
3. 发现可用工具
4. 测试文件读取、写入、目录列表功能
5. 测试自定义工具注册和调用
6. 验证工具管理器功能

### 扩展MCP功能

#### 1. 添加新的MCP服务器

```python
# 创建新的MCP服务器类型
class CustomMCPServer:
    def __init__(self, config):
        self.config = config
    
    def list_tools(self):
        return [
            {
                'name': 'custom_tool',
                'description': '自定义工具',
                'parameters': {
                    'param1': {'type': 'string', 'description': '参数1'}
                }
            }
        ]
    
    def call_tool(self, tool_name, parameters):
        if tool_name == 'custom_tool':
            return self._execute_custom_tool(parameters)
        return {'error': f'工具不存在: {tool_name}'}
```

#### 2. 注册自定义工具

```python
# 注册自定义工具函数
def my_custom_tool(param1: str, param2: int = 10):
    """自定义工具函数"""
    return {
        'result': f'处理结果: {param1}, 数值: {param2}',
        'timestamp': datetime.now().isoformat()
    }

tool_manager.register_tool('my_custom_tool', my_custom_tool, "自定义工具描述")
```

## 📚 文档

- [使用示例](docs/使用示例.md) - 详细的使用示例和命令速查
- [Tab补全设置指南](docs/Tab补全设置指南.md) - Tab补全功能设置指南
- [邮件推送配置指南](docs/邮件推送配置指南.md) - 邮件通知配置指南

## 🤝 贡献

欢迎提交Issue和Pull Request来改进系统！

## �� 许可证

MIT License
