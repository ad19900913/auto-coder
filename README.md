# 自动化AI任务执行系统

🚀 一个基于Python的自动化AI任务执行系统，支持多种任务类型，包括代码生成、代码审查、文档生成、需求审查和自定义任务。

## ✨ 系统特性

- **🤖 多AI服务支持**: 集成Claude、DeepSeek等主流AI服务，支持服务工厂模式
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
│   ├── AI服务 (AIService) - Claude、DeepSeek等AI服务抽象
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
pip install PyYAML click APScheduler requests GitPython
```

### 系统验证

运行系统测试脚本验证安装：

```bash
python test_system.py
```

如果看到 "🎉 所有测试通过！系统基本功能正常" 表示安装成功。

### 配置系统

#### 1. 设置环境变量

创建 `.env` 文件或在系统环境变量中设置：

```bash
# AI服务配置
CLAUDE_API_KEY=your_claude_api_key
DEEPSEEK_API_KEY=your_deepseek_api_key

# Git服务配置
GITHUB_TOKEN=your_github_token
GITHUB_USERNAME=your_github_username
GITLAB_TOKEN=your_gitlab_token
GITLAB_BASE_URL=https://gitlab.com
GITLAB_USERNAME=your_gitlab_username

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
  default: "claude"
  claude:
    api_key: "${CLAUDE_API_KEY}"
    base_url: "https://api.anthropic.com"
    model: "claude-3-sonnet-20240229"

# Git配置
git:
  default: "github"
  github:
    token: "${GITHUB_TOKEN}"
    username: "${GITHUB_USERNAME}"
```

#### 3. 创建工作流模板

系统支持工作流模板，在 `workflows/` 目录下创建：

```bash
workflows/
├── base/                    # 基础模板
│   └── base_workflow.yaml
├── coding/                  # 编码任务模板
│   └── coding_workflow.yaml
├── review/                  # 审查任务模板
│   └── review_workflow.yaml
└── doc/                     # 文档任务模板
    └── doc_workflow.yaml
```

#### 4. 创建AI提示词模板

在 `prompts/` 目录下创建提示词模板：

```bash
prompts/
├── coding/
│   ├── coding_init_prompt.md
│   └── coding_implement_prompt.md
├── review/
│   └── review_init_prompt.md
└── doc/
    └── doc_init_prompt.md
```

#### 5. 创建任务配置

在 `config/tasks/` 目录下创建任务配置文件：

```yaml
# config/tasks/example_coding_task.yaml
task_id: "example_coding_task"
name: "示例编码任务"
type: "coding"
enabled: true

# 工作流模式配置
workflow_mode: "manual"  # manual 或 automated

# 调度配置
schedule:
  type: "cron"
  expression: "0 9 * * 1-5"  # 工作日早上9点

# AI服务配置
ai:
  provider: "claude"
  model: "claude-3-sonnet-20240229"
  temperature: 0.1

# Git服务配置
git:
  platform: "github"
  repo_url: "https://github.com/your-username/your-repo"
  branch: "main"

# 通知配置
notifications:
  events: ["start", "complete", "error"]
  channels: ["dingtalk"]

# 重试和超时配置
retry:
  max_attempts: 3
  base_delay: 60

timeout:
  task: 1800  # 30分钟
```

### 启动系统

#### 方式1: 使用CLI工具（推荐）

```bash
# 查看系统状态
python src/cli/main.py status

# 列出所有任务
python src/cli/main.py list-tasks

# 立即执行任务
python src/cli/main.py run-task <task_id>

