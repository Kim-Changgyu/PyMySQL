import pymysql
import sys
import datetime
import math
import csv
import json
import xml.etree.ElementTree as ET
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt

conn = pymysql.connect(host='localhost', user='guest', password='bemyguest', db='kleague', charset='utf8')

cursor = conn.cursor(pymysql.cursors.DictCursor)

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setupUI()

    def setupUI(self):
        # 윈도우 기본 설정
        self.setWindowTitle("Python and DB Applications REPORT")
        ##########################################################
        self.resize(800, 500)
        win = self.frameGeometry()
        centerPos = QDesktopWidget().availableGeometry().center()
        win.moveCenter(centerPos)
        self.move(win.topLeft())
        ##########################################################
        # 위 코드가 정상적으로 작동하지 않으면 아래 코드를 활용
        # self.setGeometry(0, 0, 800, 500)

        # Team Table에서 전체 데이터 추출 후 저장
        self.sql = "SELECT * from TEAM"
        cursor.execute(self.sql)
        team_data = cursor.fetchall()
        self.teams = {}
        for data in team_data:
            if not data["TEAM_NAME"] in self.teams:
                self.teams[data["TEAM_NAME"]] = data["TEAM_ID"]

        # Player Table에서 전체 데이터 추출 후 저장
        self.sql = "SELECT * FROM player"
        cursor.execute(self.sql)
        all_data = cursor.fetchall()

        # 검색 결과 딕셔너리 초기화
        self.result = {}

        # ComboBox Item 추가를 위해 추출
        # Team은 Team Table에서 추출한 데이터를 이용해 Item 추가
        team = []
        position = []
        nation = []
        for player in all_data:
            if player["POSITION"] != None:
                position.append(player["POSITION"])
            if player["NATION"] != None:
                nation.append(player["NATION"])
        for t in list(self.teams.keys()):
            team.append(t)
        team = list(set(team))
        position = list(set(position))
        nation = list(set(nation))
        team.append("ALL")      # Default로 조건이 따로 설정되지 않은 ALL을 위해 추가
        position.append("ALL")
        nation.append("ALL")
        team.sort()             # 정렬시 ALL이 맨 위로 올라오기 때문에 Default 값 설정을 따로 하지 않아도 됨
        position.sort()
        nation.sort()

        # 각 검색 조건(팀명, 포지션, 출신국, 키, 몸무게) 저장을 위한 멤버 변수 설정
        self.teamCondition = ""
        self.positionCondition = ""
        self.nationCondition = ""
        self.heightCondition = ""
        self.weightCondition = ""

        # 최상단 세부 검색 기능을 위한 위젯 그룹화
        topGroupBox = QGroupBox("선수 검색")
        topGroupBox.setStyleSheet("QGroupBox { border: 0px }")

        # 팀명, 포지션, 출신국 (ComboBox), 초기화 버튼 위젯 설정
        topLayout1 = QGridLayout()
        self.blankLabel = QLabel(" ")
        self.teamLabel = QLabel("팀명 : ")
        self.teamLabel.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        topLayout1.addWidget(self.teamLabel, 1, 0)
        self.teamCombo = QComboBox(self.teamLabel)
        self.teamCombo.addItems(team)
        self.teamCombo.activated.connect(self.teamCombo_Activated)
        topLayout1.addWidget(self.teamCombo, 1, 1)
        self.positionLabel = QLabel("포지션 : ")
        self.positionLabel.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        topLayout1.addWidget(self.positionLabel, 1, 2)
        self.positionCombo = QComboBox(self.positionLabel)
        self.positionCombo.addItems(position)
        self.positionCombo.activated.connect(self.positionCombo_Activated)
        topLayout1.addWidget(self.positionCombo, 1, 3)
        self.nationLabel = QLabel("출신국 : ")
        self.nationLabel.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        topLayout1.addWidget(self.nationLabel, 1, 4)
        self.nationCombo = QComboBox(self.nationLabel)
        self.nationCombo.addItems(nation)
        self.nationCombo.activated.connect(self.nationCombo_Activated)
        topLayout1.addWidget(self.nationCombo, 1, 5)
        topLayout1.addWidget(self.blankLabel, 1, 6)
        self.resetButton = QPushButton("초기화")
        self.resetButton.setFixedWidth(100)
        self.resetButton.clicked.connect(self.reset_Clicked)
        topLayout1.addWidget(self.resetButton, 1, 7)

        # 키, 몸무게 (LineEdit, RadioButton 포함), 검색 버튼 위젯 설정
        topLayout2 = QGridLayout()
        self.heightLabel = QLabel("키 : ")
        self.heightLabel.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        topLayout2.addWidget(self.heightLabel, 0, 0)
        self.heightEdit = QLineEdit(self.heightLabel)
        self.heightEdit.setFixedWidth(100)
        self.heightEdit.textChanged.connect(self.height_Check)
        topLayout2.addWidget(self.heightEdit, 0, 1)
        heightGroup = QGroupBox()
        heightLayout = QHBoxLayout()
        self.heightOver = QRadioButton("이상", self.heightEdit)
        self.heightOver.setChecked(True)
        heightLayout.addWidget(self.heightOver)
        self.heightUnder = QRadioButton("이하", self.heightEdit)
        heightLayout.addWidget(self.heightUnder)
        heightGroup.setLayout(heightLayout)
        heightGroup.setStyleSheet("QGroupBox { border: 0px }")
        topLayout2.addWidget(heightGroup, 0, 2)
        self.weightLabel = QLabel("몸무게 : ")
        self.weightLabel.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        topLayout2.addWidget(self.weightLabel, 0, 3)
        self.weightEdit = QLineEdit(self.weightLabel)
        self.weightEdit.setFixedWidth(100)
        self.weightEdit.textChanged.connect(self.weight_Check)
        topLayout2.addWidget(self.weightEdit, 0, 4)
        weightGroup = QGroupBox()
        weightLayout = QHBoxLayout()
        self.weightOver = QRadioButton("이상", self.weightLabel)
        self.weightOver.setChecked(True)
        weightLayout.addWidget(self.weightOver)
        self.weightUnder = QRadioButton("이하", self.weightLabel)
        weightLayout.addWidget(self.weightUnder)
        weightGroup.setLayout(weightLayout)
        weightGroup.setStyleSheet("QGroupBox { border: 0px }")
        topLayout2.addWidget(weightGroup, 0, 5)
        topLayout2.addWidget(self.blankLabel, 0, 6)
        self.searchButton = QPushButton("검색")
        self.searchButton.setFixedWidth(100)
        self.searchButton.clicked.connect(self.search_Clicked)
        topLayout2.addWidget(self.searchButton, 0, 7)

        # 검색 결과 출력 테이블 위젯 설정
        resultLayout = QVBoxLayout()
        self.resultTable = QTableWidget(self)
        resultLayout.addWidget(self.resultTable)

        # 하단 저장 기능을 위한 위젯 그룹화
        saveGroupBox = QGroupBox("파일 출력")
        saveGroupBox.setStyleSheet("QGroupBox { border: 0px }")

        saveLayout = QGridLayout()
        saveLayout.addWidget(self.blankLabel, 0, 0)
        saveLayout.addWidget(self.blankLabel, 1, 0)
        self.saveCSV = QRadioButton("CSV")
        self.saveCSV.setChecked(True)
        # self.saveCSV.clicked.connect(self.saveOption_Clicked)
        saveLayout.addWidget(self.saveCSV, 1, 1)
        self.saveJSON = QRadioButton("JSON")
        # self.saveJSON.clicked.connect(self.saveOption_Clicked)
        saveLayout.addWidget(self.saveJSON, 1, 2)
        self.saveXML = QRadioButton("XML")
        # self.saveXML.clicked.connect(self.saveOption_Clicked)
        saveLayout.addWidget(self.saveXML, 1, 3)
        saveLayout.addWidget(self.blankLabel, 1, 4)
        saveLayout.addWidget(self.blankLabel, 1, 5)
        saveLayout.addWidget(self.blankLabel, 1, 6)
        self.saveButton = QPushButton("저장")
        self.saveButton.setFixedWidth(100)
        self.saveButton.clicked.connect(self.save_Clicked)
        saveLayout.addWidget(self.saveButton, 1, 7)

        saveLayout.setContentsMargins(20, 20, 20, 0)
        saveGroupBox.setLayout(saveLayout)

        # 전체 레이아웃 그룹화
        topLayout = QVBoxLayout()
        topLayout.setContentsMargins(20, 20, 20, 0)
        topLayout.addLayout(topLayout1)
        topLayout.addLayout(topLayout2)
        topLayout.addLayout(resultLayout)
        topGroupBox.setLayout(topLayout)

        # 메인 레이아웃으로 병합 (Window Size에 따라 Layout과 Widget의 크기가 변경)
        mainLayout = QVBoxLayout()
        mainLayout.addWidget(topGroupBox)
        mainLayout.addWidget(saveGroupBox)

        self.setLayout(mainLayout)

    # ComboBox의 Item을 클릭했을 때, 처리 루틴
    def teamCombo_Activated(self):
        self.teamCondition = ""
        if self.teamCombo.currentText() != "ALL":
            self.teamCondition = "TEAM_ID = '" + self.teams[self.teamCombo.currentText()] + "'"
    def positionCombo_Activated(self):
        self.positionCondition = ""
        if self.positionCombo.currentText() != "ALL":
            self.positionCondition = "POSITION = '" + self.positionCombo.currentText() + "'"
    def nationCombo_Activated(self):
        self.nationCondition = ""
        if self.nationCombo.currentText() != "ALL":
            self.nationCondition = "NATION = '" + self.nationCombo.currentText() + "'"

    # 키, 몸무게 입력 시 정수가 아닌 경우 재입력하는 루틴
    def height_Check(self):
        self.heightCondition = ""
        if self.heightEdit.text() != "" and self.heightEdit.text().isnumeric() == False:
            self.heightEdit.setText("")
            QMessageBox.information(self, "입력 오류", "정수를 입력하세요.")
    def weight_Check(self):
        self.weightCondition = ""
        if self.weightEdit.text() != "" and self.weightEdit.text().isnumeric() == False:
            self.weightEdit.setText("")
            QMessageBox.information(self, "입력 오류", "정수를 입력하세요.")

    def reset_Clicked(self):
        self.teamCondition = self.positionCondition = self.nationCondition = self.heightCondition = self.weightCondition = ""
        self.teamCombo.setCurrentIndex(0)
        self.positionCombo.setCurrentIndex(0)
        self.nationCombo.setCurrentIndex(0)
        self.heightEdit.setText("")
        self.weightEdit.setText("")

        self.resultTable.setRowCount(0)
        self.resultTable.setColumnCount(0)
        self.result = {}
        QMessageBox.about(self, "실행 결과", "초기화가 완료 됐습니다.")

    def search_Clicked(self):
        self.sql = "SELECT * FROM player"

        # 키, 몸무게에 값이 존재하는 지 확인한 후 검색 전 검색 조건 저장
        if self.heightEdit.text() != "":
            self.heightCondition = "HEIGHT "
            if self.heightOver.isChecked():
                self.heightCondition += "> " + self.heightEdit.text()
            else:
                self.heightCondition += "< " + self.heightEdit.text()
        if self.weightEdit.text() != "":
            self.weightCondition = "WEIGHT "
            if self.weightOver.isChecked():
                self.weightCondition += "> " + self.weightEdit.text()
            else:
                self.weightCondition += "< " + self.weightEdit.text()

        # AND 조건을 위해 TEAM, POSITION, NATION, HEIGHT, WEIGHT 조건이 존재하는지 확인
        self.condition_List = [self.teamCondition, self.positionCondition, self.nationCondition, self.heightCondition, self.weightCondition]
        # print(self.condition_List)
        self.condition_Count = 0
        for data in self.condition_List:
            if data != "":
                self.condition_Count += 1

        # 조건이 1개 이상 존재할 경우 쿼리에 WHERE 문 추가
        if self.condition_Count >= 1:
            self.sql += " WHERE "
            for data in self.condition_List:
                if data != "":
                    self.sql += data + " AND "
            # 맨 마지막에 " AND " 문자열이 존재하는 경우 삭제
            if self.sql[-5:] == " AND ":
                self.sql = self.sql[:-5]

        cursor.execute(self.sql)
        self.result = cursor.fetchall()

        self.update_Table()

    # Window 중간에 위치한 TableWidget에 쿼리 결과를 반영
    def update_Table(self):
        # 검색된 결과가 0일 때 처리
        if len(self.result) == 0:
            QMessageBox.about(self, "검색 결과", "검색된 선수가 없습니다.")
            return -1

        columnNames = list(self.result[0].keys())
        self.resultTable.setRowCount(len(self.result))
        self.resultTable.setColumnCount(len(self.result[0].keys()))
        self.resultTable.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.resultTable.setHorizontalHeaderLabels(columnNames)

        for player in self.result:
            rowIDX = self.result.index(player)
            for k, v in player.items():
                columnIDX = list(player.keys()).index(k)
                if type(v) == datetime.date:
                    item = QTableWidgetItem(v.strftime("%Y-%m-%d"))
                elif type(v) == int:
                    item = QTableWidgetItem(str(v))
                else:
                    if k == "POSITION" and v == None:
                        item = QTableWidgetItem("미정")
                    elif k == "NATION" and v == None:
                        item = QTableWidgetItem("대한민국")
                    else:
                        item = QTableWidgetItem(v)
                self.resultTable.setItem(rowIDX, columnIDX, item)

        self.resultTable.resizeRowsToContents()
        self.resultTable.resizeColumnsToContents()


    # 저장 옵션 클릭 시 처리 루틴
    # def saveOption_Clicked(self):
    #     if self.saveCSV.isChecked():
    #         print("CSV")
    #     elif self.saveJSON.isChecked():
    #         print("JSON")
    #     elif self.saveXML.isChecked():
    #         print("XML")

    # 저장 버튼 클릭 시 처리 루틴
    def save_Clicked(self):
        # 검색 테이블에 결과가 없을 경우 저장하지 않고 경고창 띄움
        if len(self.result) == 0:
            QMessageBox.information(self, "실행 결과", "검색된 선수가 없습니다.")
            return -1

        if self.saveCSV.isChecked():
            self.save_CSV()
        elif self.saveJSON.isChecked():
            self.save_JSON()
        else:
            self.save_XML()
        QMessageBox.about(self, "실행 결과", "현재 폴더에 검색 결과가 파일로 저장 됐습니다.")

    # Python Dictionary를 CSV 파일로 변환
    def save_CSV(self):
        with open("player.csv", "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)

            columnNames = list(self.result[0].keys())
            writer.writerow(columnNames)

            for player in self.result:
                modified = player
                if player["POSITION"] == None:
                    modified["POSITION"] = "미정"
                if player["NATION"] == None:
                    modified["NATION"] = "대한민국"

                row = list(modified.values())
                writer.writerow(row)

    # Python Dictionary를 JSON 파일로 변환
    def save_JSON(self):
        modified = self.result
        for player in modified:
            for k, v in player.items():
                if isinstance(v, datetime.date):
                    player[k] = v.strftime("%Y-%m-%d")
                elif k == "POSITION" and player[k] == None:
                    player[k] = "미정"
                elif k == "NATION" and player[k] == None:
                    player[k] = "대한민국"

        saveDict = dict(Player = modified)
        with open("player.json", "w", encoding="utf-8") as f:
            json.dump(saveDict, f, indent=4, ensure_ascii=False)

    # Python Dictionary를 XML 파일로 변환
    def save_XML(self):
        modified = self.result
        for player in modified:
            for k, v in player.items():
                if isinstance(v, datetime.date):
                    player[k] = v.strftime("%Y-%m-%d")
                elif k == "POSITION" and player[k] == None:
                    player[k] = "미정"
                elif k == "NATION" and player[k] == None:
                    player[k] = "대한민국"

        saveDict = dict(Player = modified)

        tableName = list(saveDict.keys())[0]
        tableRows = list(saveDict.values())[0]

        rootElement = ET.Element("TABLE")
        rootElement.attrib["name"] = tableName

        for row in tableRows:
            rowElement = ET.Element("ROW")
            rootElement.append(rowElement)

            for columnName in list(row.keys()):
                if row[columnName] == None:
                    if columnName == "POSITION":
                        rowElement.attrib[columnName] = "미정"
                    elif columnName == "NATION":
                        rowElement.attrib[columnName] = "대한민국"
                    else:
                        rowElement.attrib[columnName] = ""
                else:
                    rowElement.attrib[columnName] = row[columnName]

                if type(row[columnName]) == int:
                    rowElement.attrib[columnName] = str(row[columnName])

        ET.ElementTree(rootElement).write("player.xml", encoding="utf-8", xml_declaration=True)


# GUI Program Execute
def main():
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())
    conn.close()

main()

