import sys
from PyQt5.QtWidgets import QApplication
from peernetwork import PeerNetwork
from user_manager import UserManager
from login_app import LoginApp

if __name__ == '__main__':
    app = QApplication(sys.argv)
    user_manager = UserManager()
    peer_network = PeerNetwork()
    login_window = LoginApp(user_manager, peer_network)
    login_window.show()
    sys.exit(app.exec_())