# 执行工作流任务
python src/cli/main.py run-workflow <task_id>
```

#### 方式2: 直接运行主程序

```bash
python main.py
```

### 验证系统运行

1. **检查配置加载**：
   ```bash
   python src/cli/main.py status
   ```

2. **测试任务执行**：
   ```bash
   python src/cli/main.py run-task <task_id>
   ```

3. **查看执行结果**：
   - 检查 `outputs/` 目录下的输出文件
   - 查看 `states/` 目录下的状态文件
   - 检查 `logs/` 目录下的日志文件

### 系统目录结构

```
auto-coder/
├── src/                          # 源代码
│   ├── core/                     # 核心模块（配置管理、状态管理、工作流引擎）
│   ├── services/                 # 服务模块（AI、Git、通知服务）
│   ├── tasks/                    # 任务执行器
│   └── cli/                      # 命令行接口
├── config/                       # 配置文件
│   ├── global_config.yaml        # 全局配置
│   └── tasks/                    # 任务配置
├── workflows/                    # 工作流模板
│   ├── base/                     # 基础模板
│   ├── coding/                   # 编码任务模板
│   ├── review/                   # 审查任务模板
│   └── doc/                      # 文档任务模板
├── prompts/                      # AI提示词模板
│   ├── coding/                   # 编码任务提示词
│   ├── review/                   # 审查任务提示词
│   └── doc/                      # 文档任务提示词
├── outputs/                      # 输出文件
│   ├── reviews/                  # 审查报告
│   ├── docs/                     # 生成的文档
│   └── custom_tasks/             # 自定义任务结果
├── states/                       # 状态文件
├── logs/                         # 日志文件
├── archives/                     # 归档文件
└── test_system.py               # 系统测试脚本
```

## 🛠️ CLI命令使用

### 系统管理
```bash
# 查看系统状态
python src/cli/main.py status

# 查看系统配置摘要
python src/cli/main.py config-summary

# 重新加载配置
python src/cli/main.py reload-config

# 清理系统
python src/cli/main.py cleanup
```

### 任务管理
```bash
# 列出所有任务
python src/cli/main.py list-tasks

# 查看任务状态
python src/cli/main.py task-status <task_id>

# 立即执行任务
python src/cli/main.py run-task <task_id>

# 执行工作流任务
python src/cli/main.py run-workflow <task_id>

# 停止任务
python src/cli/main.py stop-task <task_id>

# 查看任务历史
python src/cli/main.py task-history <task_id>
```

### 工作流管理
```bash
# 列出工作流模板
python src/cli/main.py list-workflows

# 查看工作流状态
python src/cli/main.py workflow-status <task_id>

# 验证工作流配置
python src/cli/main.py validate-workflow <task_id>
```

### 其他命令
```bash
# 显示版本信息
python src/cli/main.py version

# 启用详细日志
python src/cli/main.py --verbose status

# 运行系统测试
python test_system.py
```

## 📁 目录结构

```
auto-coder/
├── src/                          # 源代码目录
│   ├── core/                     # 核心模块
│   ├── services/                 # 服务模块
│   ├── tasks/                    # 任务执行器
│   ├── cli/                      # CLI接口
│   └── utils/                    # 工具模块
├── config/                       # 配置文件目录
│   ├── global_config.yaml        # 全局配置
│   └── ...                       # 其他配置
├── tasks/                        # 任务配置目录
│   ├── example_coding_task.yaml  # 示例编码任务
│   ├── example_review_task.yaml  # 示例审查任务
│   └── ...                       # 其他任务配置
├── standards/                    # 编码规范目录
│   ├── java_coding_standards.md  # Java编码规范
│   ├── python_coding_standards.md # Python编码规范
│   └── ...                       # 其他规范
├── logs/                         # 日志目录
├── states/                       # 状态文件目录
├── archives/                     # 归档文件目录
├── outputs/                      # 输出文件目录
│   ├── reviews/                  # 审查报告
│   ├── docs/                     # 生成的文档
│   ├── requirement_reviews/      # 需求审查报告
│   └── custom_tasks/             # 自定义任务结果
├── main.py                       # 主程序入口
├── requirements.txt              # Python依赖
└── README.md                     # 项目说明
```

## ⚙️ 配置说明

### 全局配置 (config/global_config.yaml)

```yaml
# 系统基本配置
system:
  name: "自动化AI任务执行系统"
  version: "1.0.0"
  max_concurrent_tasks: 5

