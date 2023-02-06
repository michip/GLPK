wget --reject "index.html*" -m -np http://old.sztaki.hu/~meszaros/public_ftp/lptestset/misc/

mv old.sztaki.hu/\~meszaros/public_ftp/lptestset/misc/ ./
rm -rf old.sztaki.hu
mv misc misc-gz