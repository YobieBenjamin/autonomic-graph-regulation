Can an AI Have a Nervous System?

*Garbage In, Gospel Out, Part II, the plain-English version: why I am
building an early-warning system for AI, how the experiments work, what
they found, and where it goes next.*

*This project is by me and AI. I conceived and directed it; the code,
experiments, analyses and drafts were produced by me together with AI
systems (Anthropic's Claude as research assistant, and a locally run
open model). The full record, including every mistake and correction, is
public at github.com/YobieBenjamin/autonomic-graph-regulation.*

Why I am doing this

In my book, Garbage In, Gospel Out, I argued that AI language models are
extremely fancy autocomplete with a PhD vocabulary. They sound just as
sure of themselves when they are wrong as when they are right. The
output always reads like gospel.

I wanted to know whether that was a metaphor or a measurable fact, at
least for one AI model. In an early experiment, three out of four of its
wrong answers carried at least 90% of the model's own probability on
every piece of the answer. On a fresh set of questions, that probability
was not just unhelpful but inverted: wrong answers tended to carry more
of it than right ones.

Most AI safety today works by watching what the AI says. To be fair,
that works well once an answer is finished: simply asking the AI the
same question again turns out to be very accurate. But checking takes
time, and a safety system that is supposed to act in the moment needs to
raise its hand before the answer goes out, not after.

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
warning while the AI is still thinking. Others have shown that an AI's
internals carry warning signs too; what is different here is the
hospital-style framing, the external design, and a fair race against the
clock. The long-term goal is a small brain-inspired chip that sits next
to every AI chip. Today it is a software simulation on one MacBook.

How the experiment works

The ingredients

-   **The monitored model.** An open AI model (gpt-oss-20b) whose
    insides I can read. It has 24 layers, like 24 stages of processing.

-   **The questions.** Six kinds of questions a computer can grade
    exactly: small and large multiplications, counting letters, working
    out the day of the week, modular arithmetic, and long additions. No
    AI ever decides what counts as right. In the final test, all the
    wrong answers came from four of the six kinds.

