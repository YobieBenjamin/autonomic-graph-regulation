Your AI Lies With a Straight Face. So I Built It a Nervous System.

*Part 1 of 2, the plain-English story: what I learned testing whether an
AI's mistakes can be caught before it makes them.*

*Part 1 of 2. This part tells the story in plain English. Part 2 is the
technical version: the math, the methods, the tests and a link to every
result on GitHub.*

The problem

Ask an AI a question and it answers with total confidence. Ask it
something it gets wrong, and it answers with the same confidence,
sometimes more. It doesn't hesitate, it doesn't say "I'm not sure," it
just tells you the wrong thing like it's reading from a textbook.

I wrote a book about this called Garbage In, Gospel Out. Then I decided
to measure it. On one AI model, the wrong answers actually came out more
confident than the right ones. In an early test, three out of four of
its mistakes were delivered with 90% confidence or more on every word of
the answer. (I didn't check how often right answers looked the same in
that test.)

So you can't trust how sure an AI sounds. That's a problem when AI
starts making decisions that matter: moving money, approving claims,
giving medical information.

This post is about what I've found so far. Fair warning: this research
is just beginning. The results are promising, not proven, and there's a
lot more to do. But they already point to one big conclusion: keeping AI
safe takes several layers of protection, not one.

Why the AI can't check its own work

The obvious fix is to ask the AI "are you sure?" That doesn't work as a
safety brake, and here's why.

An AI like the ones behind today's chatbots does one thing: it guesses
the next word, over and over, based on patterns from everything it has
read. There is no little inspector inside checking the work. When you
ask it to double-check, the same guessing machine guesses what a careful
double-check would sound like. Often it confirms its own mistake,
fluently. Asking again can catch some errors once the answer is out, but
that's slow, and it's no help when the AI is consistently wrong.

It's like asking someone who misread a map whether they read the map
right. They'll look at the same map with the same eyes and tell you yes.

So the checking has to come from outside the AI.

Where the idea comes from: your brain has brakes

This whole project started with biology. Your brain takes in a flood of
information every second, sights, sounds, memories, feelings, and still
gets most calls right. One big reason: it has brakes.

Start to say something you shouldn't in a meeting and you can stop
mid-sentence. Scientists study this with a simple game: start pressing a
button, then a signal tells you to stop. Inside your brain, a "go"
process and a "stop" process race each other. If the stop arrives in
time, the action never happens.

Your brain also has an alarm for mistakes. Within about a tenth of a
second of slipping up, well before you could say you'd made a mistake, a
specific brain signal fires that means "that was wrong." And these
brakes and alarms run on what's happening inside you, not on what you
tell yourself.

Today's AI has none of that. No brakes, no internal alarm, no gut
feeling that something is off. It just keeps guessing the next word. My
watchdog is an attempt to bolt the missing piece on from the outside.

My idea: vital signs

Hospitals solved a version of this long ago. A nurse doesn't just ask a
patient "how do you feel?" They check heart rate, blood pressure,
breathing and temperature. A patient can say "I'm fine" while the
numbers say otherwise, and the numbers win.

So I built a watchdog that does the same for AI. It never listens to
what the AI says. Instead it reads 120 numbers from inside the AI while
it's thinking, the AI equivalent of a pulse and blood pressure, and
raises a flag when something looks off. Because it never reads the AI's
words, clever wording can't argue with it. (Whether someone could craft
inputs that fool its readings hasn't been tested yet.)

How I tested it

One MacBook, a free AI model from OpenAI called gpt-oss-20b, and
thousands of questions with answers a computer can check exactly: math
problems, counting letters, calendar dates. No opinions, no judgment
calls. Right is right. I picked that model because it's "open": anyone
can download it and look at what's happening inside it, which is exactly
what my watchdog needs. The big commercial chatbots don't let you do
that.

Then I ran a race. While the AI was still thinking, before it gave its
answer, could my watchdog spot that the answer was going to be wrong? I
raced it against a bigger AI acting as a judge, OpenAI's gpt-oss-120b,
reading the first AI's reasoning as it went. It's about five and a half
times bigger overall, though only about 1.4 times bigger in the part
that does the work for each word.

To keep myself honest, I wrote down the rules and locked them in before
each test, with a public timestamp from the second test on, so I
couldn't move the goalposts after seeing the results. And every monitor
was allowed only a limited number of false alarms. You don't get credit
for catching mistakes by crying wolf all the time.

What I found

In the biggest test, the AI got 138 answers wrong. Here is how many each
monitor caught before the wrong answer came out:

  --------------------------------------- -------------------------------
  **Monitor**                             **Wrong answers caught in time
                                          (of 138)**

  A standard method that reads the AI's   100
  inner state                             

  My watchdog (the 120 "vital signs")     94

  A bigger AI judge reading its reasoning 28
  --------------------------------------- -------------------------------

Reading the inside of the AI caught more than three times as many
mistakes as the bigger AI judge reading its words, and clearly more than
the judge in each of the three separate test sets in that experiment (my
watchdog caught between 2.5 and 2.9 times as many in each; I checked
that breakdown afterwards).

One humbling detail: a standard method researchers already use did about
as well as my version. So the big idea is right, reading the inside
beats listening to the outside, but my particular recipe isn't special.
I'd rather know that than pretend otherwise.

The catch: a warning has to arrive in time

Next I tested the watchdog's warnings against a real safety tool. NVIDIA
recently released one called OpenShell. Think of it as a locked room for
an AI agent, with a list of what it's allowed to do. It's a good idea,
but it has a blind spot: if the AI is allowed to make a payment,
OpenShell lets the payment through even if the AI calculated the amount
wrong. It controls what the AI may do, not whether its thinking is
right.

