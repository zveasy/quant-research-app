"""Start PySyft GridNetwork with dummy clients."""
import syft as sy


def main() -> None:
    network = sy.GridNetwork(name="quant-grid", sqlite=True)
    for i in range(3):
        network.create_client(name=f"client_{i}")
    network.start()


if __name__ == "__main__":
    main()
