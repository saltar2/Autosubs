sudo apt install -y autoconf automake libtool make
git clone https://github.com/xiph/rnnoise.git
cd rnnoise
chmod +x autogen.sh
./autogen.sh
./configure
make
make install
python3 -m pip install torch torchaudio --index-url https://download.pytorch.org/whl/cpu
#** Para instalar torch en tu sistema mira esta pagina:
# https://pytorch.org/ El siguiente comando es para linux y si usas otro sistema debes cambiarlo por el que indique la web.
python3 -m pip install -r requirements.txt