---
title: "Java编码规范 v1.0"
version: "1.0"
last_updated: "2025-01-20"
language: "java"
framework: "spring-boot"
alwaysApply: true
---

# Java编码规范 v1.0

## 命名规范

### 类名
- 使用PascalCase，如 `UserService`、`OrderController`
- 接口名可以不加前缀，如 `UserService` 而不是 `IUserService`
- 抽象类名以 `Abstract` 开头，如 `AbstractBaseService`

### 方法名
- 使用camelCase，如 `getUserById`、`createOrder`
- 动词开头，表达动作含义
- 布尔方法使用 `is`、`has`、`can` 等前缀

### 变量名
- 使用camelCase，如 `userName`、`orderList`
- 常量使用UPPER_SNAKE_CASE，如 `MAX_RETRY_COUNT`
- 避免使用单字母变量名（循环计数器除外）

### 包名
- 使用小写字母，如 `com.example.user`
- 避免使用下划线或连字符

## 代码结构

### 类成员顺序
1. 静态常量
2. 实例变量
3. 构造方法
4. 公共方法
5. 受保护方法
6. 私有方法

### 方法设计
- 单个方法不超过50行
- 方法参数不超过5个
- 单一职责原则：一个方法只做一件事

### 类设计
- 单个类不超过500行
- 遵循单一职责原则
- 优先使用组合而非继承

## 异常处理

### 异常捕获
- 使用具体的异常类型，避免捕获通用Exception
- 记录详细的错误日志，包含上下文信息
- 对外接口返回统一的错误响应格式

### 异常抛出
- 检查异常转换为运行时异常
- 提供有意义的异常消息
- 包含必要的上下文信息

## 性能规范

### 集合使用
- 初始化集合时指定容量
- 优先使用 `ArrayList` 而非 `LinkedList`
- 使用 `HashMap` 而非 `Hashtable`

### 字符串处理
- 使用 `StringBuilder` 进行字符串拼接
- 避免在循环中创建字符串对象
- 优先使用字符串常量池

### 数据库操作
- 避免在循环中进行数据库查询
- 使用批量操作减少数据库交互
- 合理使用数据库连接池

## 红线规范

### 禁止使用
- 禁止使用 `System.out.println()` 输出日志
- 禁止在 `finally` 块中 `return`
- 禁止使用 `Thread.sleep()` 进行业务逻辑控制
- 禁止使用 `new Date()` 获取当前时间

### 必须遵循
- 必须使用日志框架记录日志
- 必须处理所有检查异常
- 必须验证输入参数
- 必须释放资源（使用try-with-resources）

## 日志规范

### 日志级别
- ERROR：系统错误，需要立即处理
- WARN：警告信息，可能存在问题
- INFO：一般信息，记录重要操作
- DEBUG：调试信息，开发时使用

### 日志内容
- 包含操作类型和结果
- 包含关键参数信息
- 包含执行时间（重要操作）
- 包含错误堆栈（异常情况）

## 测试规范

### 单元测试
- 测试覆盖率不低于80%
- 每个公共方法都要有测试
- 使用有意义的测试方法名
- 测试数据要独立，避免相互影响

### 集成测试
- 测试组件间的协作
- 使用测试数据库
- 测试完成后清理数据

# server 项目的 Cursor AI 规则 (基于阿里巴巴 Java 编码规范)

## 通用 Java 开发规范

- **命名规范：**
  - 类名：UpperCamelCase (例如：`UserController`)。
  - 方法名：lowerCamelCase (例如：`getUserById`, `calculateTotalPrice`)。
  - 常量名：ALL_CAPS_WITH_UNDERSCORES (例如：`MAX_RETRY_COUNT`)。
  - 变量名：lowerCamelCase。
  - 包名：all_lowercase_with_dots (例如：`com.example.project.service`)。
  - 接口命名: IXXXXService (例如：IUserService)
  - 接口实现类命名： XXXXServiceImpl （例如：UserServiceImpl）

- **注释规范：**
  - 为所有公共类和方法编写 Javadoc。
  - 解释复杂逻辑或非显而易见的代码段。
  - 避免仅仅复述代码的冗余注释。

- **代码格式：**
  - 使用 4 个空格进行缩进（不要使用制表符）。
  - 限制行长度为 120 个字符。
  - 确保一致的大括号风格 (例如：K&R 风格)。

- **异常处理：**
  - 捕获异常时要具体。除非绝对必要，否则避免捕获通用的 `Exception` 或 `Throwable`。
  - 记录异常时提供足够的上下文信息。
  - 不要忽略异常（避免空的 catch 块）。
  - 在 `finally` 块中清理资源，或使用 try-with-resources 语句。

- **并发处理：**
  - 处理共享可变状态时，注意线程安全。
  - 在需要时使用适当的同步机制（如 `synchronized`, `Lock`,并发集合）。
  - 避免使用 `Thread.sleep()` 进行轮询或等待；应使用恰当的 wait/notify 或更高级别的并发工具。

- **面向对象编程：**
  - 遵循 SOLID 原则。保持高内聚性和低耦合性.
  - 在适当情况下，优先使用组合而非继承。
  - 封装内部状态。

- **魔法数字：**
  - 避免使用魔法数字；使用命名常量代替。优先使用项目中的常量或者枚举等

