import sys

from PyQt5.QtWidgets import (QApplication, QMainWindow, QTableWidget, QTableWidgetItem,
                             QVBoxLayout, QWidget, QPushButton, QMessageBox, QHBoxLayout)
from PyQt5.QtGui import QColor, QBrush
from docker import from_env


class DockerManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.docker_client = from_env()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Docker Manager')
        self.setGeometry(100, 100, 800, 600)

        self.tableWidget = QTableWidget()
        self.tableWidget.setColumnCount(5)
        self.tableWidget.setHorizontalHeaderLabels(['CONTAINER ID', 'IMAGE', 'STATUS', 'PORTS', 'ACTIONS'])

        self.loadContainers()

        layout = QVBoxLayout()
        layout.addWidget(self.tableWidget)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def loadContainers(self):
        self.tableWidget.clearContents()
        containers = self.docker_client.containers.list(all=True)
        self.tableWidget.setRowCount(len(containers))
        for index, container in enumerate(containers):
            self.tableWidget.setItem(index, 0, QTableWidgetItem(container.short_id))
            self.tableWidget.setItem(index, 1,
                                     QTableWidgetItem(container.image.tags[0] if container.image.tags else 'unknown'))

            status_item = QTableWidgetItem(container.status)
            # Устанавливаем цвет фона в зависимости от статуса контейнера
            if container.status == 'running':
                status_item.setBackground(QBrush(QColor(144, 238, 144)))  # Светло-зеленый цвет
            else:
                status_item.setBackground(QBrush(QColor(255, 99, 71)))  # Светло-красный цвет
            self.tableWidget.setItem(index, 2, status_item)

            self.tableWidget.setItem(index, 3, QTableWidgetItem(str(container.attrs['NetworkSettings']['Ports'])))
            self.addControlButtons(index, container)

    def addControlButtons(self, row, container):
        btn_layout = QHBoxLayout()
        start_btn = QPushButton('Start')
        stop_btn = QPushButton('Stop')
        btn_layout.addWidget(start_btn)
        btn_layout.addWidget(stop_btn)

        start_btn.clicked.connect(lambda checked, container_id=container.id: self.startContainer(container_id))
        stop_btn.clicked.connect(lambda checked, container_id=container.id: self.stopContainer(container_id))

        container_widget = QWidget()
        container_widget.setLayout(btn_layout)
        self.tableWidget.setCellWidget(row, 4, container_widget)

    def startContainer(self, container_id):
        try:
            container = self.docker_client.containers.get(container_id)
            container.start()
            QMessageBox.information(self, "Container Start", f"Container {container_id} has been started successfully.")
            self.loadContainers()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def stopContainer(self, container_id):
        try:
            container = self.docker_client.containers.get(container_id)
            container.stop()
            QMessageBox.information(self, "Container Stop", f"Container {container_id} has been stopped successfully.")
            self.loadContainers()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


def run_app():
    app = QApplication(sys.argv)
    ex = DockerManager()
    ex.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    run_app()
