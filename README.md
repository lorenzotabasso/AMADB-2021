# Progetto Unito MAADB

This is a work in progress readme

## Installation

### Setup Docker

Use your favorite shell to install [docker](https://docs.docker.com/get-started/overview/) and its utils.

Example
```bash
sudo apt-get install docker docker-compose
```
Verify that is correclty running 

```bash
docker info
```

If you are on unix sistem you maybe need to follow this post-installation step
https://docs.docker.com/engine/install/linux-postinstall/

## Usage

Execute the setup script

```bash
./setup
```

Verify that is correclty running
```bash
docker ps
```

If you wanna take down the net
```bash
docker-compose down
```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License