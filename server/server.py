import socket
from utils import read_json, pre_check
import threading
from game import Game


def start_game(clients, mode, client_deck):
    gcg = Game(mode, clients, client_deck)
    gcg.start_game()

class Server:
    def __init__(self):
        self.waiting_clients = [] # clients waiting in the waiting area
        self.client_info = {} # client info, formatted as {"ip": (nickname, mode)}
        self.mode_clients = {} # key: mode, value: list of clients who choose this mode
        self.config = read_json("config.json")["server"] # load the configuration file
        self.svr_sock = self.create_socket() # create socket
        self.valid_deck_client = {} # client deck information, formatted as {"ip": (character, deck)}


    @staticmethod
    def create_socket():
        svr_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        svr_sock.bind(("127.0.0.1", 4095))
        return svr_sock

    def send(self, data, client):
        self.svr_sock.sendto(data, client)

    def handle_game_session(conn, player_info):
        ...
        while True:
            # Получаем сообщение от клиента
            data = conn.recv(BUFFER_SIZE)
            ...
            # Если клиент отправил запрос на начало игры
            elif message["message"] == "start game":
            # Добавляем клиента в список ожидающих игроков
            waiting_clients.append(conn)
            client_info[address][1] = "waiting"
            print(f"{client_info[address][0]} is waiting for an opponent.")
            # Если количество ожидающих игроков становится 2, начинаем игру
            if len(waiting_clients) == 2:
                print("Two players are now waiting. Starting game.")
                player1, player2 = waiting_clients
                waiting_clients = []
                # Определяем порядок игроков
                player_order = [player1, player2] if random.random() < 0.5 else [player2, player1]
                # Запускаем игровую сессию
                game_session = GameSession(player_order[0], player_order[1], player_info)
                game_session.start()
                print("Game over.")
            # Если количество ожидающих игроков становится 1, создаем бота и запускаем игру
            elif len(waiting_clients) == 1:
                print("One player is waiting. Starting game with bot.")
                # Создаем бота
                bot_deck = create_bot_deck()
                bot_player = Player("Bot", bot_deck)
                # Определяем порядок игроков
                human_player, = waiting_clients
                player_order = [human_player, bot_player]
                waiting_clients = []
                # Запускаем игровую сессию
                game_session = GameSession(player_order[0], player_order[1], player_info)
                game_session.start()
                print("Game over.")


    def handle_message(self, data, remote_addr):
        try:
            msg = eval(data.decode("utf-8"))
            if msg["message"] == "connect request":
                nickname = msg["nickname"]
                self.client_info[remote_addr] = [nickname, None]
                self.waiting_clients.append(remote_addr)
                self.send(str({"message": "choose mode"}).encode("utf-8"), remote_addr)
            elif msg["message"] == "selected mode":
                mode = msg["mode"]
                self.client_info[remote_addr][1] = mode
                self.send(str({"message": "send deck"}).encode("utf-8"), remote_addr)
                self.mode_clients.setdefault(mode, []).append(remote_addr)
            elif msg["message"] == "check deck":
                character = msg["character"]
                card = msg["card"]
                mode = self.client_info[remote_addr][1]
                check_state = pre_check(mode, character, card)
                if isinstance(check_state, list):
                    self.send(str({"message": "recheck deck", "invalid_card": check_state}).encode("utf-8"), remote_addr)
                else:
                    self.valid_deck_client.update({remote_addr: (character, card)})
                    self.whether_start_game(mode)
        except Exception as e:
            print("Error in handle_message:", e)

    def whether_start_game(self, mode):
        if mode in self.mode_clients:
            valid_client = []
            client_deck = {}
            for client in self.mode_clients[mode]:
                if client in self.valid_deck_client:
                    valid_client.append(client)
                    client_deck.update({client: self.valid_deck_client[client]})
            if len(valid_client) >= self.config[mode]["client_num"]:
                new_game_thread = threading.Thread(target=start_game, args=(valid_client, mode, client_deck))
                new_game_thread.start()  # 居然不能临时拉个进程
                for c in valid_client:
                    self.waiting_clients.remove(c)
                    self.mode_clients[mode].remove(c)
                    self.valid_deck_client.pop(c)

    def receive(self):
        while True:
            data, remote_addr = self.svr_sock.recvfrom(4096)
            if data:
                self.handle_message(data, remote_addr)

    def start(self):
        threading.Thread(target=self.receive).start()

if __name__ == "__main__":
    svr = Server()
    svr.start()
