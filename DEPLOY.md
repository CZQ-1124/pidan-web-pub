# 皮蛋乡村系统：公开网页版部署说明

## 1. 当前包做了什么处理

- 删除 `.git/`、`venv/`、`__pycache__/`、`.env`、运行期 `uploads/`、`data/cases.db`。
- 示例图片文件名已改为 `demo_case_001.*` 形式，病例表中的 `file_name` 和 `relative_path` 已同步更新。
- API key 默认不允许从网页端写入；公开部署时请用平台 Secrets 或服务器环境变量配置。
- 新增 `Dockerfile`、`.dockerignore`、`.streamlit/secrets.example.toml`。

> 注意：本包只处理了文件名和路径层面的脱敏。图片内容本身是否含可识别人脸、纹身、病案号、水印等，需要人工复核；公开展示前必须确认授权、伦理与隐私合规。

## 2. 本地测试

```bash
cd pidan_web_public
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# 编辑 .env，填入 AI_API_KEY 等
streamlit run app.py
```

## 3. Streamlit Community Cloud 部署

1. 新建 GitHub 仓库，只上传本部署包内容。
2. 不要上传 `.env`、`.streamlit/secrets.toml`、`data/cases.db`、`uploads/`。
3. 在 Streamlit Cloud 选择仓库和入口文件 `app.py`。
4. 在 Secrets 中配置：

```toml
AI_BASE_URL = "https://aihubmix.com/v1"
AI_API_KEY = "replace_with_your_key"
TEXT_MODEL = "doubao-seed-2-0-mini"
VISION_MODEL = "qwen3-vl-flash"
AUDIO_MODEL = ""
THINKING_MODE = "omit"
AI_TIMEOUT_SEC = "25"
PUBLIC_MODE = "true"
ENABLE_RUNTIME_SETTINGS = "false"
```

## 4. 服务器 / 云主机 Docker 部署

```bash
docker build -t pidan-web .
docker run -d --name pidan-web       -p 8501:8501       -e AI_BASE_URL="https://aihubmix.com/v1"       -e AI_API_KEY="replace_with_your_key"       -e TEXT_MODEL="doubao-seed-2-0-mini"       -e VISION_MODEL="qwen3-vl-flash"       -e PUBLIC_MODE="true"       -e ENABLE_RUNTIME_SETTINGS="false"       pidan-web
```

浏览器访问：`http://服务器IP:8501`。

## 5. 更正式的公网发布建议

- 用域名 + HTTPS 反向代理，不要裸奔 HTTP。
- 用户上传图片、语音、病例数据不要只存本地 SQLite；正式版建议接对象存储 + PostgreSQL/MySQL。
- 增加真正账号体系、角色权限、日志审计、限流和免责声明。
- 医学输出统一标注为“辅助建议，不能替代医生诊断”。
