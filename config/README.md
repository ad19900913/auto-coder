# 配置文件目录

本目录包含AI自动化任务执行系统的核心配置文件。

## 文件说明

### 📋 核心配置文件

- **[global_config.yaml](./global_config.yaml)** - **全局配置文件**
  - 系统基础配置（名称、版本、并发任务数）
  - AI服务配置（OpenAI、Anthropic等）
  - Git平台配置（GitHub、GitLab等）
  - 通知服务配置（邮件、Slack等）
  - 任务依赖管理配置
  - 配置验证设置
  - 智能任务生成配置
  - AI模型管理配置
  - 多模态AI支持配置
  - 机器学习集成配置

- **[mcp_config.yaml](./mcp_config.yaml)** - **MCP配置文件**
  - Model Context Protocol配置
  - MCP服务器设置
  - 工具集成配置
  - 连接参数设置

## 配置说明

### 环境变量
系统支持通过环境变量覆盖配置文件中的敏感信息：

```bash
# AI服务API密钥
export OPENAI_API_KEY="your-openai-api-key"
export ANTHROPIC_API_KEY="your-anthropic-api-key"

# Git平台令牌
export GITHUB_TOKEN="your-github-token"
export GITLAB_TOKEN="your-gitlab-token"

# 邮件服务
export EMAIL_USERNAME="your-email@example.com"
export EMAIL_PASSWORD="your-email-password"
```

### 配置验证
系统会自动验证配置文件的正确性：
- 类型验证：检查字段类型是否正确
- 值范围验证：检查配置值是否在合理范围内
- 结构验证：验证配置文件的整体结构
- 字段验证：检查必需字段和未知字段

### 配置优先级
1. 环境变量（最高优先级）
2. 配置文件中的值
3. 系统默认值（最低优先级）

## 使用指南

### 1. 初始配置
1. 复制配置文件模板
2. 根据实际需求修改配置
3. 设置必要的环境变量
4. 运行配置验证

### 2. 配置更新
- 修改配置文件后，系统会自动重新加载
- 支持热更新，无需重启系统
- 配置变更会记录在日志中

### 3. 配置备份
- 建议定期备份配置文件
- 将配置文件纳入版本控制
- 敏感信息使用环境变量

## 注意事项

- **安全性**：不要在配置文件中硬编码敏感信息
- **验证**：修改配置后要验证配置的正确性
- **备份**：重要配置修改前要备份原文件
- **文档**：配置变更要更新相关文档

## 精简说明

本目录已精简，移除了以下不必要的文件：
- 各种示例配置文件（功能已在系统功能完整文档中说明）
- 增强版配置文件（功能已合并到主配置文件）
- 任务示例文件（使用说明已在文档中提供）

保留的文件都是系统运行必需的核心配置文件。
