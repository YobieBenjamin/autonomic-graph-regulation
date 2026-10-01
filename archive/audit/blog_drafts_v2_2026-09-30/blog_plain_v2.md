Can an AI Have a Nervous System?

*Garbage In, Gospel Out, Part II, the plain-English version: why I am
building an early-warning system for AI, how the experiments work, what
they found, and where it goes next.*

Why I am doing this

In my book, Garbage In, Gospel Out, I argued that AI language models are
extremely fancy autocomplete with a PhD vocabulary. They sound just as
sure of themselves when they are wrong as when they are right. The
output always reads like gospel.

I wanted to know whether that was a metaphor or a measurable fact. In an
early experiment, three out of four of the AI's wrong answers were
delivered with at least 90% confidence on every piece of the answer. On
a fresh set of questions, \"how confident did the answer sound?\"
predicted mistakes worse than a coin flip: wrong answers tended to sound
more sure than right ones.

Most AI safety today works by watching what the AI says. To be fair,
that works well once an answer is finished: a larger AI checking the
answer, or simply asking the AI the same question again, turns out to be
quite accurate. But checking takes time, and a safety system that is
supposed to act in the moment needs to raise its hand before the answer
goes out, not after.

The idea: vital signs, not conversation

Hospitals solved a version of this problem decades ago. Nurses do not
ask a patient \"how are you feeling?\" and trust the answer. They
measure heart rate, breathing, blood pressure and oxygen, and a scoring
system called NEWS2 turns those readings into a warning level so staff
can act before a crisis.

My conviction is that there is no working model of judgment other than
the human brain and body. So instead of asking the AI to judge itself, I
am building it an external nervous system: a separate, simple regulator
that reads the AI's internal vital signs, never its words, and raises a
warning while the AI is still thinking. The long-term goal is a small
brain-inspired chip that sits next to every AI chip. Today it is a
software simulation on one MacBook.

How the experiment works

The ingredients

-   **The monitored model.** An open AI model (gpt-oss-20b) whose
    insides I can read. It has 24 layers, like 24 stages of processing.

-   **The questions.** Six kinds of questions a computer can grade
    exactly: small and large multiplications, counting letters, working
    out the day of the week, modular arithmetic, and long additions. No
    AI ever decides what counts as right.

