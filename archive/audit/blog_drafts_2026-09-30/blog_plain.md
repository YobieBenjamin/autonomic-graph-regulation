Can an AI Have a Nervous System?

*Garbage In, Gospel Out, Part II, the plain-English version: why I am
building an early-warning system for AI, how the experiments work, what
they found, and where it goes next.*

Why I am doing this

In my book, Garbage In, Gospel Out, I argued that AI language models are
extremely fancy autocomplete with a PhD vocabulary. They sound exactly
as confident when they are wrong as when they are right. The output
always reads like gospel.

I wanted to know whether that was a metaphor or a measurable fact. So I
measured it. When the AI got an answer wrong, three out of four of those
wrong answers were delivered with more than 90% confidence. Worse, when
I used \"how confident did the answer sound?\" to predict mistakes, it
did worse than a coin flip. Wrong answers sounded more sure than right
ones.

That matters because most AI safety today works by watching what the AI
says: reading its answers, grading its outputs, filtering its words. If
the words look equally confident whether the AI is right or wrong,
watching the words cannot reliably tell you when to worry.

The idea: vital signs, not conversation

Hospitals solved a version of this problem decades ago. Nurses do not
ask a patient \"how are you feeling?\" and trust the answer. They
measure: heart rate, breathing, blood pressure, oxygen. A system called
NEWS2 turns those readings into points and a warning level, stable,
watch, concern or urgent, so staff act hours before a crisis instead of
after it.

My conviction is that there is no working model of judgment other than
the human brain and body. So instead of asking the AI to judge itself, I
am building it an external nervous system: a separate, simple regulator
that reads the AI's internal vital signs, never its words, and raises
graded warnings before a mistake reaches the output. The long-term goal
is a small brain-inspired chip that sits next to every AI chip. Today it
is a software simulation on one MacBook.

How the experiment works

The ingredients

-   **The monitored model.** An open AI model (gpt-oss-20b) whose
    insides I can read. It has 24 layers, like 24 stages of processing.

-   **The questions.** Thousands of questions a computer can grade
    exactly: big multiplications, counting letters, working out the day
    of the week, and similar. No AI ever decides what counts as right.

-   **The vital signs (the variables).** For every piece of text the AI
    produces, I record five readings from each of its 24 layers, 120
    numbers in all: how hard its attention is working, how hard its
    specialist sub-networks (\"experts\") are working, its overall
    activation level, how much each layer changes direction, and how
    undecided it is about which experts to use. I also record how
    undecided it is about its next word.

-   **The regulator.** A small, deterministic program that never sees a
    single word. It learned what healthy and failing \"physiology\" look
    like from 5,367 practice answers, 402 of them wrong.

The race

The key test is a race against the clock. While the AI is still
thinking, the regulator gets to look at four moments: after 48, 96, 192
and 384 pieces of text. Its warning only counts if it arrives before the
AI states its answer, including the time the regulator itself needs to
compute.

It races three competitors:

-   **An AI judge** about five and a half times larger than the
    monitored model, reading the reasoning so far and estimating the
    chance it will end up wrong.

-   **Asking again:** letting the AI continue twice from the same point
    and checking whether it agrees with itself.

-   **A deliberately dumb monitor** that only knows how long the AI has
    been thinking. If the regulator cannot beat this, it is not reading
    anything deeper than length.

The fairness rules

-   Every monitor may raise a false alarm on at most 10% of correct
    answers. Catching errors by crying wolf does not count.

-   The rules and the complete analysis code are committed to GitHub,
    with a timestamp, before the test questions even exist.

-   Each test set is brand new and used once.

What we found

Two things that confirmed the premise

-   **The AI sounds most sure when it is wrong.** Confirmed on fresh
    data: answer confidence predicts mistakes worse than chance.

-   **AI does not sweat.** I measured the chip's power draw while it
    thought. No difference between right and wrong answers. Unlike a
    body, a transformer does the same amount of work for every word, so
    a safety system has to read the brain, not the power cord.

The part where I was wrong

I promised honesty, so here it is. My early results looked exciting and
several did not survive scrutiny. An early \"warning 4.5 seconds before
the answer\" turned out to be an alarm that fired on almost every
answer, right or wrong. Early versions of the regulator did not beat
simple baselines like \"how long did it think?\".

To catch mistakes like these, I had a separate AI act as an independent,
adversarial auditor of the whole project, reading everything without
being told what I already suspected. It found 38 problems, three of them
critical, including a subtle bug that delivered the vital signs one step
late. I verified every critical finding myself, fixed the instruments
and the statistics, logged every error in a corrections record, and
re-ran the key experiment from scratch.

The main result, after all the fixes

On 600 brand-new questions, with every correction in place:

  ------------------------------- ------------------- -------------------
  **Monitor**                     **Wrong answers     **Time per check**
                                  caught before the   
                                  answer**            

  The regulator (vital signs      23 of 40            about 5
  only)                                               milliseconds

  The AI judge (5.6x larger)      11 of 40            about 1.5 to 2
                                                      seconds

  The length-only monitor         9 of 40             instant

  Asking the AI again             0 of 40             several seconds
  ------------------------------- ------------------- -------------------

The same pattern held on two earlier test sets re-analysed with the
corrected instruments. Pooled over 1,610 questions, the regulator caught
about 32 percentage points more of the wrong answers in time than either
the judge or the length monitor, and the uncertainty range stays well
above zero.

Where it does not help

Some answers never finish: the AI keeps thinking until it runs out of
room. If those count as failures too, the regulator is no better than
simply noticing that the AI has been thinking for a long time. Its real
advantage is on the dangerous case: the confident wrong answer.

What this does and does not mean

-   It is the first result in this project where reading an AI's
    internal physiology beats watching its behavior, under fair,
    pre-announced rules and on data nobody had seen.

-   It is one AI model and one kind of task: questions with a single
    checkable answer. It is not yet detection of \"hallucinations\" in
    ordinary prose.

-   The regulator cannot be sweet-talked because it never reads words.
    Whether it can be fooled in other ways has not been tested, so I do
    not claim it is unbreakable.

Conclusion

The gospel problem is real and measurable: an AI's confidence tells you
little about whether it is right. Reading the AI's internal vital signs,
the way a hospital reads a patient's, gave earlier and more reliable
warnings of confident mistakes than a much larger AI judge, at a tiny
fraction of the cost. It took a lot of failed experiments and an
unforgiving audit to get a result I trust. I think the biological
template, a separate nervous system instead of a self-grading machine,
is standing on firmer ground than when I started.

Next steps

1.  **A second AI model.** Repeat the test on a different company's
    model with a different internal design, the equivalent of validating
    a hospital score at a second hospital.

2.  **Flagging believable prose that is false.** The real product goal:
    highlight the specific sentences in a fluent paragraph that are
    likely untrue.

3.  **Models without \"experts\".** Test whether the approach still
    works when its strongest warning sign does not exist.

4.  **A transparent score.** Make the hospital-style points score as
    good as the black-box regulator, so every warning can be explained.

5.  **Situations, not just answers.** Test graded warnings on an AI
    agent doing multi-step tasks, where problems build up gradually.

6.  **Toward the chip.** Write the hardware interface: what the AI chip
    exposes, what the regulator computes, and what it signals.

7.  **Outside eyes.** Invite independent researchers to replicate the
    results from the published code and data.
