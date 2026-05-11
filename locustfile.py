from locust import HttpUser, task, between

class UsuarioHotSale(HttpUser):
    wait_time = between(0.1, 0.5)  # tráfico agresivo

    @task(3)  # 30%
    def comprar(self):
        self.client.post(
            "/orders",
            params={
                "product_id": 1,
                "quantity": 1
            }
        )

    @task(7)  # 70%
    def ver_catalogo(self):
        self.client.get("/products")