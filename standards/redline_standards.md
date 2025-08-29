---
title: "编码红线规范 v1.0"
version: "1.0"
last_updated: "2025-01-20"
language: "all"
framework: "cross-platform"
---

## 🚨 编码红线 - 绝对禁止

### 安全红线

#### 1. 绝对禁止硬编码敏感信息
```python
# ❌ 绝对禁止
password = "admin123"
api_key = "sk-1234567890abcdef"
database_url = "mysql://user:pass@localhost/db"

# ✅ 正确做法
password = os.getenv("DB_PASSWORD")
api_key = os.getenv("OPENAI_API_KEY")
database_url = os.getenv("DATABASE_URL")
```

#### 2. 绝对禁止SQL注入
```python
# ❌ 绝对禁止
query = f"SELECT * FROM users WHERE id = {user_id}"

# ✅ 正确做法
query = "SELECT * FROM users WHERE id = %s"
cursor.execute(query, (user_id,))
```

#### 3. 绝对禁止XSS攻击
```javascript
// ❌ 绝对禁止
element.innerHTML = userInput;

// ✅ 正确做法
element.textContent = userInput;
// 或者使用安全的HTML净化库
```

#### 4. 绝对禁止命令注入
```python
# ❌ 绝对禁止
os.system(f"rm -rf {user_input}")

# ✅ 正确做法
# 使用安全的文件操作API
import shutil
shutil.rmtree(safe_path)
```

### 性能红线

#### 5. 绝对禁止N+1查询问题
```python
# ❌ 绝对禁止
for user in users:
    posts = Post.objects.filter(user=user)  # 每次循环都查询数据库

# ✅ 正确做法
users = User.objects.prefetch_related('posts').all()
for user in users:
    posts = user.posts.all()  # 使用预加载的数据
```

#### 6. 绝对禁止无限循环
```python
# ❌ 绝对禁止
while True:
    process_data()

# ✅ 正确做法
max_iterations = 1000
iteration = 0
while iteration < max_iterations:
    process_data()
    iteration += 1
```

#### 7. 绝对禁止内存泄漏
```python
# ❌ 绝对禁止
class DataProcessor:
    def __init__(self):
        self.data = []
    
    def add_data(self, item):
        self.data.append(item)  # 无限增长，从不清理

# ✅ 正确做法
class DataProcessor:
    def __init__(self, max_size=1000):
        self.data = []
        self.max_size = max_size
    
    def add_data(self, item):
        if len(self.data) >= self.max_size:
            self.data.pop(0)  # 保持固定大小
        self.data.append(item)
```

### 代码质量红线

#### 8. 绝对禁止魔法数字
```python
# ❌ 绝对禁止
if user.age > 18:
    allow_access = True

# ✅ 正确做法
MINIMUM_AGE = 18
if user.age > MINIMUM_AGE:
    allow_access = True
```

#### 9. 绝对禁止深层嵌套
```python
# ❌ 绝对禁止（超过3层嵌套）
if condition1:
    if condition2:
        if condition3:
            if condition4:
                if condition5:
                    do_something()

# ✅ 正确做法
def should_do_something(condition1, condition2, condition3, condition4, condition5):
    return all([condition1, condition2, condition3, condition4, condition5])

if should_do_something(condition1, condition2, condition3, condition4, condition5):
    do_something()
```

#### 10. 绝对禁止空异常处理
```python
# ❌ 绝对禁止
try:
    risky_operation()
except Exception:
    pass  # 静默忽略所有异常

# ✅ 正确做法
try:
    risky_operation()
except SpecificException as e:
    logger.error(f"操作失败: {e}")
    # 处理特定异常
except Exception as e:
    logger.error(f"未知错误: {e}")
    # 记录并上报未知异常
```

### 并发安全红线

#### 11. 绝对禁止竞态条件
```python
# ❌ 绝对禁止
class Counter:
    def __init__(self):
        self.value = 0
    
    def increment(self):
        self.value += 1  # 非原子操作

# ✅ 正确做法
import threading

class Counter:
    def __init__(self):
        self.value = 0
        self.lock = threading.Lock()
    
    def increment(self):
        with self.lock:
            self.value += 1
```

