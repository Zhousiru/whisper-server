import argparse


def parse_args():
    parser = argparse.ArgumentParser(
        description='whisper-server')

    parser.add_argument('--host', default='127.0.0.1',
                        type=str, help='Listen host (default: 127.0.0.1)')
    parser.add_argument('--port', default=8080, type=int,
                        help='Listen port (default: 8080)')
    parser.add_argument('--model', required=True,
                        type=str, help='Model path or name')
    parser.add_argument('--device', default='auto', choices=[
                        'auto', 'cpu', 'cuda'], help='Device type (default: auto)')
    parser.add_argument('--type', default='default', type=str,
                        help='Quantization type, see https://opennmt.net/CTranslate2/quantization.html (default: default)')

    return parser.parse_args()
