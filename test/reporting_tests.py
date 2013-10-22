import datetime
import sys
from io import StringIO
from unittest import mock
import sure
import contexts
from contexts import reporting


class WhenWatchingForDots(object):
    def context(self):
        self.stringio = StringIO()
        self.result = reporting.TextResult(self.stringio)

    def because_we_run_some_assertions(self):
        with self.result.run_context(None):
            with self.result.run_assertion(None):
                pass
            self.first = self.stringio.getvalue()
            with self.result.run_assertion(None):
                pass
            self.second = self.stringio.getvalue()
            with self.result.run_assertion(None):
                raise AssertionError()
            self.third = self.stringio.getvalue()
            with self.result.run_assertion(None):
                raise TypeError()
            self.fourth = self.stringio.getvalue()
            raise ValueError()
        self.fifth = self.stringio.getvalue()

    def it_should_print_a_dot_for_the_first_pass(self):
        self.first.should.equal('.')

    def it_should_print_a_dot_for_the_second_pass(self):
        self.second.should.equal('..')

    def it_should_print_an_F_for_the_failure(self):
        self.third.should.equal('..F')

    def it_should_print_an_E_for_the_assertion_error(self):
        self.fourth.should.equal('..FE')

    def it_should_print_an_E_for_the_ctx_error(self):
        self.fifth.should.equal('..FEE')

class WhenPrintingASuccessfulResult(object):
    def in_the_context_of_a_successful_run(self):
        # We don't want it to try and print anything while we set it up
        self.stringio = StringIO()
        self.result = reporting.TextResult(StringIO())

    def because_we_run_some_tests(self):
        with self.result.run_suite(None):
            with self.result.run_context(None):
                with self.result.run_assertion(None):
                    pass
                with self.result.run_assertion(None):
                    pass
            with self.result.run_context(None):
                with self.result.run_assertion(None):
                    pass
            self.result.stream = self.stringio

    def it_should_print_the_summary_to_the_stream(self):
        self.stringio.getvalue().should.equal(
"""
----------------------------------------------------------------------
PASSED!
2 contexts, 3 assertions
""")

class WhenPrintingAFailureResult(object):
    def in_the_context_of_a_failed_run(self):
        self.result = reporting.TextResult(StringIO())
        self.stringio = StringIO()

        self.exception1 = TypeError("Gotcha")
        self.tb1 = [('made_up_file.py', 3, 'made_up_function', 'frame1'),
               ('another_made_up_file.py', 2, 'another_made_up_function', 'frame2')]
        self.assertion1 = contexts.core.Assertion(None, "made.up.assertion_1")

        self.exception2 = AssertionError("you fail")
        self.tb2 = [('made_up_file_3.py', 1, 'made_up_function_3', 'frame3'),
               ('made_up_file_4.py', 2, 'made_up_function_4', 'frame4')]
        self.assertion2 = contexts.core.Assertion(None, "made.up.assertion_2")

        self.exception3 = ZeroDivisionError("oh dear")
        self.tb3 = [('made_up_file_4.py', 1, 'made_up_function_4', 'frame4'),
               ('made_up_file_5.py', 2, 'made_up_function_5', 'frame5')]
        self.context3 = contexts.core.Context([],[],[],[],"made.up_context")

    def because_we_run_some_tests(self):
        with self.result.run_suite(None):
            with self.result.run_context(None):
                # Figure out a way to do this using the context manager?
                self.result.assertion_errored(self.assertion1, self.exception1, self.tb1)
                self.result.assertion_failed(self.assertion2, self.exception2, self.tb2)
            self.result.context_errored(self.context3, self.exception3, self.tb3)
            self.result.stream = self.stringio

    def it_should_print_a_traceback_for_each_failure(self):
        self.stringio.getvalue().should.equal(
"""
======================================================================
ERROR: made.up_context
----------------------------------------------------------------------
Traceback (most recent call last):
  File "made_up_file_4.py", line 1, in made_up_function_4
    frame4
  File "made_up_file_5.py", line 2, in made_up_function_5
    frame5
ZeroDivisionError: oh dear
======================================================================
ERROR: made.up.assertion_1
----------------------------------------------------------------------
Traceback (most recent call last):
  File "made_up_file.py", line 3, in made_up_function
    frame1
  File "another_made_up_file.py", line 2, in another_made_up_function
    frame2
TypeError: Gotcha
======================================================================
FAIL: made.up.assertion_2
----------------------------------------------------------------------
Traceback (most recent call last):
  File "made_up_file_3.py", line 1, in made_up_function_3
    frame3
  File "made_up_file_4.py", line 2, in made_up_function_4
    frame4
AssertionError: you fail
----------------------------------------------------------------------
FAILED!
2 contexts, 2 assertions: 1 failed, 2 errors
""")


class WhenTimingATestRun(object):
    def context(self):
        self.fake_now = datetime.datetime(2013, 10, 22, 13, 41, 0)
        self.fake_soon = datetime.timedelta(seconds=10, milliseconds=530)

        class FakeDateTime(datetime.datetime):
            now = mock.Mock(return_value=self.fake_now)
        self.FakeDateTime = FakeDateTime

        self.stringio = StringIO()
        self.result = reporting.TimedTextResult(self.stringio)

    def because_we_run_a_suite(self):
        with mock.patch('datetime.datetime', self.FakeDateTime):
            with self.result.run_suite(None):
                datetime.datetime.now.return_value += self.fake_soon

    def it_should_report_the_total_time_for_the_test_run(self):
        self.stringio.getvalue().should.equal("""
----------------------------------------------------------------------
PASSED!
0 contexts, 0 assertions
(10.5 seconds)
""")

class WhenCapturingStdOut(object):
    def context(self):
        self.real_stdout = sys.stdout
        self.real_stderr = sys.stderr
        sys.stdout = self.fake_stdout = StringIO()
        sys.stderr = self.fake_stderr = StringIO()

        self.stringio = StringIO()
        # we don't want the output to be cluttered up with dots
        self.result = reporting.CapturingTextResult(StringIO())

    def because_we_print_some_stuff(self):
        with self.result.run_suite(None):
            with self.result.run_assertion(None):
                print("passing assertion")
            with self.result.run_assertion(None):
                print("failing assertion")
                assert False
            with self.result.run_assertion(None):
                print("erroring assertion")
                raise ValueError()

            with self.result.run_context(None):
                print("passing context")
            with self.result.run_context(None):
                print("erroring context")
                raise ValueError()
            with self.result.run_context(None):
                print("failing context")
                with self.result.run_assertion(None):
                    assert False

            self.result.stream = self.stringio

    def it_should_not_print_anything_to_stdout(self):
        self.fake_stdout.getvalue().should.be.empty

    def cleanup_stdout_and_stderr(self):
        sys.stdout = self.real_stdout
        sys.stderr = self.real_stderr

if __name__ == "__main__":
    contexts.main()