-   **The vital signs (the variables).** For every piece of text the AI
    produces, I record five readings from each of its 24 layers, 120
    numbers in all: how hard its attention is working, how hard its
    specialist sub-networks (\"experts\") are working, its overall
    activation level, how much each layer changes direction, and how
    undecided it is about which experts to use.

-   **The regulator.** A small, deterministic program that never sees a
    single word. It learned what healthy and failing \"physiology\" look
    like from 5,367 practice answers, 402 of them wrong. It is a
    statistical model with an alarm threshold; a more transparent,
    hospital-style points score I also built did not work as well.

The race

The key test is a race against the clock. While the AI is still
thinking, each monitor gets to look at four moments: after 48, 96, 192
and 384 pieces of text. A warning only counts if it arrives before the
AI states its answer, including the time the monitor itself needs to
compute. The regulator's competitors:

-   **An AI judge** about five and a half times larger than the
    monitored model, reading the reasoning so far and estimating the
    chance it will end up wrong.

-   **Asking again:** letting the AI continue twice from the same point
    and checking whether it agrees with itself.

-   **Two deliberately dumb monitors:** one that only knows how long the
    AI has been thinking, and one that only knows which kind of question
    it is. If the regulator cannot beat these, it is not reading
    anything deeper.

The fairness rules

-   Every monitor may raise a false alarm on at most 10% of the correct
    answers in the test. Catching errors by crying wolf does not count.

-   The rules and the complete analysis code were committed to GitHub,
    with a timestamp, before the test recordings existed.

-   The decisive test used 600 new questions recorded once, after the
    rules were fixed.

What we found

Two things that confirmed the premise

-   **Confidence is a poor guide.** Measured on fresh data, how sure the
    answer sounded predicted mistakes worse than chance.

-   **The power cord says nothing.** I measured the chip's power draw
    while the AI thought and found no detectable difference between
    right and wrong answers, so a safety system has to read the AI's
    internal signals directly.

The part where I was wrong

I promised honesty, so here it is. Several of my early results did not
survive scrutiny. An early \"warning 4.5 seconds before the answer\"
turned out to be an alarm that fired on almost every answer, right or
wrong. Early versions of the regulator did not beat simple baselines
like \"how long did it think?\".

To catch mistakes like these, I had an independent AI auditor review the
whole project, reading everything without being told what we already
suspected. It found 38 problems, three of them critical, including a
subtle bug that delivered the vital signs one step late. My AI research
assistant verified each critical finding under my direction; we fixed
the instruments and the statistics, logged every error in a corrections
record, and re-ran the key experiment from scratch. A second independent
audit then reviewed that experiment and an earlier draft of this post,
and found more overstatements, which this version corrects.

The main result

On the 600 new questions, warnings that arrived before the AI's answer:

  ------------------------------- ------------------- -------------------
  **Monitor**                     **Wrong answers     **Time per check**
                                  caught in time (of  
                                  40)**               

  The regulator (vital signs      23                  about 5
  only)                                               milliseconds

  The AI judge (5.6x larger)      11                  median 1.5 seconds;
                                                      1 in 10 checks over
                                                      7 seconds

  The length-only monitor         9                   instant

  The question-type monitor       6                   instant

  Asking the AI again             0                   several seconds
  ------------------------------- ------------------- -------------------

Two checks make this harder to dismiss. First, the regulator's alarm
threshold could be set using only the practice answers, never the test
answers, and it still caught 22 of 40. Second, the judge raised fewer
false alarms than the regulator on the answers either could see. When I
held both to exactly the same false-alarm rate there, the regulator
still caught more, 19 to 11, though the margin is smaller and its
uncertainty range comes close to zero. Two earlier test sets,
re-analysed with the corrected instruments, showed the same pattern.

Where it does not help

-   **After the answer is finished,** the AI judge and simply asking
    again are more accurate than the regulator. Its advantage is speed
    and cost while the answer is still forming.

-   **When the AI never finishes** and keeps thinking until it runs out
    of room, noticing that it has been thinking for a long time works
    just as well.

What this does and does not mean

-   Before an answer exists, reading an AI's internal physiology caught
    more of its wrong answers in time than a much larger AI judge
    reading its reasoning, under rules fixed in advance and on data
    nobody had seen.

-   It is one AI model and one kind of task: questions with a single
    checkable answer. It is not yet detection of \"hallucinations\" in
    ordinary prose, and I did not measure how confident the caught wrong
    answers sounded.

-   The regulator cannot be sweet-talked because it never reads words.
    Whether it can be fooled in other ways has not been tested.

Conclusion

The gospel problem is real: an AI's confidence tells you little about
whether it is right. Watching the AI's words works well, but only after
the answer exists. Reading its internal vital signs, the way a hospital
reads a patient's, caught more of its mistakes before they reached the
output than a much larger AI judge could, in milliseconds instead of
seconds. It is a narrow result, earned through a lot of failed
experiments and two unforgiving audits, and it is the first one in this
project I would stake my name on. The biological template, a separate
nervous system instead of a self-grading machine, looks worth pursuing.

Next steps

1.  **A second AI model.** Repeat the test on a different company's
    model with a different internal design, the equivalent of validating
    a hospital score at a second hospital.

2.  **Flagging believable prose that is false.** The real product goal:
    highlight the specific sentences in a fluent paragraph that are
    likely untrue.

3.  **Models without \"experts\".** Test whether the approach still
    works when one of its most useful signals does not exist.

4.  **A transparent score.** Make the hospital-style points score as
    good as the statistical regulator, so every warning can be
    explained.

5.  **Situations, not just answers.** Test warnings on an AI agent doing
    multi-step tasks, where problems build up gradually.

6.  **Toward the chip.** Write the hardware interface: what the AI chip
    exposes, what the regulator computes, and what it signals.

7.  **Outside eyes.** Invite independent researchers to replicate the
    results.
