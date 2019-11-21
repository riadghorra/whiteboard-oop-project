from white_board import WhiteBoard
import json

with open('config.json') as json_file:
    start_config = json.load(json_file)


def main():
    board = WhiteBoard("client", start_config)
    board.start_local()


if __name__ == '__main__':
    main()
