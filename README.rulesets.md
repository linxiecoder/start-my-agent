# GitHub 仓库规则集配置

已为您创建基础规则集配置，包含以下保护措施：

## 🛡️ 规则集内容

### 1. 分支保护规则
- **禁止直接推送**：防止直接推送到 master 分支
- **线性历史要求**：强制使用合并提交，保持历史清晰
- **非快进合并**：确保每个合并都有明确的记录

### 2. 提交要求
- **语义化提交消息**：要求提交消息符合格式：`type(scope): description`
  - 示例：`feat(auth): add login feature`
  - 支持的类型：feat, fix, chore, docs, style, refactor, perf, test
- **提交签名验证**（可选）：可启用 GPG 签名验证

### 3. 合并要求
- **代码审核**：至少需要 1 次审核批准
- **过时审核自动失效**：代码更新后需要重新审核
- **对话解决要求**：所有讨论必须标记为已解决
- **状态检查**：可配置 CI 测试要求

## 📋 应用规则集

### 方法一：通过 GitHub Web UI（推荐）

1. **访问仓库设置**
   - 打开仓库页面：https://github.com/linxiecoder/start-my-agent
   - 点击 **Settings** → **Rules** → **Add rule set**

2. **导入规则集配置**
   - 选择 **"Create from JSON"**
   - 复制 `.sisyphus/rulesets/basic-ruleset.json` 内容
   - 粘贴到配置框中
   - 点击 **Create rule set**

3. **自定义配置**（可选）
   - 调整分支范围：默认包含 master 分支
   - 修改审核人数：根据团队规模调整
   - 添加状态检查：配置 CI 工作流

### 方法二：通过 GitHub CLI

```bash
# 安装 GitHub CLI（如果未安装）
# Windows: winget install GitHub.cli
# macOS: brew install gh
# Linux: sudo apt install gh

# 登录 GitHub
gh auth login

# 应用规则集
gh api \
  --method POST \
  -H "Accept: application/vnd.github+json" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  /repos/linxiecoder/start-my-agent/rulesets \
  -f name='基础保护规则集' \
  -f target='branch' \
  -f enforcement='active' \
  --input .sisyphus/rulesets/basic-ruleset.json
```

### 方法三：通过 GitHub API

```bash
curl -L \
  -X POST \
  -H "Accept: application/vnd.github+json" \
  -H "Authorization: Bearer YOUR_GITHUB_TOKEN" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  https://api.github.com/repos/linxiecoder/start-my-agent/rulesets \
  -d @.sisyphus/rulesets/basic-ruleset.json
```

## 🔧 规则集配置详解

### 核心规则说明

| 规则类型 | 作用 | 参数配置 |
|---------|------|----------|
| `pull_request` | 合并请求要求 | 需要 1 次审核，过时审核失效 |
| `required_linear_history` | 线性历史 | 禁止合并提交 |
| `commit_message_pattern` | 提交消息格式 | 语义化提交格式 |
| `required_status_checks` | 状态检查 | 可配置 CI 检查项 |

### 自定义调整建议

1. **团队协作调整**：
   ```json
   "required_approving_review_count": 2,  // 增加审核人数
   "require_code_owner_review": true      // 启用代码所有者审核
   ```

2. **CI/CD 集成**：
   ```json
   "required_status_checks": [
     {
       "context": "ci/tests",
       "integration_id": null
     }
   ]
   ```

3. **分支范围扩展**：
   ```json
   "include": [
     "~DEFAULT_BRANCH",
     "refs/heads/master",
     "refs/heads/main",
     "refs/heads/release/*"
   ]
   ```

## 📝 语义化提交规范

### 提交类型
- **feat**: 新功能
- **fix**: 错误修复
- **docs**: 文档更新
- **style**: 代码格式（不影响功能）
- **refactor**: 代码重构
- **perf**: 性能优化
- **test**: 测试相关
- **chore**: 构建/工具更新

### 示例
```
feat(auth): add JWT authentication
fix(api): resolve CORS issue
docs(readme): update installation steps
chore(deps): upgrade dependencies
```

## ⚠️ 注意事项

1. **首次应用**：建议在非工作时间应用，避免影响开发
2. **权限要求**：需要仓库管理员权限
3. **渐进实施**：可先应用于新分支，再扩展到主分支
4. **备份配置**：保留当前规则集配置作为备份

## 🔗 参考资源

- [GitHub Rulesets Documentation](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/about-rulesets)
- [Semantic Commit Messages](https://www.conventionalcommits.org/)
- [GitHub REST API - Rulesets](https://docs.github.com/en/rest/repos/rules)

---

**提示**：应用规则集后，所有新合并请求将自动受规则约束。现有分支不受影响。