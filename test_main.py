from contextlib import redirect_stdout
from io import StringIO
import unittest
from unittest.mock import patch
from types import SimpleNamespace
import tempfile
import json
from pathlib import Path
import main
from copy import deepcopy


class TestExitCommand(unittest.TestCase):
    def test_exit_command(self):
        self.assertTrue(main.is_exit_command("exit"))
        self.assertTrue(main.is_exit_command("quit"))
        self.assertFalse(main.is_exit_command("hello"))
        self.assertTrue(
            main.is_exit_command(" QUIT ")
        )  # Test with leading/trailing spaces and case insensitivity


class TestResponseGeneration(unittest.TestCase):
    def test_response_generation(self):
        with patch("main.OpenAI") as mock_openai:
            mock_openai.return_value.responses.create.return_value.output_text = (
                "A pretend model reply"
            )

            result = main.get_response([{"role": "user", "content": "hello"}])

            mock_openai.return_value.responses.create.assert_called_once_with(
                model="gpt-4.1-mini",
                input=[{"role": "user", "content": "hello"}],
            )

            self.assertEqual(result, "A pretend model reply")


class TestHistoryPersistence(unittest.TestCase):
    def test_missing_history_returns_empty_list(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            history_path = Path(temp_dir) / "history.json"

            result = main.load_history(history_path)

        self.assertEqual(result, [])

    def test_history_can_be_saved_and_loaded(self):
        history = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there"},
        ]

        with tempfile.TemporaryDirectory() as temp_dir:
            history_path = Path(temp_dir) / "history.json"

            main.save_history(history_path, history)
            loaded_history = main.load_history(history_path)

        self.assertEqual(loaded_history, history)

    def test_empty_history_file_returns_empty_list(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            history_path = Path(temp_dir) / "history.json"
            history_path.write_text("", encoding="utf-8")

            result = main.load_history(history_path)

        self.assertEqual(result, [])

    def test_invalid_json_raises_error(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            history_path = Path(temp_dir) / "history.json"
            history_path.write_text("{not valid json", encoding="utf-8")

            with self.assertRaises(json.JSONDecodeError):
                main.load_history(history_path)

    def test_invalid_chat_history_json_raises_error(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            history_path = Path(temp_dir) / "history.json"
            history_path.write_text("{}", encoding="utf-8")

            with self.assertRaises(ValueError):
                main.load_history(history_path)

    def test_invalid_chat_history_missing_fields_raises_error(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            history_path = Path(temp_dir) / "history.json"
            history_path.write_text("[{}]", encoding="utf-8")

            with self.assertRaises(ValueError):
                main.load_history(history_path)

    def test_invalid_chat_history_non_dictionary_item_raises_error(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            history_path = Path(temp_dir) / "history.json"
            data = """[
                        {"role": "user", "content": "Hi"},
                        "not a message"
                    ]"""
            history_path.write_text(data, encoding="utf-8")

            with self.assertRaises(ValueError):
                main.load_history(history_path)

    def test_non_string_role_raises_error(self):
        self.assert_invalid_history('[{"role": 123, "content": "Hi"}]')

    def test_non_string_content_raises_error(self):
        self.assert_invalid_history('[{"role": "user", "content": 123}]')

    def assert_invalid_history(self, data):
        with tempfile.TemporaryDirectory() as temp_dir:
            history_path = Path(temp_dir) / "history.json"
            history_path.write_text(data, encoding="utf-8")

            with self.assertRaises(ValueError):
                main.load_history(history_path)


class TestRecentMessages(unittest.TestCase):
    def setUp(self):
        self.history = [
            {"role": "user", "content": "Old question"},
            {"role": "assistant", "content": "Old answer"},
            {"role": "user", "content": "Recent question"},
            {"role": "assistant", "content": "Recent answer"},
            {"role": "user", "content": "Current question"},
        ]
        self.original_history = deepcopy(self.history)

    def test_keeps_current_question_when_budget_fits_no_exchange(self):
        current_question = [self.history[-1]]
        budget = main.estimate_content_tokens(current_question)

        selected = main.select_recent_messages(self.history, budget)

        self.assertEqual(selected, current_question)
        self.assertEqual(self.history, self.original_history)

    def test_keeps_latest_exchange_and_current_question_when_they_fit(self):
        expected = self.history[-3:]
        budget = main.estimate_content_tokens(expected)

        selected = main.select_recent_messages(self.history, budget)

        self.assertEqual(selected, expected)
        self.assertEqual(self.history, self.original_history)

    def test_raises_when_current_question_exceeds_budget(self):
        current_question = [self.history[-1]]
        budget = main.estimate_content_tokens(current_question) - 1

        with self.assertRaises(ValueError):
            main.select_recent_messages(self.history, budget)

        self.assertEqual(self.history, self.original_history)


class TestHistoryCompaction(unittest.TestCase):
    def test_does_not_compact_below_threshold(self):
        with patch(
            "main.estimate_content_tokens",
            return_value=main.CONTEXT_TOKENS_THRESHOLD - 1,
        ):
            self.assertFalse(main.should_compact_history([]))

    def test_compacts_at_threshold(self):
        with patch(
            "main.estimate_content_tokens",
            return_value=main.CONTEXT_TOKENS_THRESHOLD,
        ):
            self.assertTrue(main.should_compact_history([]))


class TestChatLoop(unittest.TestCase):
    def test_chat_replies_and_exits(self):
        initial_history = [
            {"role": "user", "content": "Old question"},
            {"role": "assistant", "content": "Old answer"},
            {"role": "user", "content": "Second question"},
            {"role": "assistant", "content": "Second answer"},
            {"role": "user", "content": "Third question"},
            {"role": "assistant", "content": "Third answer"},
        ]

        expected_recent_request = [
            {"role": "user", "content": "Second question"},
            {"role": "assistant", "content": "Second answer"},
            {"role": "user", "content": "Third question"},
            {"role": "assistant", "content": "Third answer"},
            {"role": "user", "content": "How are you?"},
        ]

        expected_saved_history = initial_history + [
            {"role": "user", "content": "How are you?"},
            {"role": "assistant", "content": "Pretend reply"},
        ]
        output = StringIO()

        with patch("builtins.input", side_effect=["How are you?", "exit"]):
            with patch("main.OpenAI") as mock_openai:
                with patch(
                    "main.load_history", return_value=initial_history
                ) as mock_load:
                    with patch("main.save_history") as mock_save:
                        mock_create = mock_openai.return_value.responses.create
                        captured_requests = []

                        def fake_create(*, model, input):
                            captured_requests.append(
                                [message.copy() for message in input]
                            )
                            return SimpleNamespace(output_text="Pretend reply")

                        mock_create.side_effect = fake_create
                        with patch(
                            "main.MAX_CONTEXT_CONTENT_TOKENS",
                            main.estimate_content_tokens(expected_recent_request),
                        ):
                            with redirect_stdout(output):
                                main.run_chat()

        mock_load.assert_called_once_with(main.HISTORY_PATH)
        mock_create.assert_called_once()
        mock_save.assert_called_once_with(
            main.HISTORY_PATH,
            expected_saved_history,
        )
        self.assertEqual(captured_requests[0], expected_recent_request)
        self.assertEqual(
            output.getvalue().strip(),
            "Bot: Pretend reply\nBot: Goodbye!",
        )

    def test_oversized_message_is_rejected_without_saving(self):
        output = StringIO()
        initial_history = []

        with patch("builtins.input", side_effect=["too long", "exit"]):
            with patch("main.load_history", return_value=initial_history):
                with patch(
                    "main.select_recent_messages",
                    side_effect=ValueError("Message exceeds token budget"),
                ):
                    with patch("main.OpenAI") as mock_openai:
                        with patch("main.save_history") as mock_save:
                            with redirect_stdout(output):
                                main.run_chat()

        self.assertIn(
            "Your message exceeds the context limit. Please shorten it and try again.",
            output.getvalue(),
        )
        self.assertIn("Bot: Goodbye!", output.getvalue())
        self.assertEqual(initial_history, [])
        mock_openai.assert_not_called()
        mock_save.assert_not_called()


class TestSplitHistoryForCompaction(unittest.TestCase):
    def test_six_messages_split_into_two_old_and_four_recent(self):
        history = [
            {"role": "user", "content": "Message 0"},
            {"role": "assistant", "content": "Message 1"},
            {"role": "user", "content": "Message 2"},
            {"role": "assistant", "content": "Message 3"},
            {"role": "user", "content": "Message 4"},
            {"role": "assistant", "content": "Message 5"},
        ]

        older_messages, recent_messages = main.split_history_for_compaction(history)

        self.assertEqual(
            older_messages,
            [
                {"role": "user", "content": "Message 0"},
                {"role": "assistant", "content": "Message 1"},
            ],
        )
        self.assertEqual(
            recent_messages,
            [
                {"role": "user", "content": "Message 2"},
                {"role": "assistant", "content": "Message 3"},
                {"role": "user", "content": "Message 4"},
                {"role": "assistant", "content": "Message 5"},
            ],
        )

    def test_four_messages_are_all_recent(self):
        history = [
            {"role": "user", "content": "Message 0"},
            {"role": "assistant", "content": "Message 1"},
            {"role": "user", "content": "Message 2"},
            {"role": "assistant", "content": "Message 3"},
        ]

        older_messages, recent_messages = main.split_history_for_compaction(history)

        self.assertEqual(older_messages, [])
        self.assertEqual(recent_messages, history)

    def test_three_messages_are_all_recent(self):
        history = [
            {"role": "user", "content": "Message 0"},
            {"role": "assistant", "content": "Message 1"},
            {"role": "user", "content": "Message 2"},
        ]

        older_messages, recent_messages = main.split_history_for_compaction(history)

        self.assertEqual(older_messages, [])
        self.assertEqual(recent_messages, history)


class TestSummarizeMessages(unittest.TestCase):
    def test_summarize_messages_builds_prompt_and_returns_summary(self):
        older_messages = [
            {"role": "user", "content": "I am learning Python."},
            {"role": "assistant", "content": "We are building a chatbot."},
        ]
        expected_summary = "The user is learning Python and building a chatbot."
        expected_prompt = [
            {
                "role": "system",
                "content": (
                    "Create a compact summary of the conversation below. "
                    "Preserve useful facts, preferences, decisions, and unresolved tasks. "
                    "Omit greetings and repetition. Do not invent details."
                ),
            },
            *older_messages,
        ]

        with patch(
            "main.get_response", return_value=expected_summary
        ) as mock_get_response:
            result = main.summarize_messages(older_messages)

        mock_get_response.assert_called_once_with(expected_prompt)
        self.assertEqual(result, expected_summary)


if __name__ == "__main__":
    unittest.main()
