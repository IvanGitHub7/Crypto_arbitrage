import sys

from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QTableWidget, QTableWidgetItem,
    QHeaderView, QGroupBox, QCheckBox, QTextEdit, QMessageBox
)
from PyQt6.QtCore import Qt
from crypto_arbitrage.core.arbitrage_engine import ArbitrageEngine
from crypto_arbitrage.utils.async_qt import AsyncQtBridge
from crypto_arbitrage.utils.debug_logger import logger


class CryptoArbitrageGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.arbitrage = ArbitrageEngine()
        self.async_bridge = AsyncQtBridge()
        self.opportunities = []
        self.init_ui()
        self._connect_signals()

    def init_ui(self):
        self.setWindowTitle('Crypto Arbitrage Finder (Spot & Futures)')
        self.setGeometry(100, 100, 1400, 900)

        main_widget = QWidget()
        layout = QVBoxLayout(main_widget)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)

        # Control Panel
        control_panel = QWidget()
        control_layout = QHBoxLayout(control_panel)
        control_layout.setContentsMargins(0, 0, 0, 0)

        # Input Fields
        self.investment_input = QLineEdit('10000')
        self.min_profit_input = QLineEdit('0.1')
        self.max_profit_input = QLineEdit('10')

        # Analysis Types Group
        analysis_group = QGroupBox("Analysis Types")
        analysis_layout = QHBoxLayout()
        self.spot_spot_cb = QCheckBox("Spot-Spot", checked=True)
        self.spot_futures_cb = QCheckBox("Spot-Futures")
        self.futures_futures_cb = QCheckBox("Futures-Futures")
        analysis_layout.addWidget(self.spot_spot_cb)
        analysis_layout.addWidget(self.spot_futures_cb)
        analysis_layout.addWidget(self.futures_futures_cb)
        analysis_group.setLayout(analysis_layout)

        # Exchanges Group
        exchanges_group = QGroupBox("Exchanges")
        exchanges_layout = QVBoxLayout()
        self.exchange_checkboxes = {}
        exchanges = ['Binance', 'KuCoin', 'Bybit', 'OKX', 'Huobi']

        for exchange in exchanges:
            cb = QCheckBox(exchange, checked=True)
            self.exchange_checkboxes[exchange] = cb
            exchanges_layout.addWidget(cb)
        exchanges_group.setLayout(exchanges_layout)

        # Buttons
        self.start_btn = QPushButton('Start/Refresh')
        self.start_btn.clicked.connect(self.start_arbitrage)

        self.debug_btn = QPushButton('Debug Info')
        self.debug_btn.clicked.connect(self.show_debug_info)
        self.debug_btn.setStyleSheet("background-color: #f39c12;")

        control_layout.addWidget(QLabel('Investment ($):'))
        control_layout.addWidget(self.investment_input)
        control_layout.addWidget(QLabel('Min Spread (%):'))
        control_layout.addWidget(self.min_profit_input)
        control_layout.addWidget(QLabel('Max Spread (%):'))
        control_layout.addWidget(self.max_profit_input)
        control_layout.addWidget(analysis_group)
        control_layout.addWidget(exchanges_group)
        control_layout.addStretch()
        control_layout.addWidget(self.start_btn)
        control_layout.addWidget(self.debug_btn)

        # Results Table
        self.table = QTableWidget()
        self.table.setColumnCount(10)
        self.table.setHorizontalHeaderLabels([
            'Pair', 'Buy Exchange', 'Buy Market',
            'Sell Exchange', 'Sell Market', 'Buy Price',
            'Sell Price', 'Spread %', 'Profit $', 'Investment'
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        # Log Output
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setMaximumHeight(200)

        # Initialize logger
        logger.output_widget = self.log_output

        layout.addWidget(control_panel)
        layout.addWidget(self.table)
        layout.addWidget(QLabel("Log Output:"))
        layout.addWidget(self.log_output)

        self.setCentralWidget(main_widget)
        self.apply_styles()

    def apply_styles(self):
        self.setStyleSheet("""
            QMainWindow { background-color: #2D2D2D; }
            QLabel { color: #FFFFFF; }
            QTableWidget { 
                background-color: #252525; 
                color: #FFFFFF;
                gridline-color: #444;
            }
            QHeaderView::section { 
                background-color: #252525; 
                color: #DDDDDD;
                padding: 5px;
                border: none;
            }
            QLineEdit { 
                background-color: #252525; 
                color: #FFFFFF;
                border: 1px solid #444;
                padding: 5px;
                border-radius: 3px;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 5px 10px;
                border-radius: 3px;
                min-width: 80px;
            }
            QPushButton:hover { background-color: #45A049; }
            QGroupBox {
                color: #DDDDDD;
                border: 1px solid #444;
                border-radius: 5px;
                margin-top: 10px;
                padding: 10px 5px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px;
            }
            QTextEdit {
                background-color: #252525;
                color: #FFFFFF;
                border: 1px solid #444;
                font-family: Consolas, monospace;
            }
        """)

    def _connect_signals(self):
        self.async_bridge.update_signal.connect(self.update_status)
        self.async_bridge.finished.connect(self.display_results)

    def start_arbitrage(self):
        try:
            investment = float(self.investment_input.text())
            min_profit = float(self.min_profit_input.text())
            max_profit = float(self.max_profit_input.text())

            selected_exchanges = [
                name for name, cb in self.exchange_checkboxes.items()
                if cb.isChecked()
            ]

            if not selected_exchanges:
                QMessageBox.warning(self, "Warning", "Please select at least one exchange")
                return

            self.arbitrage.set_exchanges(selected_exchanges)
            self.arbitrage.set_analysis_types(
                self.spot_spot_cb.isChecked(),
                self.spot_futures_cb.isChecked(),
                self.futures_futures_cb.isChecked()
            )

            logger.log("\n=== STARTING ARBITRAGE SEARCH ===")
            logger.log(f"Exchanges: {selected_exchanges}")
            logger.log(f"Investment: ${investment:.2f}")
            logger.log(f"Spread range: {min_profit}% - {max_profit}%")

            self.async_bridge.start_arbitrage(
                self.arbitrage,
                min_profit=min_profit,
                max_profit=max_profit,
                investment=investment
            )

        except ValueError as e:
            logger.log(f"Error: Invalid input values - {str(e)}")
            QMessageBox.critical(self, "Error", "Please enter valid numbers")

    def show_debug_info(self):
        """Принудительный вывод отладочной информации"""
        debug_info = []
        debug_info.append("\n=== DEBUG INFORMATION ===")
        debug_info.append(f"Active exchanges: {list(self.arbitrage.active_exchanges.keys())}")
        debug_info.append(f"Analysis types: {self.arbitrage.analysis_types}")

        if hasattr(self.arbitrage, 'last_prices'):
            debug_info.append("\nLast prices sample:")
            for symbol, prices in list(self.arbitrage.last_prices.items())[:5]:
                debug_info.append(f"\n{symbol}:")
                for price in prices[:2]:  # Первые 2 записи
                    debug_info.append(
                        f"  {price['exchange']} {price['market_type']}: "
                        f"bid={price['bid']}, ask={price['ask']}"
                    )

        logger.log("\n".join(debug_info))

    def update_status(self, message):
        self.statusBar().showMessage(message)
        logger.log(message)

    def display_results(self, opportunities):
        self.opportunities = opportunities
        self.table.setRowCount(len(opportunities))

        for row, opp in enumerate(opportunities):
            for col, text in enumerate([
                opp['symbol'],
                opp['buy_exchange'],
                opp['buy_market_type'].capitalize(),
                opp['sell_exchange'],
                opp['sell_market_type'].capitalize(),
                f"{opp['buy_price']:.8f}".rstrip('0').rstrip('.'),
                f"{opp['sell_price']:.8f}".rstrip('0').rstrip('.'),
                f"{opp['spread_percent']:.2f}%",
                f"${opp['profit_amount']:.2f}",
                f"${opp['investment']:.2f}"
            ]):
                item = QTableWidgetItem(text)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

                # Цветовая маркировка по проценту спреда
                spread = opp['spread_percent']
                if spread > 5:
                    item.setBackground(QColor(0, 100, 0))  # Темно-зеленый
                elif spread > 2:
                    item.setBackground(QColor(0, 70, 0))  # Зеленый
                elif spread > 1:
                    item.setBackground(QColor(100, 100, 0))  # Желтый

                self.table.setItem(row, col, item)

        status = f"Found {len(opportunities)} opportunities"
        self.update_status(status)
        logger.log(status)

    def closeEvent(self, event):
        self.async_bridge.close()
        event.accept()


def main():
    app = QApplication(sys.argv)
    window = CryptoArbitrageGUI()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()