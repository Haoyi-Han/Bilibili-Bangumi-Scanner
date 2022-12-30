# 哔哩哔哩（Bilibili）番剧名称扫描工具

## 简介
本工具用于遍历 md 号爬取 B 站番剧名称，将爬取到的 md 号、番剧名称、番剧主页地址保存在文本文档中。

## 用法
用以下命令克隆本项目：
```shell
git clone https://github.com/Haoyi-Han/Bilibili-Bangumi-Scanner.git
cd Bilibili-Bangumi-Scanner
```

安装必要运行库：
```shell
pip install -r requirements.txt
```

运行命令：
```shell
python -m bilibili-bangumi-scanner <起始 md 号（仅数字）> <终止 md 号（仅数字，不含）> [--log]
# 示例（--log 用于输出调试日志，常规使用可省略）
python -m bilibili-bangumi-scanner 28370000 28390000 --log
```

程序将以多线程运行，期间会有部分缓存文件产生，这些文件将在程序结束时自动清理。

爬取的番剧名称信息将保存到同目录下的 `bangumi_titles.txt` 文件中。
