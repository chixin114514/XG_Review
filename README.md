# 习概毛概刷题工具

离线可用的习概/毛概高效刷题网页。

## 使用

直接打开 `index.html`。题库文件需要和 `index.html` 放在同一目录：

- `question_bank_combined_en_schema.json`
- `question_bank_combined_en_schema.js`

页面使用浏览器本地存储保存错题、收藏、连续答对和进度。

## 验证

```bash
node --test tests/app-core.test.mjs tests/html-contract.test.mjs
```
