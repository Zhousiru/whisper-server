# whisper-server

Bundled Whisper API server, with faster-whisper and CUDA Toolkit.

## Download

[Dev Build (latest)](https://github.com/Zhousiru/whisper-server/releases/tag/latest)

## Usage

Execute `whisper-server.sh` on Linux or `whisper-server.bat` on Windows with the following arguments:

```
whisper-server [-h] [--host HOST] [--port PORT] --model MODEL [--device {auto,cpu,cuda}] [--type TYPE]
```

### Options

- `-h, --help`: Displays the help message and exits the program.
- `--model MODEL`: Specifies the path or name of the model.
- `--host HOST`: Sets the listening host. (default: 127.0.0.1)
- `--port PORT`: Sets the listening port. (default: 8080)
- `--device {auto,cpu,cuda}`: Chooses the device type. (default: auto)
- `--type TYPE`: Selects the quantization type. For more information, refer to the [CTranslate2 Quantization Documentation](https://opennmt.net/CTranslate2/quantization.html). (default: default)