#### 12. 绝对禁止死锁
```python
# ❌ 绝对禁止
def transfer_money(account1, account2, amount):
    with account1.lock:
        with account2.lock:  # 可能导致死锁
            # 转账逻辑

# ✅ 正确做法
def transfer_money(account1, account2, amount):
    # 按固定顺序获取锁，避免死锁
    first, second = sorted([account1, account2], key=lambda x: x.id)
    with first.lock:
        with second.lock:
            # 转账逻辑
```

### 错误处理红线

#### 13. 绝对禁止吞掉异常
```python
# ❌ 绝对禁止
def process_data():
    try:
        return complex_operation()
    except Exception:
        return None  # 吞掉异常，返回None

# ✅ 正确做法
def process_data():
    try:
        return complex_operation()
    except Exception as e:
        logger.error(f"数据处理失败: {e}")
        raise  # 重新抛出异常，让调用者知道失败
```

#### 14. 绝对禁止忽略返回值
```python
# ❌ 绝对禁止
def create_user():
    user = User.objects.create(name="John")
    # 忽略创建结果，不知道是否成功

# ✅ 正确做法
def create_user():
    try:
        user = User.objects.create(name="John")
        logger.info(f"用户创建成功: {user.id}")
        return user
    except Exception as e:
        logger.error(f"用户创建失败: {e}")
        raise
```

### 日志记录红线

#### 15. 绝对禁止记录敏感信息
```python
# ❌ 绝对禁止
logger.info(f"用户登录成功: {user.password}")

# ✅ 正确做法
logger.info(f"用户登录成功: {user.username}")
```

#### 16. 绝对禁止使用print调试
```python
# ❌ 绝对禁止
def process_order(order):
    print(f"处理订单: {order.id}")  # 生产环境不应该有print
    # 处理逻辑

# ✅ 正确做法
def process_order(order):
    logger.info(f"处理订单: {order.id}")
    # 处理逻辑
```

### 配置管理红线

#### 17. 绝对禁止硬编码配置
```python
# ❌ 绝对禁止
DATABASE_URL = "mysql://localhost:3306/production_db"

# ✅ 正确做法
DATABASE_URL = os.getenv("DATABASE_URL", "mysql://localhost:3306/dev_db")
```

#### 18. 绝对禁止环境相关配置
```python
# ❌ 绝对禁止
if os.path.exists("/etc/production"):
    DEBUG = False
else:
    DEBUG = True

# ✅ 正确做法
DEBUG = os.getenv("DEBUG", "false").lower() == "true"
```

## 🔍 红线检查清单

### 代码提交前检查
- [ ] 没有硬编码的敏感信息
- [ ] 没有SQL注入风险
- [ ] 没有XSS攻击风险
- [ ] 没有命令注入风险
- [ ] 没有N+1查询问题
- [ ] 没有无限循环风险
- [ ] 没有内存泄漏风险
- [ ] 没有魔法数字
- [ ] 嵌套层级不超过3层
- [ ] 异常处理完整
- [ ] 没有竞态条件
- [ ] 没有死锁风险
- [ ] 没有吞掉异常
- [ ] 没有忽略返回值
- [ ] 没有记录敏感信息
- [ ] 没有print调试语句
- [ ] 没有硬编码配置
- [ ] 没有环境相关配置

### 代码审查要点
- 重点关注安全相关的代码
- 检查异常处理是否完整
- 验证并发安全性
- 确认配置管理正确
- 检查日志记录规范

## 📚 红线规范执行

### 自动化检查
- 使用ESLint、Pylint等静态分析工具
- 配置安全扫描工具
- 实施自动化测试覆盖
- 使用代码质量门禁

### 人工审查
- 强制代码审查流程
- 重点关注红线区域
- 定期进行安全培训
- 建立红线违规报告机制

### 违规处理
- 立即停止违规代码合并
- 要求开发者修复问题
- 记录违规情况
- 提供修复指导

## 🎯 红线规范目标

通过严格执行这些红线规范，我们致力于：
- 确保代码安全性
- 提高系统性能
- 保证代码质量
- 减少生产事故
- 提升开发效率
- 建立良好的编码习惯

记住：**红线就是底线，绝对不能触碰！**
