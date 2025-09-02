#!/bin/bash

# 自动化AI任务执行系统 - 智能Tab补全脚本
# 动态读取配置文件中的任务列表

echo "🚀 设置自动化AI任务执行系统的智能Tab补全..."

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "📁 脚本目录: $SCRIPT_DIR"

# 创建智能补全函数
create_smart_completion_function() {
    cat > /tmp/auto_coder_smart_completion.sh << 'EOF'
# 自动化AI任务执行系统 - 智能Tab补全函数
_auto_coder_smart_completion() {
    local cur prev opts cmds
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"
    
    # 主要命令列表
    cmds="status task-status run-task execute-workflow stop-task list-tasks start-system stop-system cleanup config-summary version"
    
    # 动态获取任务列表的函数
    get_task_ids() {
        local config_dir="./config"
        local task_ids=""
        
        # 检查配置文件目录
        if [[ -d "$config_dir/tasks" ]]; then
            # 读取所有yaml文件并提取task_id
            for file in "$config_dir/tasks"/*.yaml; do
                if [[ -f "$file" ]]; then
                    # 使用grep提取task_id（简单方法）
                    local task_id=$(grep -E "^task_id:" "$file" | head -1 | sed 's/task_id:[[:space:]]*"\([^"]*\)"/\1/')
                    if [[ -n "$task_id" ]]; then
                        task_ids="$task_ids $task_id"
                    fi
                fi
            done
        fi
        
        echo "$task_ids"
    }
    
    # 如果当前是第一个参数，显示所有命令
    if [[ $COMP_CWORD -eq 1 ]]; then
        COMPREPLY=( $(compgen -W "${cmds}" -- "${cur}") )
        return 0
    fi
    
    # 根据前一个参数提供不同的补全
    case "${prev}" in
        task-status|run-task|execute-workflow|stop-task)
            # 动态获取任务ID列表
            local task_ids=$(get_task_ids)
            if [[ -n "$task_ids" ]]; then
                COMPREPLY=( $(compgen -W "${task_ids}" -- "${cur}") )
            else
                # 如果无法获取，使用默认列表
                local default_tasks="auto-webhook-tool doc_task_example review_task_example"
                COMPREPLY=( $(compgen -W "${default_tasks}" -- "${cur}") )
            fi
            ;;
        --config|-c)
            # 配置文件目录补全
            COMPREPLY=( $(compgen -d -- "${cur}") )
            ;;
        --verbose|-v)
            # 布尔标志补全
            COMPREPLY=( $(compgen -W "true false" -- "${cur}") )
            ;;
        *)
            # 其他情况，显示所有命令
            COMPREPLY=( $(compgen -W "${cmds}" -- "${cur}") )
            ;;
    esac
}

# 注册补全函数
complete -F _auto_coder_smart_completion python
complete -F _auto_coder_smart_completion py

# 为特定命令创建别名以简化使用
alias auto-coder="python src/cli/main.py"
alias auto-coder-py="py src/cli/main.py"

# 为别名也注册补全
complete -F _auto_coder_smart_completion auto-coder
complete -F _auto_coder_smart_completion auto-coder-py
EOF

    echo "✅ 智能补全函数已创建"
}

# 设置补全
setup_smart_completion() {
    # 创建智能补全函数
    create_smart_completion_function
    
    # 加载补全函数
    source /tmp/auto_coder_smart_completion.sh
    
    # 添加到bashrc（如果存在）
    if [[ -f ~/.bashrc ]]; then
        # 检查是否已经添加过
        if ! grep -q "auto_coder_smart_completion" ~/.bashrc; then
            echo "" >> ~/.bashrc
            echo "# 自动化AI任务执行系统 - 智能Tab补全" >> ~/.bashrc
            echo "source /tmp/auto_coder_smart_completion.sh" >> ~/.bashrc
            echo "✅ 已添加到 ~/.bashrc"
        else
            echo "ℹ️  智能补全配置已存在于 ~/.bashrc"
        fi
    else
        echo "⚠️  未找到 ~/.bashrc，请手动添加补全配置"
    fi
    
    echo "✅ 智能Tab补全设置完成！"
    echo ""
    echo "💡 使用方法："
    echo "   1. 重新启动Git Bash或运行: source ~/.bashrc"
    echo "   2. 输入: python src/cli/main.py [TAB]"
    echo "   3. 或者: py src/cli/main.py [TAB]"
    echo "   4. 或者使用别名: auto-coder [TAB]"
    echo ""
    echo "🎯 支持的智能补全："
    echo "   - 命令补全: status, task-status, run-task 等"
    echo "   - 动态任务ID补全: 自动读取config/tasks/目录"
    echo "   - 目录补全: --config 参数"
    echo "   - 别名支持: auto-coder, auto-coder-py"
    echo ""
    echo "🔧 别名设置："
    echo "   - auto-coder = python src/cli/main.py"
    echo "   - auto-coder-py = py src/cli/main.py"
}

# 执行设置
setup_smart_completion
