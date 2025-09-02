#!/bin/bash

# 自动化AI任务执行系统 - 智能Tab补全脚本
# 专门为system_manager.py提供Tab补全功能

echo "🚀 设置自动化AI任务执行系统的Tab补全..."

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "📁 脚本目录: $SCRIPT_DIR"

# 创建智能补全函数
create_smart_completion_function() {
    cat > /tmp/auto_coder_smart_completion.sh << 'EOF'
# 自动化AI任务执行系统 - 智能Tab补全函数
_auto_coder_system_manager_completion() {
    local cur prev
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"
    
    # system_manager.py 命令列表
    local cmds="start stop status run daemon --help -h help"
    
    if [[ $COMP_CWORD -eq 1 ]]; then
        COMPREPLY=( $(compgen -W "${cmds}" -- "${cur}") )
    fi
}

# 注册补全函数
complete -F _auto_coder_system_manager_completion python
complete -F _auto_coder_system_manager_completion py

# 为system_manager.py注册专用补全
complete -F _auto_coder_system_manager_completion system_manager.py

# 为特定命令创建别名以简化使用
alias system-manager="python system_manager.py"

# 为别名也注册补全
complete -F _auto_coder_system_manager_completion system-manager
EOF

    echo "✅ system_manager.py补全函数已创建"
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
    
    echo "✅ Tab补全设置完成！"
    echo ""
    echo "💡 使用方法："
    echo "   1. 重新启动Git Bash或运行: source ~/.bashrc"
    echo "   2. 系统管理: python system_manager.py [TAB]"
    echo "   3. 或者使用别名: system-manager [TAB]"
    echo ""
    echo "🎯 支持的补全："
    echo "   🚀 系统管理命令补全:"
    echo "      - start, stop, status, run, daemon"
    echo "      - --help, -h, help"
    echo ""
    echo "🔧 别名设置："
    echo "   - system-manager = python system_manager.py"
    echo ""
    echo "📝 使用示例："
    echo "   # 系统管理"
    echo "   system-manager [TAB]          # 显示: start stop status run daemon"
    echo "   system-manager daemon         # 后台启动系统"
    echo "   system-manager status         # 查看系统状态"
    echo "   system-manager stop           # 停止系统"
}

# 执行设置
setup_smart_completion
