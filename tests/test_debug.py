from synth.debug import DebugLevel, DebugReporter


class TestDebugReporter:
    def test_none_outputs_nothing(self, capsys) -> None:
        reporter = DebugReporter(DebugLevel.NONE)

        reporter.light("light message")
        reporter.verbose("verbose message")

        assert capsys.readouterr().out == ""

    def test_light_outputs_light_messages_only(self, capsys) -> None:
        reporter = DebugReporter(DebugLevel.LIGHT)

        reporter.light("light message")
        reporter.verbose("verbose message")

        assert capsys.readouterr().out == "light message\n"

    def test_verbose_outputs_light_and_verbose_messages(self, capsys) -> None:
        reporter = DebugReporter(DebugLevel.VERBOSE)

        reporter.light("light message")
        reporter.verbose("verbose message")

        assert capsys.readouterr().out == "light message\nverbose message\n"
