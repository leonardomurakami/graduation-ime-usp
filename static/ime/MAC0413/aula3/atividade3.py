class Item:
    def __init__(self, preco, quantidade):
        pass

    def get_desconto(self):
        return (self.get_subtotal() * self.discount)

    def get_subtotal(self):
        return (self.preco*self.quantidade)

class Livro(Item):
    def __init__(self, preco, quantidade):
        self.type = "LIVRO"
        self.preco = preco
        self.quantidade = quantidade
        self.discount = 0.05

class Eletronico(Item):
    def __init__(self, preco, quantidade):
        self.type = "ELETRONICO"
        self.preco = preco
        self.quantidade = quantidade
        self.discount = 0.02

class Outro(Item):
    def __init__(self, preco, quantidade):
        self.type = "OUTRO"
        self.preco = preco
        self.quantidade = quantidade
        self.discount = 0.0

class Cliente:
    def __init__(self, tipo, desconto):
        self.tipo = tipo
        self.desconto = desconto

    def get_desconto(self):
        return self.desconto

class ClienteComum(Cliente):
    def __init__(self):
        super().__init__("COMUM", 0.0)

class ClientePremium(Cliente):
    def __init__(self):
        super().__init__("PREMIUM", 0.10)

class Entrega:
    def __init__(self, tipo):
        self.tipo = tipo

    def get_valor_frete(self, valor_pedido):
        pass

class Retirada(Entrega):
    def __init__(self):
        super().__init__("RETIRADA")

    def get_valor_frete(self, valor_pedido):
        return 0.0

class Normal(Entrega):
    def __init__(self):
        super().__init__("NORMAL")

    def get_valor_frete(self, valor_pedido):
        return 12.0 if valor_pedido < 150.0 else 0.0


class Expressa(Entrega):
    def __init__(self):
        super().__init__("NORMAL")

    def get_valor_frete(self, valor_pedido):
        return 25.0

class Pedido:
    def __init__(self, cliente: Cliente, entrega: Entrega):
        self.cliente: Cliente = cliente
        self.entrega: Entrega = entrega
        self.items = []

    def adicionar_item(self, item: Item):
        self.items.append(item)

    def get_subtotal(self):
        subtotal_items = 0.0
        for item in self.items:
            subtotal_items += item.get_subtotal()
        return subtotal_items

    def get_desconto_items(self):
        desconto_items = 0.0
        for item in self.items:
            desconto_items += item.get_desconto()
        return desconto_items

    def get_desconto(self):
        subtotal_items = self.get_subtotal()
        desconto_items = self.get_desconto_items()

        return ((subtotal_items - desconto_items) * self.cliente.get_desconto()) + desconto_items

    def get_frete(self):
        return self.entrega.get_valor_frete(self.get_subtotal() - self.get_desconto()) 

    def get_total(self):
        return self.get_subtotal() - self.get_desconto() + self.get_frete()

    def display(self):
        subtotal, desconto, frete, total = self.get_subtotal(), self.get_desconto(), self.get_frete(), self.get_total()
        print(f"SUBTOTAL={subtotal:.2f}")
        print(f"DESCONTO={desconto:.2f}")
        print(f"FRETE={frete:.2f}")
        print(f"TOTAL={total:.2f}")

def main():

    cliente = {
        "COMUM": ClienteComum,
        "PREMIUM": ClientePremium
    }

    entrega = {
        "RETIRADA": Retirada,
        "NORMAL": Normal,
        "EXPRESSA": Expressa
    }

    item = {
        "LIVRO": Livro,
        "ELETRONICO": Eletronico,
        "OUTRO": Outro
    }

    cliente_input = cliente[input().strip()]()
    entrega_input = entrega[input().strip()]()

    pedido = Pedido(cliente_input, entrega_input)
    n = int(input().strip())

    for _ in range(n):
        categoria, preco, quantidade = input().split()
        item_input = item[categoria](float(preco), int(quantidade))
        pedido.adicionar_item(item_input)

    pedido.display()


if __name__ == "__main__":
    main()