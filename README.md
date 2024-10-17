# fuqr

## 概要
windowsデスクトップでQRコードを読み取るだけのやつです  
スクショ、再生成、ブラウザで開く、値のコピーができるはずです  
再生成に関しては値の正しさは保証できません

## 使い方
起動したら枠の中にQRコードを収めてください。認識に成功したら自動で結果が表示されます  
うまく読み取れないときは少し動かしてみてください    
小さい丸でできてるやつとか特殊形はあまり認識できません  


## インストール
[uv](https://github.com/astral-sh/uv)を前提とします

### git cloneする場合
1. `uv sync --all-extras --dev`

2.  a. `.venv/scripts/pythonw.exe`のショートカットを作る  
    作業ディレクトリを`/path/to/fuqr`、リンク先に`-m fuqr`を追記  
    アイコンの変更で`favicon.ico`設定してあげるとアイコンも反映されます。タスクバーに固定するとpythonのアイコンになりますが

    b. `uv tool install .`でuvのツールとしてインストールする  
    `~/.local/bin`に実行ファイルが作成されます。アイコンは反映されません

### コードはいらない場合
1. `uv tool install git+https://github.com/futa-t/fuqr`でインストールできます。アイコンは反映されません