# AI服务配置
ai_services:
  claude:
    api_key: "${CLAUDE_API_KEY}"
    base_url: "https://api.anthropic.com"
    models:
      default: "claude-3-sonnet-20240229"
      coding: "claude-3-sonnet-20240229"
      review: "claude-3-sonnet-20240229"
  
  deepseek:
    api_key: "${DEEPSEEK_API_KEY}"
    base_url: "https://api.deepseek.com"
    models:
      default: "deepseek-chat"

# Git服务配置
git_services:
  github:
    token: "${GITHUB_TOKEN}"
    username: "${GITHUB_USERNAME}"
    base_url: "https://api.github.com"
  
  gitlab:
    token: "${GITLAB_TOKEN}"
    username: "${GITLAB_USERNAME}"
    base_url: "https://gitlab.com/api/v4"

# 通知服务配置
notifications:
  dingtalk:
    webhook_url: "${DINGTALK_WEBHOOK_URL}"
    secret: "${DINGTALK_SECRET}"
    at_users: ["@张三", "@李四"]
    at_all: false
```

### 任务配置示例

```yaml
# 编码任务配置
task_id: "my_coding_task"
type: "coding"
enabled: true
priority: 5

schedule:
  type: "cron"
  cron:
    minute: "0"
    hour: "9"
    day: "*"
    month: "*"
    day_of_week: "1-5"

coding:
  project_path: "./my_project"
  branch_name: "feature/ai-generated"
  prompt: "请生成一个用户登录验证函数"
  output_file: "auth.py"

ai:
  provider: "claude"
  model: "claude-3-sonnet-20240229"
  max_tokens: 2000
  temperature: 0.1
```

## 🔧 开发指南

### 添加新的任务类型

1. 在 `src/tasks/` 目录下创建新的执行器类
2. 继承 `TaskExecutor` 基类
3. 实现 `_execute_task` 方法
4. 在 `TaskExecutorFactory` 中注册新的执行器

### 扩展AI服务

1. 在 `src/services/` 目录下创建新的AI服务类
2. 继承 `AIService` 基类
3. 实现必要的方法
4. 在配置文件中添加新的服务配置

### 自定义通知渠道

1. 在 `src/services/` 目录下创建新的通知器类
2. 继承 `BaseNotifier` 基类
3. 实现 `send_notification` 方法
4. 在 `NotifyService` 中注册新的通知器

## 📊 监控和调试

### 日志系统

- 日志级别: INFO
- 日志保留: 30天
- 日志位置: `logs/` 目录
- 敏感信息自动脱敏

### 状态监控

- 任务执行状态实时跟踪
- 进度百分比更新
- 错误计数和重试统计
- 元数据记录

### 性能指标

- 任务执行时间统计
- 并发任务数量监控
- 资源使用情况跟踪
- 系统响应时间监控

## 🔒 安全特性

- API密钥通过环境变量管理
- 敏感信息自动脱敏
- 访问权限控制
- 操作日志记录

## 🚧 注意事项

1. **API密钥安全**: 请妥善保管AI服务和Git服务的API密钥
2. **网络环境**: 确保系统能够访问AI服务API和Git仓库
3. **资源限制**: 注意AI服务的调用频率和配额限制
4. **文件权限**: 确保系统有足够的文件读写权限

## 🤝 贡献指南

欢迎提交Issue和Pull Request来改进系统！

### 开发环境设置

```bash
# 克隆仓库
git clone <repository_url>
cd auto-coder

# 安装开发依赖
pip install -r requirements.txt

# 运行测试
pytest

# 代码格式化
black src/
flake8 src/
```

## 📄 许可证

本项目采用MIT许可证，详见LICENSE文件。

## 📞 联系方式

- 项目维护者: Auto Coder Team
- 邮箱: support@auto-coder.com
- 项目地址: [GitHub Repository]

---

**🎉 系统实现完成！** 

现在您可以：
1. 配置AI服务和Git服务
2. 创建任务配置文件
3. 启动系统并开始使用
4. 通过CLI工具管理任务

如有问题，请查看日志文件或提交Issue。