-   **The vital signs (the variables).** For every piece of text the AI
    produces, I record five readings from each of its 24 layers, 120
    numbers in all: how hard its attention is working, how hard its
    specialist sub-networks (\"experts\") are working, its overall
    activation level, how much each layer changes direction, and how
    undecided it is about which experts to use.

-   **The regulator.** A small, deterministic program that never reads
    the AI's words. Besides the vital signs, it is told only which kind
    of question is being answered and how long the AI has been thinking.
    It learned what healthy and failing \"physiology\" look like from
    5,367 practice answers, 402 of them wrong. It is a statistical model
    with an alarm threshold; a more transparent, hospital-style points
    score I also built did not work as well.

The race

The key test is a race against the clock, run as a replay of recorded
thinking that charges each monitor its own measured computing time.
While the AI is still thinking, each monitor gets to look at four
moments: after 48, 96, 192 and 384 pieces of text. A warning only counts
if it would arrive before the AI states its answer. The regulator's
competitors:

-   **An AI judge** about five and a half times larger than the
    monitored model in total size (though per piece of text it does only
    about 1.4 times the computation), reading the reasoning so far and
    estimating the chance it will end up wrong.

-   **Asking again:** letting the AI continue twice from the same point
    and checking whether it agrees with itself. This takes several
    seconds per look, so it almost never finishes in time; the race is
    lopsided against it by design.

-   **A deliberately dumb monitor** that only knows how long the AI has
    been thinking. If the regulator cannot beat this, it is not reading
    anything deeper.

The fairness rules

-   Every monitor may raise a false alarm on at most 10% of the correct
    answers in the test. Catching errors by crying wolf does not count.

-   Before the test began, the rules and the complete analysis code were
    sent to GitHub, whose own servers logged their arrival about ten
    seconds before the first test question was recorded.

-   The decisive test used 600 newly recorded questions, recorded once
    after the rules were fixed.

What we found

Two things that support the premise

-   **The model's own confidence is a poor guide.** On fresh data, the
    probability it gave its answer pointed the wrong way, toward right
    answers rather than wrong ones.

-   **The power cord says nothing.** In a small experiment I found no
    detectable difference in the chip's power draw between right and
    wrong answers, which points toward reading the AI's internal signals
    directly.

The part where I was wrong

I promised honesty, so here it is. Several of my early results did not
survive scrutiny. An early \"warning 4.5 seconds before the answer\"
turned out to be an alarm that fired on almost every answer, right or
wrong. Early versions of the regulator did not beat simple baselines
like \"how long did it think?\". And in a fair, pre-announced race, the
regulator lost to the AI judge: it caught 4 wrong answers in time to the
judge's 12, out of 47. I redesigned it, training it on unfinished
thinking, the way hospitals take vital signs again and again, and only
then did it win on new data.

To catch mistakes like these, the project was audited three times. Each
audit was a separate session of an AI model, told nothing about earlier
findings: independent of the session that did the work, but not of the
AI system, and no human expert has reviewed the work yet. The first
audit found 38 problems, three of them critical; among the more serious
others was a subtle bug that delivered the vital signs one step late. My
AI research assistant verified each critical finding under my direction;
we fixed the instruments and the statistics, logged every error in a
public corrections record, and re-ran the key test on 600 newly recorded
questions. Two further audits reviewed that test and earlier drafts of
this post, and this version corrects what they found.

The main result

Of the 600 new questions, 535 were answered and 40 of those answers were
wrong. Warnings that arrived before the AI's answer:

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

  Asking the AI again             0                   median about 6
                                                      seconds
  ------------------------------- ------------------- -------------------

Checks I added afterwards, after an audit asked for them (they were not
in the rules fixed in advance):

-   A monitor that knows only the kind of question caught 6. One that
    knows the kind of question and how long the AI has been thinking
    caught 9.

-   Setting the regulator's alarm using only the practice answers, never
    the test answers, it still caught 22 of 40, though with somewhat
    more false alarms on the answers it could see.

-   The judge raised fewer false alarms than the regulator on the
    answers either could see. Holding both to about the same rate there,
    the regulator still caught more, 19 to 11, but the margin is smaller
    and its uncertainty range comes close to zero.

Two earlier test sets, re-analysed with the corrected instruments,
showed the same pattern.

Where it does not help

-   **After the answer is finished,** asking the AI again is more
    accurate than the regulator, and a larger AI judge did about as well
    as an earlier version of it. The regulator's advantage is speed and
    cost while the answer is still forming.

-   **When the AI never finishes** and keeps thinking until it runs out
    of room, noticing that it has been thinking for a long time works at
    least as well as the regulator.

What this does and does not mean

-   Before an answer exists, reading an AI's internal physiology caught
    more of its wrong answers in time than a much larger AI judge
    reading its reasoning, under rules fixed in advance and on newly
    recorded data.

-   It is one AI model and one kind of task: questions with a single
    checkable answer. It is not yet detection of \"hallucinations\" in
    ordinary prose, and I did not measure how confident the caught wrong
    answers sounded.

-   The regulator never reads the AI's words, so it cannot be argued
    with directly. Whether crafted inputs could fool it, by steering the
    AI's internal activity, has not been tested.

Conclusion

For the model I studied, its own confidence tells you little about
whether it is right. Watching the AI's words works well, but only after
the answer exists. Reading its internal vital signs, the way a hospital
reads a patient's, caught more of its mistakes before they reached the
output than a much larger AI judge could, in milliseconds instead of
seconds. It is a narrow result, earned through a lost race, a redesign,
many failed experiments and three unforgiving audits. The biological
template, a separate nervous system instead of a self-grading machine,
looks worth pursuing, and I would welcome an expert to try to break it.

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

6.  **Toward the chip.** Prove the signalling is free of timing errors,
    that readings split across several processors add up exactly, and
    that warnings can always act before output leaves the chip.

7.  **Outside eyes.** Invite independent researchers to replicate the
    results from the public code and data.
