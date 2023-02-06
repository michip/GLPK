gunzip misc-gz/*.gz
mkdir misc
for f in misc-gz/*; do ../converter ${f} > misc/$(basename "$f").mps; done;
rm -rf misc-gz