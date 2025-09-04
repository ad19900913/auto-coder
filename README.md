# 自动化AI任务执行系统

🚀 一个基于Python的自动化AI任务执行系统，支持多种任务类型，包括代码生成、代码审查、文档生成、需求审查和自定义任务。

## ✨ 系统特性

- **🤖 多AI服务支持**: 集成Claude、DeepSeek、Gemini、Cursor等主流AI服务，支持服务工厂模式
- **📅 灵活调度**: 支持crontab表达式、间隔调度、指定时间调度
- **🔧 多任务类型**: 编码、审查、文档、需求审查、自定义任务
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
│   └── 自定义异常 (exceptions) - 系统特定异常类型
├── 服务模块 (src/services/)
│   ├── 服务工厂 (ServiceFactory) - 统一服务实例创建和缓存
│   ├── AI服务 (AIService) - Claude、DeepSeek、Gemini、Cursor等AI服务抽象
│   ├── Git服务 (GitService) - GitHub、GitLab等Git平台抽象
│   └── 通知服务 (NotifyService) - 多渠道通知服务
├── 任务执行器 (src/tasks/)
│   ├── 编码任务执行器 (CodingTaskExecutor)
│   ├── 代码审查任务执行器 (ReviewTaskExecutor)
│   ├── 文档生成任务执行器 (DocTaskExecutor)
│   ├── 需求审查任务执行器 (RequirementReviewTaskExecutor)
│   └── 自定义任务执行器 (CustomTaskExecutor)
├── CLI接口 (src/cli/)
│   └── 命令行管理工具
├── 工作流模板 (workflows/)
│   ├── 基础模板 (base/) - 通用工作流步骤
│   ├── 编码任务模板 (coding/) - 编码任务专用流程
│   ├── 审查任务模板 (review/) - 审查任务专用流程
│   └── 文档任务模板 (doc/) - 文档任务专用流程
├── AI提示词模板 (prompts/)
│   ├── 编码任务提示词 (coding/) - 编码相关AI提示
│   ├── 审查任务提示词 (review/) - 审查相关AI提示
│   └── 文档任务提示词 (doc/) - 文档相关AI提示
└── 配置和文档
    ├── 全局配置文件 (config/global_config.yaml)
    ├── 任务配置文件 (config/tasks/)
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

## 📚 文档

- [使用示例](docs/使用示例.md) - 详细的使用示例和命令速查
- [Tab补全设置指南](docs/Tab补全设置指南.md) - Tab补全功能设置指南
- [邮件推送配置指南](docs/邮件推送配置指南.md) - 邮件通知配置指南

## 🤝 贡献

欢迎提交Issue和Pull Request来改进系统！

## �� 许可证

MIT License
