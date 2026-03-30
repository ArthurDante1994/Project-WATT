import tkinter as tk


def calcular(operacao: str, numero_a: float, numero_b: float) -> float:
	if operacao == "+":
		return numero_a + numero_b
	if operacao == "-":
		return numero_a - numero_b
	if operacao == "*":
		return numero_a * numero_b
	if operacao == "/":
		if numero_b == 0:
			raise ZeroDivisionError("Erro")
		return numero_a / numero_b
	raise ValueError("Operacao invalida")


class CalculadoraApp:
	def __init__(self, janela: tk.Tk) -> None:
		self.janela = janela
		self.janela.title("Calculadora")
		self.janela.geometry("360x540")
		self.janela.resizable(False, False)
		self.janela.configure(bg="#f1f1f1")

		self.valor_tela = "0"
		self.primeiro_numero: float | None = None
		self.operacao: str | None = None
		self.novo_numero = True

		self.display_var = tk.StringVar(value=self.valor_tela)
		self._montar_interface()

	def _montar_interface(self) -> None:
		frame_tela = tk.Frame(self.janela, bg="#f1f1f1")
		frame_tela.pack(fill="x", padx=12, pady=(14, 10))

		tk.Label(
			frame_tela,
			text="Padrao",
			font=("Segoe UI", 16, "bold"),
			bg="#f1f1f1",
			anchor="w",
		).pack(fill="x")

		tk.Label(
			frame_tela,
			textvariable=self.display_var,
			font=("Segoe UI", 40, "bold"),
			bg="#f1f1f1",
			anchor="e",
		).pack(fill="x", pady=(18, 0))

		frame_botoes = tk.Frame(self.janela, bg="#f1f1f1")
		frame_botoes.pack(fill="both", expand=True, padx=8, pady=8)

		for indice in range(4):
			frame_botoes.grid_columnconfigure(indice, weight=1)
		for indice in range(5):
			frame_botoes.grid_rowconfigure(indice, weight=1)

		botoes = [
			("7", 0, 0, lambda: self._adicionar_numero("7")),
			("8", 0, 1, lambda: self._adicionar_numero("8")),
			("9", 0, 2, lambda: self._adicionar_numero("9")),
			("/", 0, 3, lambda: self._definir_operacao("/")),
			("4", 1, 0, lambda: self._adicionar_numero("4")),
			("5", 1, 1, lambda: self._adicionar_numero("5")),
			("6", 1, 2, lambda: self._adicionar_numero("6")),
			("*", 1, 3, lambda: self._definir_operacao("*")),
			("1", 2, 0, lambda: self._adicionar_numero("1")),
			("2", 2, 1, lambda: self._adicionar_numero("2")),
			("3", 2, 2, lambda: self._adicionar_numero("3")),
			("-", 2, 3, lambda: self._definir_operacao("-")),
			("0", 3, 0, lambda: self._adicionar_numero("0")),
			(".", 3, 1, self._adicionar_decimal),
			("C", 3, 2, self._limpar),
			("+", 3, 3, lambda: self._definir_operacao("+")),
			("=", 4, 0, self._calcular_resultado),
		]

		for texto, linha, coluna, comando in botoes:
			largura_coluna = 4 if texto == "=" else 1
			cor = "#ffffff"
			cor_texto = "#202020"
			if texto in {"+", "-", "*", "/", "="}:
				cor = "#dbeafe" if texto != "=" else "#0b67c2"
				cor_texto = "#202020" if texto != "=" else "#ffffff"

			tk.Button(
				frame_botoes,
				text=texto,
				font=("Segoe UI", 18),
				bg=cor,
				fg=cor_texto,
				activebackground=cor,
				relief="flat",
				command=comando,
			).grid(
				row=linha,
				column=coluna,
				columnspan=largura_coluna,
				sticky="nsew",
				padx=3,
				pady=3,
			)

	def _adicionar_numero(self, digito: str) -> None:
		if self.novo_numero or self.valor_tela == "0":
			self.valor_tela = digito
			self.novo_numero = False
		else:
			self.valor_tela += digito
		self.display_var.set(self.valor_tela)

	def _adicionar_decimal(self) -> None:
		if self.novo_numero:
			self.valor_tela = "0."
			self.novo_numero = False
		elif "." not in self.valor_tela:
			self.valor_tela += "."
		self.display_var.set(self.valor_tela)

	def _definir_operacao(self, operacao: str) -> None:
		try:
			self.primeiro_numero = float(self.valor_tela)
		except ValueError:
			self._mostrar_erro()
			return
		self.operacao = operacao
		self.novo_numero = True

	def _calcular_resultado(self) -> None:
		if self.primeiro_numero is None or self.operacao is None:
			return

		try:
			segundo_numero = float(self.valor_tela)
			resultado = calcular(self.operacao, self.primeiro_numero, segundo_numero)
			self.valor_tela = str(int(resultado)) if resultado.is_integer() else str(resultado)
			self.display_var.set(self.valor_tela)
			self.primeiro_numero = None
			self.operacao = None
			self.novo_numero = True
		except (ValueError, ZeroDivisionError):
			self._mostrar_erro()

	def _limpar(self) -> None:
		self.valor_tela = "0"
		self.primeiro_numero = None
		self.operacao = None
		self.novo_numero = True
		self.display_var.set(self.valor_tela)

	def _mostrar_erro(self) -> None:
		self.valor_tela = "Erro"
		self.display_var.set(self.valor_tela)
		self.primeiro_numero = None
		self.operacao = None
		self.novo_numero = True


def main() -> None:
	app = tk.Tk()
	CalculadoraApp(app)
	app.mainloop()


if __name__ == "__main__":
    main()