So I replayed my watchdog's warnings into it to see if they could stop
bad actions. With its alarm level fixed in advance, the watchdog warned
in time about 93 wrong answers. But changing OpenShell's permissions
took about five and a half seconds, and the AI usually acted within a
few seconds of the warning. Result: 74 of those 93 wrong actions went
through anyway. The warning was right. It was just too late.

The fix is simple and a little boring: make important actions wait for
an all clear. When every action had to wait, every warned action was
stopped, because nothing with a warning ever got released. The price was
a wait of about seven seconds per action (the median), and 16 of 138
right answers held up, mostly by false alarms.

Honest note: this was a replay of recorded results through NVIDIA's
free, open-source tool on my Mac, not a live system on their hardware.

Notice that this is the same race your brain runs: the stop signal has
to beat the action. Your brain's brake works in about a fifth of a
second. A permission change that takes five seconds usually isn't.

Why this matters more than a wrong math answer

A wrong math answer is harmless. Now put the same kind of AI in charge
of something that can't be undone. Imagine an AI-guided combat drone
that picks the wrong target with the same calm confidence it used when
it got a big multiplication wrong. There's no "oops" that un-bombs a
school.

With people, we have a backstop: accountability. A soldier, a pilot, a
surgeon or a banker who makes a terrible call can be investigated,
fired, sued or sent to prison. That threat is part of what keeps human
judgment careful.

You can't put an AI on trial. You can't jail an algorithm, and legal
systems around the world were built to judge people, not machines. When
an AI makes the call, responsibility gets smeared across the company
that built it, the company that deployed it and the person who switched
it on, and it can end up landing on nobody. Philosophers have a name for
this: the responsibility gap.

So with AI we can't count on punishment after the fact. The brakes have
to be built in before the action: an outside monitor reading the AI's
vital signs, a hold on anything that can't be undone, and a human who
has to sign off when lives are at stake. When a mistake is permanent and
nobody can be held to account, prevention is the only safety there is.

To be clear, my tests used math questions on a laptop, not weapons. But
the principle only gets stronger as the stakes rise.

The big lesson: you need layers of locks

Banks figured this out a long time ago. A card payment doesn't pass one
check. It gets authorized, scored for fraud, checked against limits and
sometimes held before it settles. No single check is perfect, so you
stack checks that fail in different ways.

AI needs the same thing:

1.  **A permission check:** what is the AI allowed to touch at all?

2.  **A vital-signs check:** is its thinking going wrong right now?

3.  **A hold on anything you can't undo,** until it's cleared.

4.  **A second opinion after the fact** for the answers that slip
    through.

5.  **A human** for the decisions that really matter, because a person
    can be held accountable and a machine can't.

The AI can give a second opinion on its own finished work, but it can't
be the lock on its own actions.

What I'm sure of, and what I'm not

I'm now convinced that reading what's happening inside an AI is a much
better early warning than trusting what it says, at least for this AI
and these kinds of questions. I'm convinced the safety check has to live
outside the AI. And I'm convinced timing matters as much as accuracy.

I'm not yet sure it works the same on other AI models, on everyday
writing instead of math problems, or at the speed and scale of real
products. Those are the next tests, each with a clear pass or fail line
written down in advance. This is the beginning of the research, not the
end.

The tools and models I used

-   **The AI being watched:** gpt-oss-20b, a free, open model from
    OpenAI.

-   **The AI judge it raced against:** gpt-oss-120b, OpenAI's bigger
    open model (about five and a half times larger overall). It also
    helped write some of the code.

-   **The safety tool:** OpenShell from NVIDIA, free and open source.

-   **My research assistant:** Claude, from Anthropic. It helped write
    the code, run the experiments, draft the text and review the work.

-   **A second, independent reviewer:** GLM-5.3-flash, from a different
    company, Z.ai, so the work wasn't only checked by the same AI that
    helped build it.

-   **The hardware:** one MacBook. That's it.

Keeping myself honest

Several of my early results didn't hold up, and I retracted them
publicly. One test failed to repeat before a bigger, better one
confirmed the result. The work has been checked eleven times by AI
reviewers, most recently by three AI systems from three different
companies at once: Anthropic's Claude Fable, OpenAI's GPT-5.5 and Z.ai's
GLM. Every source I cite was read in full. Every correction is public.
No human expert has reviewed it yet. I'd welcome that.

Coming up in Part 2

Part 2 is for readers who want to check my work: how the watchdog is
built, the math behind it, the three monitoring tests plus the
experiment with NVIDIA's tool, all written down in advance, the outside
reviews, every source I cite, and everything that is still unproven.
Every number in this post links to a file there.

An invitation

All of this ran on one laptop. The next tests need bigger AI models,
much bigger test sets and specialized hardware. If you work at an AI
lab, a chip or cloud company, or a university and want to test this at
scale, or think I got something wrong, I'd love to hear from you:
yobie@ieee.org. The code, data and every correction are free for
research at github.com/YobieBenjamin/autonomic-graph-regulation.

If you take one thing from this: there is no single magic fix for AI
safety. It takes layers, each catching what the others miss, and the AI
can't be the lock on its own actions. My early results are promising,
and the work is just getting started.

Garbage in, gospel out. The answer isn't a more confident AI. It's a
nervous system that doesn't listen to its words, inside a stack of locks
it can't open by itself.

*This project is by me and AI: I came up with the ideas and directed the
work; the AI tools listed above helped with the code, the experiments,
the writing and the reviews. Part 2, the technical version, links every
number to its source on GitHub.*