- **Null 值检查：**
  - 勤勉地执行 Null 检查，特别是对于方法参数和外部调用的返回值。
  - 当值的缺失是正常情况时，考虑使用 `Optional` 作为返回类型。
  - 禁止为集合或数组返回 `null`；应返回空集合/数组。

- **Equals 和 HashCode：**
  - 如果对象要在基于哈希的集合中使用，务必一致地覆盖 `equals()` 和 `hashCode()`。

- **日志记录：**
  - 使用标准日志框架 (例如 SLF4J 配合 Logback 或 Log4j2)。
  - 使用适当的日志级别 (DEBUG, INFO, WARN, ERROR)。
  - 不要记录敏感信息。
  - 日志打印信息只能是英文，不能出现中文。

## Spring Boot 特定规范 (@2.3.12.RELEASE)

- **组件扫描：**
  - 如果关注性能，优先使用显式的组件扫描路径，而不是默认的广泛扫描。

- **配置：**
  - 使用 `@ConfigurationProperties` 实现类型安全的配置。
  - 使用 `application.properties` 或 `application.yml` 进行外部化配置。

- **依赖注入：**
  - 对于强制依赖项，优先使用构造函数注入。
  - 谨慎使用 `@Autowired`，并清晰记录其用途。

- **REST 控制器：**
  - 使用特定的 HTTP 方法 (`@GetMapping`, `@PostMapping` 等)。
  - 返回恰当的 HTTP 状态码。
  - 清晰定义请求和响应的 DTO。
  - 使用 `@RestControllerAdvice` 进行全局异常处理。

- **服务层：**
  - 业务逻辑应位于服务类中。
  - 使用 `@Service` 注解。
  - 保持服务专注和内聚。

## MyBatis 特定规范

- **Mapper 接口：**
  - 定义 Mapper 接口以确保类型安全。

- **XML Mapper 文件：**
  - 逻辑地组织 XML Mapper 文件。
  - 使用 `<sql>`片段实现可复用的 SQL 代码段。
  - 避免使用 `select *`；明确列出所有列。
  - 谨慎使用动态 SQL 以防止 SQL 注入 (参数使用 `#{}`)。

- **结果映射 (Result Maps)：**
  - 对于数据库列和 Java 对象属性之间的复杂映射，使用 `<resultMap>`。

- **事务管理：**
  - 在服务层使用 Spring 的声明式事务管理 (`@Transactional`) 来管理事务。

## MySQL 特定规范

- **数据库表结构设计：**
  - 选择合适的数据类型。
  - 定义主键和外键。
  - 明智地使用索引以优化查询性能。避免过度索引。

- **查询语句：**
  - 编写高效的 SQL 查询。对复杂查询使用 `EXPLAIN` 分析查询计划。
  - 避免 N+1 查询问题；使用 JOIN 或批量获取。

## 数据序列化 (Fastjson)

- **安全：**
  - 注意 Fastjson 的安全漏洞。保持库版本更新。
  - 如果可能，启用 `SafeMode`。
  - 除非严格需要并完全理解其影响，否则指定 `autoTypeSupport = false`。

- **日期格式化：**
  - 使用 `@JSONField(format = "yyyy-MM-dd HH:mm:ss")` 进行一致的日期格式化。

## Lombok 使用规范

- **代码清晰度：**
  - 明智地使用 Lombok 注解 (`@Data`, `@Getter`, `@Setter`, `@NoArgsConstructor`, `@AllArgsConstructor`, `@Builder`, `@Slf4j`) 以减少样板代码。
  - 确保生成的代码易于理解，并且不会掩盖重要逻辑。
  - 注意 `@Data` 等注解的潜在影响 (例如：自动生成 `equals`, `hashCode`, `toString`)。

## 阿里巴巴规范通用最佳实践 (摘要)

- **可读性：** 代码应易于阅读和理解。
- **可维护性：** 代码应易于修改和扩展。
- **可测试性：** 代码设计应便于单元测试。
- **安全性：** 注意常见的安全漏洞 (SQL 注入, XSS, CSRF 等) 并采取措施加以防范。
- **性能：** 编写高效的代码，并注意资源使用。
- **简洁性：** 优先选择简单的解决方案而非复杂的 (KISS 原则)。
- **避免使用已废弃的 API。**
- **正确处理资源关闭。**

## 项目当前统一规范
- 接口响应体采用com.streamax.base.common.model.Result封装
- 错误码采用com.streamax.base.common.constant.error.exception.BusinessException，例如：throw new BusinessException(BaseErrorCode.PARAM_ERR);
- service接口采用IXXXService命名，实现类为XXXServiceImpl

## AI 交互指南

- 在生成新代码或修改现有代码时，遵守上述规则。
- 优先考虑代码的清晰性、可维护性以及对阿里巴巴 Java 编码规范的遵守。
- 对于新功能，考虑 `server` 项目中现有的模式和约定。
- 如果不确定某个特定规则或最佳实践，请求澄清或参考阿里巴巴 Java 编码规范文档。
- 在建议数据库表结构更改或复杂查询时，解释其原因和潜在的性能影响。
- 确保所有新的公共 API (类、方法) 都用 Javadoc 进行文档化。

