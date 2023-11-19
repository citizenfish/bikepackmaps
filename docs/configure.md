# Mac OSX - Silicon


# Mac OSX Install

## osmium-tool

brew install osmium-tool

## java

Installed with (on Mac)
```shell
brew install java
sudo ln -sfn /opt/homebrew/opt/openjdk/libexec/openjdk.jdk /Library/Java/JavaVirtualMachines/openjdk.jdk
```

# Linux Install

```commandline
sudo apt-get install python3-pip
sudo apt-get install osmium-tool gdal-bin libgdal-dev
export CPLUS_INCLUDE_PATH=/usr/include/gdal
export C_INCLUDE_PATH=/usr/include/gdal
ogrinfo --version
pip install GDAL-<VERSION>
pip install -r requirements.txt
sudo apt-get install default-jre
sudo apt-get install osmosis
suod apt-get install osmctools
```

