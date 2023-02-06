gunzip stochlp-gz/*.gz
mkdir stochlp
for f in stochlp-gz/*; do ../converter ${f} > stochlp/$(basename "$f").mps; done;
rm -rf stochlp-gz