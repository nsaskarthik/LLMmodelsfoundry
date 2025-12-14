import argparse
import uuid

from services.agent_runtime import AgentRuntime
from services.core.modal_loader import modal_loader
from services.core.router import route_message
from services.integrations.iris_connector import IRISConnector


def main():
    parser = argparse.ArgumentParser(
        description="Dev Assistant (LangChain + Foundry Local)"
    )
    parser.add_argument("--user", "-u", default="Guest", help="User ID")
    parser.add_argument(
        "--router-llm",
        action="store_true",
        help="Use LLM-based routing (otherwise keyword routing).",
    )
    args = parser.parse_args()

    session_id = str(uuid.uuid4())

    # Initialize model + agent once
    llm = modal_loader.get_llm()
    agent = modal_loader.get_agent()

    runtime = AgentRuntime(user=args.user, agent=agent, llm=llm, session_id=session_id)

    print("Dev Assistant ready. Type 'exit' to quit.")
    while True:
        try:
            user_input = input("> ").strip()
            if user_input.lower() in {"exit", "quit"}:
                break
            if not user_input:
                continue

            # Decide routing strategy
            routing_llm = llm if args.router_llm else None
            mode = route_message(
                llm=routing_llm, user_input=user_input, session_id=session_id
            )

            # Execute the selected mode explicitly (avoid double-routing inside runtime.run)
            if mode == "AGENT":
                output = runtime._run_agent(user_input)
            else:
                output = runtime._run_llm_only(user_input)

            print(output)

        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"[ERROR] {e}")


if __name__ == "__main__":
    main()
