wget --reject "index.html*" -m -np http://old.sztaki.hu/~meszaros/public_ftp/lptestset/stochlp/

mv old.sztaki.hu/\~meszaros/public_ftp/lptestset/stochlp/ ./
rm -rf old.sztaki.hu
mv stochlp stochlp-gz