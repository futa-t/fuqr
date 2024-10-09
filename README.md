# fuqr

## 概要
windowsデスクトップでQRコードを読み取るだけのやつ  
スクショ、再生成、ブラウザで開く、値のコピーができるはずです  
再生成に関しては値の正しさは保証できません

## インストール
`.github/workflows/release.yml`のInstall the projectあたりから追っていくけばdistに実行ファイルが作成されるのでパス通ってる場所なりデスクトップなりに配置してください

`uv sync`したあとの`.venv/scripts/pythonw.exe`のショートカット作って作業ディレクトリを`/path/to/fuqr`にしてリンク先に`-m fuqr`を追記してアイコンの変更で`favicon.ico`設定してあげればexe化しなくても使えます。正直こっちの使い方のほうがおすすめ