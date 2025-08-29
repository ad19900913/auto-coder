# 自动化AI任务执行系统

🚀 一个基于Python的自动化AI任务执行系统，支持多种任务类型，包括代码生成、代码审查、文档生成、需求审查和自定义任务。

## ✨ 系统特性

- **🤖 多AI服务支持**: 集成Claude、DeepSeek等主流AI服务
- **📅 灵活调度**: 支持crontab表达式、间隔调度、指定时间调度
- **🔧 多任务类型**: 编码、审查、文档、需求审查、自定义任务
- **📊 状态管理**: 完整的任务状态跟踪和持久化
- **🔄 并发执行**: 支持多任务并发执行，可配置最大工作线程数
- **❌ 错误处理**: 智能重试机制，指数退避策略
- **🔔 通知系统**: 支持钉钉机器人、邮件、Webhook等多种通知方式
- **💾 Git集成**: 支持GitHub、GitLab平台操作
- **📝 进度跟踪**: 实时任务进度更新和状态监控
- **🖥️ CLI管理**: 完整的命令行管理工具

## 🏗️ 系统架构

```
自动化AI任务执行系统
├── 核心模块 (src/core/)
│   ├── 配置管理器 (ConfigManager)
│   ├── 状态管理器 (StateManager)
│   ├── 状态文件管理器 (StateFileManager)
│   ├── 任务调度器 (TaskScheduler)
│   ├── 任务执行器基类 (TaskExecutor)
│   ├── 任务执行器工厂 (TaskExecutorFactory)
│   └── 任务管理器 (TaskManager)
├── 服务模块 (src/services/)
│   ├── 通知服务 (NotifyService)
│   ├── AI服务 (AIService)
│   └── Git服务 (GitService)
├── 任务执行器 (src/tasks/)
│   ├── 编码任务执行器 (CodingTaskExecutor)
│   ├── 代码审查任务执行器 (ReviewTaskExecutor)
│   ├── 文档生成任务执行器 (DocTaskExecutor)
│   ├── 需求审查任务执行器 (RequirementReviewTaskExecutor)
│   └── 自定义任务执行器 (CustomTaskExecutor)
├── CLI接口 (src/cli/)
│   └── 命令行管理工具
└── 配置和文档
    ├── 全局配置文件
    ├── 任务配置文件
    ├── 编码规范模板
    └── 系统设计文档
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
pip install -r requirements.txt
```

### 配置系统

1. **配置AI服务**
   - 编辑 `config/global_config.yaml`
   - 设置Claude、DeepSeek等AI服务的API密钥和配置

2. **配置Git服务**
   - 设置GitHub、GitLab的访问令牌和仓库信息

3. **配置通知服务**
   - 设置钉钉机器人的Webhook URL和密钥

4. **创建任务配置**
   - 在 `tasks/` 目录下创建任务配置文件
   - 参考示例配置文件进行配置

### 启动系统

#### 方式1: 直接运行主程序
```bash
python main.py
```

#### 方式2: 使用CLI工具
```bash
# 启动系统
python src/cli/main.py start-system

# 查看系统状态
python src/cli/main.py status

# 列出所有任务
python src/cli/main.py list-tasks
```

## 🛠️ CLI命令使用

### 系统管理
```bash
# 启动系统
python src/cli/main.py start-system

# 停止系统
python src/cli/main.py stop-system

# 查看系统状态
python src/cli/main.py status

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

# 停止任务
python src/cli/main.py stop-task <task_id>
```

### 其他命令
```bash
# 显示版本信息
python src/cli/main.py version

# 启用详细日志
python src/cli/main.py --verbose status
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
