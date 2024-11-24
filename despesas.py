from kivymd.app import MDApp
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.list import MDList, OneLineListItem
from kivy.uix.scrollview import ScrollView
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
import sqlite3

# Funções para interagir com o banco de dados
def init_db():
    conn = sqlite3.connect("controle_gastos.db")
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS gastos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome_gasto TEXT,
        valor REAL
    );
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS renda (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        valor REAL
    );
    """)
    conn.commit()
    conn.close()

def salvar_renda(renda):
    conn = sqlite3.connect("controle_gastos.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM renda")
    cursor.execute("INSERT INTO renda (valor) VALUES (?)", (renda,))
    conn.commit()
    conn.close()

def obter_renda():
    conn = sqlite3.connect("controle_gastos.db")
    cursor = conn.cursor()
    cursor.execute("SELECT valor FROM renda LIMIT 1")
    renda = cursor.fetchone()
    conn.close()
    return renda[0] if renda else 0.0

def adicionar_gasto(nome_gasto, valor):
    conn = sqlite3.connect("controle_gastos.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO gastos (nome_gasto, valor) VALUES (?, ?)", (nome_gasto, valor))
    conn.commit()
    conn.close()

def obter_gastos():
    conn = sqlite3.connect("controle_gastos.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, nome_gasto, valor FROM gastos")
    gastos = cursor.fetchall()
    conn.close()
    return gastos

def excluir_gasto(id):
    conn = sqlite3.connect("controle_gastos.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM gastos WHERE id = ?", (id,))
    conn.commit()
    conn.close()

def editar_gasto(id, nome_gasto, valor):
    conn = sqlite3.connect("controle_gastos.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE gastos SET nome_gasto = ?, valor = ? WHERE id = ?", (nome_gasto, valor, id))
    conn.commit()
    conn.close()

# Classe principal do aplicativo
class ControleGastos(MDBoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.padding = dp(10)
        self.spacing = dp(10)

        # Campo para a renda mensal com vírgula
        self.renda_field = MDTextField(
            hint_text="Digite sua renda mensal",
            input_filter="float",
            on_text_validate=self.on_renda_text_validate
        )
        self.add_widget(self.renda_field)

        # Campo para o nome do gasto
        self.nome_gasto_field = MDTextField(
            hint_text="Nome do Gasto",
        )
        self.add_widget(self.nome_gasto_field)

        # Campo para adicionar o valor do gasto
        self.gasto_field = MDTextField(
            hint_text="Digite o valor do gasto",
        )
        self.add_widget(self.gasto_field)

        # Botão para adicionar o gasto à lista
        self.add_gasto_button = MDRaisedButton(
            text="Adicionar Gasto",
            on_release=self.adicionar_gasto,
        )
        self.add_widget(self.add_gasto_button)

        # Lista de gastos
        self.gastos_lista = MDList()
        self.scroll_lista = ScrollView()
        self.scroll_lista.add_widget(self.gastos_lista)
        self.add_widget(self.scroll_lista)

        # Label para mostrar o total das despesas
        self.despesas_totais_label = MDLabel(
            text="Despesas Totais: R$ 0.00",
            halign="center",
        )
        self.add_widget(self.despesas_totais_label)

        # Label para mostrar o total gasto no mês
        self.total_gasto_label = MDLabel(
            text="Total Gasto no Mês: R$ 0.00",
            halign="center",
        )
        self.add_widget(self.total_gasto_label)

        # Botão para calcular saldo final
        self.calcular_button = MDRaisedButton(
            text="Calcular Saldo",
            on_release=self.calcular_saldo,
        )
        self.add_widget(self.calcular_button)

        # Label para mostrar o saldo final
        self.saldo_label = MDLabel(
            text="Saldo Final: R$ 0.00",
            halign="center",
        )
        self.add_widget(self.saldo_label)

        # Armazena os gastos
        self.gastos = []
        self.gasto_editado = None  # Variável para controlar a edição de gasto

        # Carregar dados ao iniciar
        self.carregar_dados()

    def carregar_dados(self):
        # Carregar renda
        renda = obter_renda()
        self.renda_field.text = f"{renda:,.2f}".replace(",", "_").replace(".", ",").replace("_", ".")
        
        # Carregar gastos
        self.gastos = obter_gastos()
        self.atualizar_lista_gastos()
        self.atualizar_totais()

    def on_renda_text_validate(self, instance):
        renda = float(instance.text.replace(",", "."))
        salvar_renda(renda)
        self.carregar_dados()  # Atualiza a renda e lista

    def adicionar_gasto(self, instance):
        nome_gasto = self.nome_gasto_field.text
        valor_gasto = float(self.gasto_field.text)
        if nome_gasto and valor_gasto:
            adicionar_gasto(nome_gasto, valor_gasto)
            self.carregar_dados()
            self.nome_gasto_field.text = ""
            self.gasto_field.text = ""

    def atualizar_lista_gastos(self):
        self.gastos_lista.clear_widgets()
        for gasto in self.gastos:
            item = OneLineListItem(
                text=f"{gasto[1]}: R$ {gasto[2]:,.2f}",
                on_release=lambda item, gasto=gasto: self.excluir_gasto(gasto[0]),
            )
            self.gastos_lista.add_widget(item)

    def excluir_gasto(self, id):
        excluir_gasto(id)
        self.carregar_dados()

    def atualizar_totais(self):
        total_gasto = sum(gasto[2] for gasto in self.gastos)
        self.despesas_totais_label.text = f"Despesas Totais: R$ {total_gasto:,.2f}"
        saldo = obter_renda() - total_gasto
        self.saldo_label.text = f"Saldo Final: R$ {saldo:,.2f}"

    def calcular_saldo(self, instance):
        self.atualizar_totais()

class MyApp(MDApp):
    def build(self):
        init_db()  # Inicializa o banco de dados
        return ControleGastos()

if __name__ == "__main__":
    MyApp().run()
