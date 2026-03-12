# 部署文档

## 环境要求

- 无需服务器端运行环境（纯静态网站）
- GitHub Pages 托管
- 现代浏览器支持

## 部署步骤

### 1. GitHub Pages 自动部署

项目已配置 GitHub Actions 自动部署工作流（`.github/workflows/deploy.yml`）。

**触发条件：**
- 推送到 `main` 分支
- 手动触发 workflow

**部署流程：**
1. GitHub Actions 自动构建
2. 将 `docs/` 目录部署到 GitHub Pages
3. 访问地址：`https://badhope.github.io/python-exercise-9999/`

### 2. 手动部署

如需手动部署到其他服务器：

```bash
# 1. 克隆仓库
git clone https://github.com/badhope/python-exercise-9999.git

# 2. 复制 docs 目录到服务器
scp -r docs/* user@server:/var/www/html/

# 3. 配置 Nginx（示例）
server {
    listen 80;
    server_name example.com;
    root /var/www/html;
    index index.html;
    
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    # 启用 Gzip 压缩
    gzip on;
    gzip_types text/html text/css application/javascript;
    
    # 缓存策略
    location ~* \.(css|js|png|jpg|jpeg|gif|ico|svg|woff|woff2)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

## 配置说明

### GitHub Pages 设置

1. 进入仓库 Settings > Pages
2. Source 选择 "GitHub Actions"
3. 保存设置

### 自定义域名（可选）

1. 在 `docs/` 目录创建 `CNAME` 文件
2. 内容为你的域名（如 `example.com`）
3. 在域名服务商配置 CNAME 指向 `badhope.github.io`

## 文件结构

```
docs/
├── index.html      # 主页面
├── css/
│   └── style.css   # 样式文件
└── js/
    └── main.js     # 交互脚本
```

## 技术栈

- **HTML5**: 语义化标签，SEO友好
- **CSS3**: 响应式设计，BEM命名规范
- **JavaScript (ES6+)**: 模块化设计，无依赖
- **GitHub Actions**: CI/CD 自动部署

## 浏览器兼容性

| 浏览器 | 版本要求 |
|--------|----------|
| Chrome | 最新版及前两版本 |
| Firefox | 最新版及前两版本 |
| Safari | 最新版及前两版本 |
| Edge | 最新版及前两版本 |

## 性能优化

- CSS/JS 内联关键资源
- 字体预连接（preconnect）
- 响应式图片
- Gzip 压缩
- 浏览器缓存

## 故障排除

### 部署失败

1. 检查 GitHub Actions 日志
2. 确认 `docs/` 目录存在
3. 验证 YAML 语法正确

### 页面无法访问

1. 确认 GitHub Pages 已启用
2. 检查 CNAME 配置（如使用自定义域名）
3. 等待 DNS 传播（最多 24 小时）

## 联系方式

- GitHub Issues: https://github.com/badhope/python-exercise-9999/issues
