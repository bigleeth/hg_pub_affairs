import sys
import json
import os
from datetime import datetime
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
                             QHeaderView, QMessageBox, QPushButton)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor

class AssemblyMemberInfo(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("국회의원 정보")
        self.setGeometry(100, 100, 1200, 800)
        
        # 메인 위젯 설정
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 버튼 레이아웃
        button_layout = QHBoxLayout()
        self.refresh_button = QPushButton("데이터 새로고침")
        self.refresh_button.clicked.connect(self.refresh_data)
        button_layout.addWidget(self.refresh_button)
        layout.addLayout(button_layout)
        
        # 테이블 위젯 생성
        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels([
            "이름", "당선횟수", "선거구", "소속위원회", 
            "보좌관", "선임비서관", "비서관", "URL", "수집일시"
        ])
        
        # 테이블 헤더 설정
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        header.setStretchLastSection(True)
        
        # 테이블 스타일 설정
        self.table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #ccc;
                background-color: white;
            }
            QHeaderView::section {
                background-color: #f0f0f0;
                padding: 5px;
                border: 1px solid #ccc;
                font-weight: bold;
            }
            QTableWidget::item {
                padding: 5px;
            }
        """)
        
        layout.addWidget(self.table)
        
        # 스냅샷 파일 경로
        self.snapshot_file = 'assembly_member_snapshot.json'
        
        # 데이터 로드
        try:
            self.load_data()
        except Exception as e:
            QMessageBox.critical(self, "오류", f"데이터 로드 중 오류 발생: {str(e)}")
            sys.exit(1)
            
    def refresh_data(self):
        try:
            # 현재 데이터를 스냅샷으로 저장
            self.save_snapshot()
            
            # 데이터 수집 스크립트 실행
            os.system('python 국회의원실정보수집.py')
            
            # 새 데이터 로드 및 비교
            self.load_data()
            
            QMessageBox.information(self, "완료", "데이터가 새로고침되었습니다.")
        except Exception as e:
            QMessageBox.critical(self, "오류", f"데이터 새로고침 중 오류 발생: {str(e)}")
            
    def save_snapshot(self):
        try:
            with open('assembly_member_data.json', 'r', encoding='utf-8') as f:
                current_data = json.load(f)
                
            with open(self.snapshot_file, 'w', encoding='utf-8') as f:
                json.dump(current_data, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"스냅샷 저장 중 오류 발생: {str(e)}")
            
    def load_data(self):
        try:
            # 현재 데이터 로드
            with open('assembly_member_data.json', 'r', encoding='utf-8') as f:
                self.members_data = json.load(f)
                
            if not self.members_data:
                raise ValueError("JSON 파일이 비어있습니다.")
            
            # 스냅샷 데이터 로드 (있는 경우)
            snapshot_data = None
            if os.path.exists(self.snapshot_file):
                with open(self.snapshot_file, 'r', encoding='utf-8') as f:
                    snapshot_data = json.load(f)
            
            # 테이블 행 수 설정
            self.table.setRowCount(len(self.members_data))
            
            # 데이터 채우기
            for row, member in enumerate(self.members_data):
                # 이름
                name_item = QTableWidgetItem(member['국회의원']['이름'])
                self.table.setItem(row, 0, name_item)
                
                # 당선횟수
                election_item = QTableWidgetItem(member['국회의원']['당선횟수'].replace('\n', ' ').replace('\t', ''))
                self.table.setItem(row, 1, election_item)
                
                # 선거구
                district_item = QTableWidgetItem(member['국회의원']['선거구'])
                self.table.setItem(row, 2, district_item)
                
                # 소속위원회
                committee_item = QTableWidgetItem(member['국회의원']['소속위원회'])
                self.table.setItem(row, 3, committee_item)
                
                # 보좌관
                chief_staff_item = QTableWidgetItem(', '.join(member['보좌관']))
                self.table.setItem(row, 4, chief_staff_item)
                
                # 선임비서관
                senior_secretary_item = QTableWidgetItem(', '.join(member['선임비서관']))
                self.table.setItem(row, 5, senior_secretary_item)
                
                # 비서관
                secretary_item = QTableWidgetItem(', '.join(member['비서관']))
                self.table.setItem(row, 6, secretary_item)
                
                # URL
                url_item = QTableWidgetItem(member['메타데이터']['url'])
                self.table.setItem(row, 7, url_item)
                
                # 수집일시
                date_item = QTableWidgetItem(member['메타데이터']['수집일시'])
                self.table.setItem(row, 8, date_item)
                
                # 변경된 데이터 하이라이트
                if snapshot_data:
                    self.highlight_changes(row, member, snapshot_data)
                
            # 모든 셀을 읽기 전용으로 설정
            for row in range(self.table.rowCount()):
                for col in range(self.table.columnCount()):
                    item = self.table.item(row, col)
                    if item:
                        item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                        
        except FileNotFoundError:
            raise FileNotFoundError("assembly_member_data.json 파일을 찾을 수 없습니다.")
        except json.JSONDecodeError:
            raise ValueError("JSON 파일 형식이 올바르지 않습니다.")
        except Exception as e:
            raise Exception(f"데이터 로드 중 오류 발생: {str(e)}")
            
    def highlight_changes(self, row, current_member, snapshot_data):
        # 현재 의원의 URL로 스냅샷에서 해당 의원 찾기
        current_url = current_member['메타데이터']['url']
        snapshot_member = next((m for m in snapshot_data if m['메타데이터']['url'] == current_url), None)
        
        if not snapshot_member:
            return
            
        # 각 필드 비교 및 변경된 경우 하이라이트
        fields_to_check = [
            ('국회의원', '이름', 0),
            ('국회의원', '당선횟수', 1),
            ('국회의원', '선거구', 2),
            ('국회의원', '소속위원회', 3),
            ('보좌관', None, 4),
            ('선임비서관', None, 5),
            ('비서관', None, 6)
        ]
        
        for field, subfield, col in fields_to_check:
            if subfield:
                current_value = current_member[field][subfield]
                snapshot_value = snapshot_member[field][subfield]
            else:
                current_value = ', '.join(current_member[field])
                snapshot_value = ', '.join(snapshot_member[field])
                
            if current_value != snapshot_value:
                item = self.table.item(row, col)
                if item:
                    item.setBackground(QColor(255, 255, 0))  # 노란색 배경

if __name__ == '__main__':
    try:
        app = QApplication(sys.argv)
        window = AssemblyMemberInfo()
        window.show()
        sys.exit(app.exec())
    except Exception as e:
        print(f"프로그램 실행 중 오류 발생: {str(e)}")
        sys.exit(1) 