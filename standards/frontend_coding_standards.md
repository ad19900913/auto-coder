---
title: "前端编码规范 v1.0"
version: "1.0"
last_updated: "2025-01-20"
language: "frontend"
framework: "react-vue-angular"
---

## 命名规范

### 文件命名
- 组件文件：使用PascalCase，如 `UserProfile.tsx`、`ProductCard.vue`
- 工具文件：使用camelCase，如 `apiUtils.ts`、`dateHelper.js`
- 样式文件：使用kebab-case，如 `user-profile.css`、`product-card.scss`

### 变量命名
- 常量：使用UPPER_SNAKE_CASE，如 `MAX_RETRY_COUNT`、`API_BASE_URL`
- 变量：使用camelCase，如 `userName`、`productList`
- 布尔值：使用is/has/can前缀，如 `isLoading`、`hasPermission`、`canEdit`

### 组件命名
- React组件：使用PascalCase，如 `UserProfile`、`ProductCard`
- Vue组件：使用PascalCase，如 `UserProfile`、`ProductCard`
- Angular组件：使用PascalCase，如 `UserProfile`、`ProductCard`

## 代码结构

### 组件结构
```typescript
// React组件标准结构
import React, { useState, useEffect } from 'react';
import './UserProfile.css';

interface UserProfileProps {
  userId: string;
  onUpdate?: (user: User) => void;
}

export const UserProfile: React.FC<UserProfileProps> = ({ userId, onUpdate }) => {
  // 1. 状态定义
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(false);
  
  // 2. 副作用处理
  useEffect(() => {
    fetchUser(userId);
  }, [userId]);
  
  // 3. 事件处理函数
  const handleUpdate = async (userData: Partial<User>) => {
    // 实现逻辑
  };
  
  // 4. 渲染函数
  if (loading) return <div>加载中...</div>;
  if (!user) return <div>用户不存在</div>;
  
  return (
    <div className="user-profile">
      {/* JSX内容 */}
    </div>
  );
};
```

### 文件组织
- 每个组件一个文件
- 相关组件放在同一目录
- 工具函数单独提取到utils目录
- 类型定义放在types目录

## 性能规范

### React性能优化
- 使用React.memo包装纯组件
- 使用useCallback和useMemo优化函数和计算
- 避免在render中创建对象和函数
- 合理使用React.lazy进行代码分割

### Vue性能优化
- 使用v-show替代v-if（频繁切换时）
- 合理使用computed和watch
- 避免在模板中使用复杂表达式
- 使用keep-alive缓存组件

### 通用优化
- 图片懒加载
- 路由懒加载
- 合理使用防抖和节流
- 避免不必要的DOM操作

## 红线规范

### 禁止行为
- 禁止在组件中直接操作DOM（除了ref）
- 禁止在render函数中调用API
- 禁止在useEffect中缺少依赖数组
- 禁止使用内联样式对象
- 禁止在循环中使用key={index}

### 必须遵循
- 必须处理异步操作的错误状态
- 必须为表单输入添加适当的验证
- 必须为可访问性添加必要的属性
- 必须处理组件的加载和错误状态

## 测试规范

### 单元测试
- 每个组件都要有对应的测试文件
- 测试覆盖率不低于80%
- 测试用例要覆盖正常流程和异常情况

### 集成测试
- 测试组件间的交互
- 测试与API的集成
- 测试用户操作流程

## 代码质量

### ESLint规则
- 使用严格的ESLint配置
- 禁止使用console.log（生产环境）
- 强制使用TypeScript严格模式
- 强制使用函数式编程原则

### 代码审查要点
- 组件是否过于复杂（超过200行）
- 是否有重复代码
- 是否有性能问题
- 是否有可访问性问题
