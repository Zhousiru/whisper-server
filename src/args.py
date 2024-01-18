import argparse


def parse_args():
    parser = argparse.ArgumentParser(
        prog='whisper-server')

    parser.add_argument('--model', required=True,
                        type=str, help='model path or name')
    parser.add_argument('--host', default='127.0.0.1',
                        type=str, help='listen host (default: 127.0.0.1)')
    parser.add_argument('--port', default=8080, type=int,
                        help='listen port (default: 8080)')
    parser.add_argument('--device', default='auto', choices=[
                        'auto', 'cpu', 'cuda'], help='device type (default: auto)')
    parser.add_argument('--type', default='default', type=str,
                        help='quantization type, see https://opennmt.net/CTranslate2/quantization.html (default: default)')

    return parser.parse_args()
