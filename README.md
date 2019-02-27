# Zcash Miner

    Ondrej Sika <ondrej@ondrejsika.com>
    https://github.com/ondrejsika/zcashd-miner

## Installation

```
virtualenv .env
. .env/bin/activate
pip install git+https://github.com/ondrejsika/zcashd-miner.git
```

## Usage


```
zcashd-miner.py --help
```

Example of usage

```
zcashd-miner.py http://zu:zp@localhost:28232 1
```

## Docker

### Build Image

```
docker build -t ondrejsika/zcashd-miner .
```

### Run from Docker

```
docker run ondrejsika/zcashd-miner --help
```

Example of usage

```
docker run ondrejsika/zcashd-miner http://zu:zp@localhost:28232 1
```
