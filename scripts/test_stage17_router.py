from src.agents.router import detect_intent
from src.agents.orchestrator import run_orchestrator


def print_test(message):
    print()
    print("=" * 70)
    print("MESSAGE:", message)
    print("ROUTER:", detect_intent(message))
    print("ORCHESTRATOR:")
    print(run_orchestrator(message))


if __name__ == "__main__":
    print_test("Check renewal risk")
    print_test("Why is this claim suspicious for fraud?")
    print_test("I need an underwriting assessment")
    print_test("Explain my insurance portfolio")
