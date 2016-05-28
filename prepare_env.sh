rm -rf virtualenv-15.0.1.tar.gz
curl -o virtualenv-15.0.1.tar.gz https://pypi.python.org/packages/c8/82/7c1eb879dea5725fae239070b48187de74a8eb06b63d9087cd0a60436353/virtualenv-15.0.1.tar.gz
tar xvf virtualenv-15.0.1.tar.gz
python virtualenv-15.0.1/virtualenv.py env
source env/bin/activate
pip install docopt==0.6.2 python-digitalocean==1.8.1 petname==1.12 sshpubkeys==1.2.2