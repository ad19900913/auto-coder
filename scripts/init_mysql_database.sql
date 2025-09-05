-- 自动化AI任务执行系统 - MySQL数据库初始化脚本
-- 版本: 1.0
-- 创建时间: 2025-01-20

-- 创建数据库
CREATE DATABASE IF NOT EXISTS `auto_coder` 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

-- 使用数据库
USE `auto_coder`;

-- 创建AI模型版本表
CREATE TABLE IF NOT EXISTS `model_versions` (
    `version_id` VARCHAR(255) PRIMARY KEY,
    `model_name` VARCHAR(255) NOT NULL,
    `model_type` VARCHAR(100) NOT NULL,
    `version` VARCHAR(100) NOT NULL,
    `provider` VARCHAR(100) NOT NULL,
    `api_key` TEXT,
    `endpoint` TEXT,
    `parameters` TEXT,
    `performance_metrics` TEXT,
    `created_at` DATETIME NOT NULL,
    `updated_at` DATETIME NOT NULL,
    `status` VARCHAR(50) NOT NULL,
    `usage_count` INT DEFAULT 0,
    `success_rate` DECIMAL(5,4) DEFAULT 0.0,
    `avg_response_time` DECIMAL(10,3) DEFAULT 0.0,
    `cost_per_request` DECIMAL(10,6) DEFAULT 0.0,
    INDEX `idx_model_type` (`model_type`),
    INDEX `idx_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 创建AI模型性能历史表
CREATE TABLE IF NOT EXISTS `model_performance` (
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
    `model_version_id` VARCHAR(255) NOT NULL,
    `timestamp` DATETIME NOT NULL,
    `response_time` DECIMAL(10,3) NOT NULL,
    `success` TINYINT NOT NULL,
    `cost` DECIMAL(10,6) NOT NULL,
    `tokens_used` INT NOT NULL,
    `error_message` TEXT,
    INDEX `idx_model_version_id` (`model_version_id`),
    INDEX `idx_timestamp` (`timestamp`),
    FOREIGN KEY (`model_version_id`) REFERENCES `model_versions` (`version_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 创建任务指标表
CREATE TABLE IF NOT EXISTS `task_metrics` (
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
    `task_id` VARCHAR(255) NOT NULL,
    `task_type` VARCHAR(100) NOT NULL,
    `duration` DECIMAL(10,3) NOT NULL,
    `success` TINYINT NOT NULL,
    `error_count` INT NOT NULL,
    `retry_count` INT NOT NULL,
    `resource_usage` TEXT NOT NULL,
    `timestamp` DATETIME NOT NULL,
    `features` TEXT NOT NULL,
    `created_at` DATETIME NOT NULL,
    INDEX `idx_task_id` (`task_id`),
    INDEX `idx_timestamp` (`timestamp`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 创建预测结果表
CREATE TABLE IF NOT EXISTS `predictions` (
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
    `task_id` VARCHAR(255) NOT NULL,
    `predicted_duration` DECIMAL(10,3) NOT NULL,
    `success_probability` DECIMAL(5,4) NOT NULL,
    `confidence` DECIMAL(5,4) NOT NULL,
    `risk_factors` TEXT NOT NULL,
    `recommendations` TEXT NOT NULL,
    `actual_duration` DECIMAL(10,3),
    `actual_success` TINYINT,
    `created_at` DATETIME NOT NULL,
    INDEX `idx_task_id` (`task_id`),
    INDEX `idx_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 创建异常检测结果表
CREATE TABLE IF NOT EXISTS `anomalies` (
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
    `task_id` VARCHAR(255) NOT NULL,
    `is_anomaly` TINYINT NOT NULL,
    `anomaly_score` DECIMAL(10,6) NOT NULL,
    `anomaly_type` VARCHAR(100) NOT NULL,
    `severity` VARCHAR(50) NOT NULL,
    `explanation` TEXT NOT NULL,
    `created_at` DATETIME NOT NULL,
    INDEX `idx_task_id` (`task_id`),
    INDEX `idx_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 创建A/B测试配置表
CREATE TABLE IF NOT EXISTS `ab_tests` (
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
    `test_id` VARCHAR(255) UNIQUE NOT NULL,
    `name` VARCHAR(255) NOT NULL,
    `description` TEXT NOT NULL,
    `variants` TEXT NOT NULL,
    `traffic_split` TEXT NOT NULL,
    `metrics` TEXT NOT NULL,
    `duration_days` INT NOT NULL,
    `start_time` DATETIME NOT NULL,
    `end_time` DATETIME NOT NULL,
    `status` VARCHAR(50) NOT NULL,
    `created_at` DATETIME NOT NULL,
    INDEX `idx_test_id` (`test_id`),
    INDEX `idx_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 创建A/B测试结果表
CREATE TABLE IF NOT EXISTS `ab_test_results` (
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
    `test_id` VARCHAR(255) NOT NULL,
    `variant` VARCHAR(100) NOT NULL,
    `metrics` TEXT NOT NULL,
    `sample_size` INT NOT NULL,
    `confidence_interval` TEXT NOT NULL,
    `p_value` DECIMAL(10,6) NOT NULL,
    `is_significant` TINYINT NOT NULL,
    `winner` VARCHAR(100),
    `created_at` DATETIME NOT NULL,
    INDEX `idx_test_id` (`test_id`),
    FOREIGN KEY (`test_id`) REFERENCES `ab_tests` (`test_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 创建用户和权限表（如果需要）
CREATE TABLE IF NOT EXISTS `users` (
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
    `username` VARCHAR(100) UNIQUE NOT NULL,
    `email` VARCHAR(255) UNIQUE NOT NULL,
    `password_hash` VARCHAR(255) NOT NULL,
    `role` VARCHAR(50) DEFAULT 'user',
    `is_active` TINYINT DEFAULT 1,
    `created_at` DATETIME NOT NULL,
    `updated_at` DATETIME NOT NULL,
    INDEX `idx_username` (`username`),
    INDEX `idx_email` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 创建系统配置表
CREATE TABLE IF NOT EXISTS `system_config` (
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
    `config_key` VARCHAR(255) UNIQUE NOT NULL,
    `config_value` TEXT NOT NULL,
    `description` TEXT,
    `created_at` DATETIME NOT NULL,
    `updated_at` DATETIME NOT NULL,
    INDEX `idx_config_key` (`config_key`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 插入默认系统配置
INSERT IGNORE INTO `system_config` (`config_key`, `config_value`, `description`, `created_at`, `updated_at`) VALUES
('system_version', '1.0.0', '系统版本号', NOW(), NOW()),
('database_version', '1.0.0', '数据库版本号', NOW(), NOW()),
('last_cleanup', '', '最后清理时间', NOW(), NOW());

-- 显示创建的表
SHOW TABLES;

-- 显示数据库信息
SELECT 
    TABLE_NAME,
    TABLE_ROWS,
    DATA_LENGTH,
    INDEX_LENGTH,
    CREATE_TIME
FROM information_schema.TABLES 
WHERE TABLE_SCHEMA = 'auto_coder'
ORDER BY TABLE_NAME;
