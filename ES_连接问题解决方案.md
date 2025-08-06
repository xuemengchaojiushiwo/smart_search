# Elasticsearch 连接问题解决方案

## 🔍 问题诊断

根据测试结果，ES确实在运行，但遇到了以下问题：

1. **ES配置了HTTPS安全连接**
2. **ES启用了安全认证**
3. **默认用户名密码不正确**

## 💡 解决方案

### 方案1：重置ES安全配置（推荐）

#### 1. 停止ES服务
```bash
# 在ES控制台按 Ctrl+C 停止
# 或者找到Java进程并结束
taskkill /F /IM java.exe
```

#### 2. 修改ES配置
编辑文件：`D:\xmc\elasticsearch-9.1.0-windows-x86_64\elasticsearch-9.1.0\config\elasticsearch.yml`

添加或修改以下配置：
```yaml
# 禁用安全功能
xpack.security.enabled: false

# 禁用HTTPS
xpack.security.http.ssl.enabled: false
xpack.security.transport.ssl.enabled: false

# 允许HTTP访问
http.port: 9200
network.host: localhost
```

#### 3. 重新启动ES
```bash
cd D:\xmc\elasticsearch-9.1.0-windows-x86_64\elasticsearch-9.1.0
.\bin\elasticsearch.bat
```

#### 4. 等待启动完成（30-60秒）

#### 5. 测试连接
```bash
python test_es_status.py
```

### 方案2：使用正确的认证信息

如果你知道ES的用户名和密码：

#### 1. 修改测试脚本
编辑 `es_setup.py`，在Elasticsearch连接处添加认证：

```python
# 在文件开头添加
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 修改ES连接
es = Elasticsearch(
    ['https://localhost:9200'],
    http_auth=('your_username', 'your_password'),
    verify_certs=False
)
```

#### 2. 运行设置脚本
```bash
python es_setup.py
```

### 方案3：使用HTTP模式（最简单）

#### 1. 修改ES配置
编辑 `elasticsearch.yml`：
```yaml
# 禁用所有安全功能
xpack.security.enabled: false
xpack.security.http.ssl.enabled: false
xpack.security.transport.ssl.enabled: false

# 基本配置
http.port: 9200
network.host: localhost
cluster.name: elasticsearch
node.name: node-1
```

#### 2. 重启ES
```bash
# 停止ES
taskkill /F /IM java.exe

# 重新启动
cd D:\xmc\elasticsearch-9.1.0-windows-x86_64\elasticsearch-9.1.0
.\bin\elasticsearch.bat
```

#### 3. 测试连接
```bash
python test_es_status.py
```

## 🔧 快速修复脚本

我创建了一个快速修复脚本：

```bash
python fix_es_config.py
```

这个脚本会自动：
1. 备份原始配置
2. 修改配置文件
3. 重启ES服务
4. 测试连接

## 📋 验证步骤

修复后，按以下步骤验证：

### 1. 检查ES状态
```bash
python test_es_status.py
```

### 2. 设置知识库
```bash
python es_setup.py
```

### 3. 测试搜索功能
```bash
python test_search.py
```

## 🐛 常见问题

### 问题1：ES启动失败
**解决方案**：
- 检查内存设置：编辑 `config/jvm.options`
- 设置：`-Xms1g -Xmx1g`
- 确保有足够的内存

### 问题2：端口被占用
**解决方案**：
```bash
# 检查端口占用
netstat -ano | findstr :9200

# 杀死占用进程
taskkill /PID <进程ID> /F
```

### 问题3：权限问题
**解决方案**：
- 以管理员身份运行命令提示符
- 确保有写入ES目录的权限

## 📞 技术支持

如果问题仍然存在：

1. **查看ES日志**：
   ```
   D:\xmc\elasticsearch-9.1.0-windows-x86_64\elasticsearch-9.1.0\logs\elasticsearch.log
   ```

2. **检查系统资源**：
   - 确保有足够的内存（至少4GB）
   - 确保有足够的磁盘空间

3. **重新安装ES**：
   - 删除ES目录
   - 重新解压ES
   - 使用默认配置启动

## 🎯 成功标志

修复成功后，你应该看到：
- ✅ ES连接成功
- ✅ 集群状态正常
- ✅ 可以创建索引
- ✅ 可以添加和搜索数据 