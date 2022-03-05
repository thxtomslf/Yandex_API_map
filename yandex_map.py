import sys
from PyQt5.QtWidgets import QMainWindow, QApplication, QGraphicsScene, QGraphicsView
from PyQt5.QtGui import QPixmap, QKeyEvent
import PyQt5.QtCore
from UI.map_project import Ui_MainWindow
import requests
import io


class Map(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(Map, self).__init__()
        self.setupUi(self)
        self.initUI()

        self.map_width = '650'
        self.map_height = '450'
        self.adress = ''
        self.postal_code = ''
        self.geocode_params = {'apikey': '40d1649f-0493-4b70-98ba-98533de7710b',
                               'geocode': ' '.join(self.adress), 'format': 'json'}
        self.geocoder_server = 'https://geocode-maps.yandex.ru/1.x/'

        self.maps_server = 'https://static-maps.yandex.ru/1.x/'
        self.maps_params = {'ll': '', 'l': 'map', 'z': '8', 'size': f'{self.map_width},{self.map_height}'}
        self.book_for_map_params = {'Спутник': 'sat', 'Карта': 'map', 'Гибрид': 'sat,skl'}

        self.buf = io.BytesIO()

    def initUI(self):
        self.setFocusPolicy(PyQt5.QtCore.Qt.StrongFocus)

        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene, self)
        self.view.setFocusPolicy(PyQt5.QtCore.Qt.ClickFocus)
        self.view.setGeometry(240, 20, 781, 721)

        self.pixmap = QPixmap()

        self.pushButton.clicked.connect(self.show_result)

        self.pushButton_2.clicked.connect(self.clear_search)

        self.comboBox.currentTextChanged.connect(self.change_map_style)

        self.palett = PyQt5.QtGui.QPalette()
        self.palett.setColor(self.palett.Background, PyQt5.QtGui.QColor(128, 128, 128))
        self.statusbar.setAutoFillBackground(True)
        self.statusbar.setPalette(self.palett)

    """def eventFilter(self, obj, event):
        if event.type() == PyQt5.QtCore.QEvent.FocusIn:
            print(1)
            return True
        return False"""

    def keyPressEvent(self, event):
        if event.key() == PyQt5.QtCore.Qt.Key_Up:
            self.move_up()

        if event.key() == PyQt5.QtCore.Qt.Key_Down:
            self.move_down()

        if event.key() == PyQt5.QtCore.Qt.Key_Right:
            self.move_right()

        if event.key() == PyQt5.QtCore.Qt.Key_Left:
            self.move_left()

        if event.key() == PyQt5.QtCore.Qt.Key_Return:
            self.show_result()
        self.update_map()

    def wheelEvent(self, event):
        if event.angleDelta().y() > 0:
            self.increase_scale()
        else:
            self.shrink_scale()
        self.update_map()

    def mousePressEvent(self, event):
        if 344 < event.x() < 954 and 155 < event.y() < 605:
            pass

    def show_result(self):
        self.get_geocoder_data()
        self.update_map()

    def clear_search(self):
        self.lineEdit.setText('')
        self.statusbar.showMessage('')
        self.checkBox.setCheckState(False)
        self.maps_params['pt'] = ''
        self.update_map()

    def update_map(self):
        self.map_pic = requests.get(self.maps_server, params=self.maps_params)
        self.buf.write(self.map_pic.content)
        self.buf.seek(0)
        self.pixmap.loadFromData(self.buf.read())
        self.buf.seek(0)
        self.scene.addPixmap(self.pixmap)

    def get_geocoder_data(self):
        self.adress = self.lineEdit.text()
        self.geocode_params['geocode'] = self.adress
        try:
            resp_json = requests.get(self.geocoder_server, params=self.geocode_params).json()

            coords = resp_json['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['Point']['pos']
            coords = coords.replace(' ', ',')
            st_bar_msg = resp_json['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['metaDataProperty']['GeocoderMetaData']['text']
            if self.checkBox.isChecked():
                st_bar_msg = \
                    resp_json['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['metaDataProperty'][
                        'GeocoderMetaData']['Address']['postal_code'] + ', ' + st_bar_msg
            self.statusbar.showMessage(st_bar_msg)
            self.maps_params['ll'] = coords
            self.maps_params['pt'] = coords + ',' + 'pm2dbm'
        except KeyError:
            if self.lineEdit.text() == '':
                self.statusbar.showMessage('Поле ввода пустое')
        except IndexError:
            self.statusbar.showMessage('Запрашиваемый адрес не найден')

    def move_up(self):
        coords = self.maps_params['ll'].split(',')
        coords[1] = str(float(coords[1]) + 1.9 ** (-int(self.maps_params['z']) + 5))
        self.maps_params['ll'] = ','.join(coords)

    def move_down(self):
        coords = self.maps_params['ll'].split(',')
        coords[1] = str(float(coords[1]) - 1.9 ** (-int(self.maps_params['z']) + 5))
        self.maps_params['ll'] = ','.join(coords)

    def move_left(self):
        coords = self.maps_params['ll'].split(',')
        coords[0] = str(float(coords[0]) - 1.9 ** (-int(self.maps_params['z']) + 5))
        self.maps_params['ll'] = ','.join(coords)

    def move_right(self):
        coords = self.maps_params['ll'].split(',')
        coords[0] = str(float(coords[0]) + 1.9 ** (-int(self.maps_params['z']) + 5))
        self.maps_params['ll'] = ','.join(coords)

    def increase_scale(self):
        if float(self.maps_params['z']) + 1 <= 17:
            self.maps_params['z'] = str(int(self.maps_params['z']) + 1)

    def shrink_scale(self):
        if float(self.maps_params['z']) - 1 >= 1:
            self.maps_params['z'] = str(int(self.maps_params['z']) - 1)

    def change_map_style(self):
        self.maps_params['l'] = self.book_for_map_params[self.comboBox.currentText()]
        self.update_map()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Map()
    #window.installEventFilter(window)
    window.show()
    app.exec()