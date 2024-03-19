sudo apt install -y autoconf automake libtool make
git clone https://github.com/xiph/rnnoise.git
cd rnnoise
chmod +x autogen.sh
./autogen.sh
./configure
make
make install