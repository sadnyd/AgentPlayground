from streamlit.testing.v1 import AppTest

def test_app():
    at = AppTest.from_file("app.py")
    at.run()

    # Check if the title is correct
    assert "Agent Playground" in at.title[0].value

    # Check if there is a chat input
    assert len(at.chat_input) > 0

    # Type a message and submit
    at.chat_input[0].set_value("Hello").run()
    at.run()

    # Check if the user message and assistant message are there
    chat_msgs = at.chat_message
    assert len(chat_msgs) >= 2

    print("Test passed successfully!")

if __name__ == "__main__":
    test_app()
