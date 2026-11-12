# BLACK YAK 27FW 經銷線上訂貨

照 SDR FW27／DESCENTE 27FW 範本。資料來源：原廠 2026/11/9 提供的 KOREA TARGET 27FW RAWDATA（605 款色／240 款（已拿掉中國專屬款））；原廠 Dashboard 當時仍是舊的 150 筆。售價用公司 2026/11/12 定案的台灣建議售價（TW-SRP），已寫進 `data.js` 的 `price`。27FW 有 40 個中國專屬款色價格表沒填，卡片顯示「售價待確認」。

- `index.html` 下單頁、`data.js` 商品資料（`BY_CFG` 分頁／尺寸設定）、`imgs.js`／`big/` 圖片、`config.js` 收單網址、`apps-script/Code.gs` 收單程式。
- 重產資料：`python3 tools/gen_fw2.py .`（來源 `tools/fw2_src.json`，中文品名 `tools/fw2_zh.py`；主打款與台灣市場備註的規則都在 `gen_fw2.py`）。舊版 `tools/gen.py`
