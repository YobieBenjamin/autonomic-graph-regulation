# Citation registry (updated 2026-10-04)

Rule for the published series: every citation must have been read in full text. Evidence: archive/audit/fulltext_verification.json (pipeline: archive/audit/fulltext_verify.py) plus the two papers read directly on 2026-10-04 (Aron & Poldrack; Yeung et al.).

## Cited in the published series (all read in full)

| # | Citation | Source | Access | Supports |
|---|---|---|---|---|
| 1 | Logan & Cowan 1984, Psychological Review 91(3):295-327 | https://doi.org/10.1037/0033-295X.91.3.295 (author PDF: psy.vanderbilt.edu) | full text (pipeline, author PDF) | stop process races the go process |
| 2 | Aron & Poldrack 2006, J Neurosci 26(9):2424-2433 | https://doi.org/10.1523/JNEUROSCI.4682-05.2006 (journal PDF jneurosci.org; PMC6793670) | full text (journal PDF read 2026-10-04; pipeline fetch blocked 403) | right IFC and STN in stopping; stopped in as little as about 120 ms; SSRT 187.4 and 189.3 ms (Table 1); hyperdirect route tentatively proposed |
| 3 | Yeung, Botvinick & Cohen 2004, Psychological Review 111(4):931-959 | https://doi.org/10.1037/0033-295X.111.4.931 | full text (author-hosted PDF read 2026-10-04; that copy later returned 404 to another checker; use DOI) | ERN begins around the error and peaks roughly 100 ms later; most likely generator anterior cingulate cortex; explicit error report about 700 ms; reviews original reports (Falkenstein; Gehring; Dehaene) |
| 4 | Sparrow 2007, J Appl Philos 24(1):62-77 | https://robsparrow.com/wp-content/uploads/Killer-robots.pdf | full text (pipeline) | responsibility gap argued for autonomous weapons |
| 5 | Azaria & Mitchell 2023, Findings of EMNLP | https://arxiv.org/abs/2304.13734 | full text (pipeline) | internal state reveals truthfulness |
| 6 | Burns et al. 2023, ICLR | https://arxiv.org/abs/2212.03827 | full text (pipeline) | latent knowledge in activations |
| 7 | Kadavath et al. 2022 | https://arxiv.org/abs/2207.05221 | full text (pipeline) | self-evaluation partly works; degrades on new tasks |
| 8 | Orgad et al. 2024 | https://arxiv.org/abs/2410.02707 | full text (pipeline) | detectors generalise poorly across datasets |
| 9 | Kossen et al. 2024 | https://arxiv.org/abs/2406.15927 | full text (pipeline) | semantic entropy probes |
| 10 | Kuhn, Gal & Farquhar 2023, ICLR | https://arxiv.org/abs/2302.09664 | full text (pipeline) | semantic entropy |
| 11 | Farquhar et al. 2024, Nature 630:625-630 | https://www.nature.com/articles/s41586-024-07421-0 | full text (pipeline, open-access Nature PDF) | semantic entropy detects confabulations |
| 12 | Wang et al. 2022 (ICLR 2023) | https://arxiv.org/abs/2203.11171 | full text (pipeline) | self-consistency proposed for accuracy; adapted here as a disagreement signal |
| 13 | Oladri, Jawahar & Mohamed 2026 | https://arxiv.org/abs/2607.21433 | full text (pipeline); author list per arXiv listing | hidden-state probes predict non-convergence |
| 14 | Goldowsky-Dill et al. 2025, ICML | https://arxiv.org/abs/2502.03407 | full text (pipeline) | deception probes; insufficient as robust defence |
| 15 | Bailey et al. 2024 | https://arxiv.org/abs/2412.09565 | full text (pipeline) | latent-space monitors vulnerable to obfuscated activations |
| 16 | Chiba & Krichmar 2020, Proc IEEE 108(7):976-986 | https://escholarship.org/uc/item/2hs105zt | full text (pipeline) | homeostasis and neurobiologically inspired self-monitoring |
| 17 | Mineault et al. 2024, NeuroAI for AI Safety | https://arxiv.org/abs/2411.18526 | full text (pipeline) | neuroscience for AI safety |
| 18 | Byrnes 2022, Intro to Brain-Like-AGI Safety (blog series) | https://www.alignmentforum.org/s/HzcM2dkCq7fwXBej8 (dates: sjbyrnes.com/agi.html, published Jan-May 2022, revised July 2024) | full text (series pages) | brain-like AGI safety |
| 19 | Royal College of Physicians 2017, NEWS2 | https://www.rcp.ac.uk/media/a4ibkkbf/news2-final-report_0_0.pdf | full text (pipeline) | early-warning score template |
| 20 | Petrie & Aarne 2025, flexHEG | https://arxiv.org/abs/2506.03409 | full text (pipeline); author list per arXiv listing | guarantee processor with access to accelerator data paths |
| 21 | NVIDIA 2026, Open Agent Safety Platform press release (28 Sep 2026) | NVIDIA press release, mirrored in full at telecomtv.com and finviz.com | full text (release text) | OpenShell open source and broadly available; Sentry a reference design on BlueField-4; the millisecond-quarantine claim is NVIDIA's (NVIDIA agent-safety page, nvidia.com/en-us/solutions/ai/agent-safety; also stated by Jensen Huang in launch coverage), not benchmarked |

## Verified to exist but NOT cited (full text not available to us)

Each was confirmed at abstract or record level on 2026-10-03, then removed from the series on 2026-10-04 because the full text could not be read. Claims they supported were re-sourced to papers above or removed. They can be restored if a full text is read (drop PDFs in archive/audit/papers_inbox/; PDFs are git-ignored).

- Gehring et al. 1993
- Dehaene, Posner & Tucker 1994
- Nieuwenhuis et al. 2001
- Nambu, Tokuno & Takada 2002
- Craig 2002
- Damasio 1994
- Man & Damasio 2019
- Scheffer et al. 2009
- Matthias 2004
- Champagne & Tonkens 2015
- Robillard 2018
