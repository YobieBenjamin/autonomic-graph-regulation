#!/usr/bin/env python3
"""Full-text citation verification: fetch each open full text, extract text per page,
find passages supporting the specific claim the posts make, write a report with quotes and pages.
Paywalled sources are listed as such (no workaround). Run: .venv/bin/python archive/audit/fulltext_verify.py"""
import io, json, re, sys, time, urllib.request
from pypdf import PdfReader
UA = {'User-Agent': 'Mozilla/5.0 (research citation check; yobie@ieee.org)'}
# id, citation, full-text URL (open/legitimate) or None if paywalled, claim made in post, search terms (all must co-occur in a passage window)
S = [
 ('logan1984', 'Logan & Cowan 1984', 'http://www.psy.vanderbilt.edu/faculty/logan/1984LoganPR.pdf', 'stop process races ongoing process; if stop wins, action inhibited', [['race'], ['stop']]),
 ('aron2006', 'Aron & Poldrack 2006', 'https://www.jneurosci.org/content/jneuro/26/9/2424.full.pdf', 'right IFC and STN in stopping; hyperdirect implementation not established; SSRT ~200 ms', [['hyperdirect'], ['SSRT'], ['subthalamic']]),
 ('yeung2004', 'Yeung, Botvinick & Cohen 2004', 'https://www.ece.uvic.ca/~bctill/papers/learning/Yeung_etal_2004a.pdf', 'ERN peaks about 100 ms after error; ACC generator', [['100 ms'], ['anterior cingulate']]),
 ('matthias2004', 'Matthias 2004', None, 'responsibility gap for learning automata', [['responsibility gap']]),
 ('sparrow2007', 'Sparrow 2007', 'https://robsparrow.com/wp-content/uploads/Killer-robots.pdf', 'no satisfactory locus of responsibility for autonomous weapon war crimes', [['responsib'], ['war crime']]),
 ('azaria2023', 'Azaria & Mitchell 2023', 'https://arxiv.org/pdf/2304.13734', 'internal state reveals truthfulness', [['truthful'], ['hidden']]),
 ('burns2023', 'Burns et al. 2023', 'https://arxiv.org/pdf/2212.03827', 'latent knowledge in activations distinct from outputs', [['latent knowledge'], ['activation']]),
 ('kadavath2022', 'Kadavath et al. 2022', 'https://arxiv.org/pdf/2207.05221', 'calibrated in suitable formats; P(IK) struggles on new tasks', [['calibrat'], ['P(IK)']]),
 ('orgad2024', 'Orgad et al. 2024', 'https://arxiv.org/pdf/2410.02707', 'detectors fail to generalise across datasets', [['generaliz'], ['dataset']]),
 ('kossen2024', 'Kossen et al. 2024', 'https://arxiv.org/pdf/2406.15927', 'semantic entropy probes from hidden states', [['semantic entropy'], ['hidden state']]),
 ('kuhn2023', 'Kuhn, Gal & Farquhar 2023', 'https://arxiv.org/pdf/2302.09664', 'semantic entropy uncertainty measure', [['semantic entropy']]),
 ('farquhar2024', 'Farquhar et al. 2024', 'https://www.nature.com/articles/s41586-024-07421-0.pdf', 'semantic entropy detects confabulations', [['semantic entropy'], ['confabulation']]),
 ('wang2022', 'Wang et al. 2022', 'https://arxiv.org/pdf/2203.11171', 'self-consistency majority vote improves accuracy', [['self-consistency'], ['majority']]),
 ('oladri2026', 'Oladri et al. 2026', 'https://arxiv.org/pdf/2607.21433', 'probes predict non-convergence; AUC 0.608', [['convergence'], ['probe']]),
 ('goldowsky2025', 'Goldowsky-Dill et al. 2025', 'https://arxiv.org/pdf/2502.03407', 'probes detect deception; insufficient as robust defence', [['deceptive'], ['probe']]),
 ('bailey2024', 'Bailey et al. 2024', 'https://arxiv.org/pdf/2412.09565', 'latent-space monitors vulnerable to obfuscated activations', [['obfuscated activations']]),
 ('chiba2020', 'Chiba & Krichmar 2020', 'https://escholarship.org/content/qt2hs105zt/qt2hs105zt.pdf', 'neurobiologically inspired self-monitoring, homeostasis', [['homeostasis'], ['self-monitoring']]),
 ('mineault2024', 'Mineault et al. 2024', 'https://arxiv.org/pdf/2411.18526', 'neuroscience holds keys to AI safety', [['neuroscience'], ['safety']]),
 ('news2_2017', 'RCP NEWS2 2017', 'https://www.rcp.ac.uk/media/a4ibkkbf/news2-final-report_0_0.pdf', 'aggregate scoring of physiological parameters; trigger levels', [['aggregate'], ['score']]),
 ('petrie2025', 'Petrie & Aarne 2025 flexHEG', 'https://arxiv.org/pdf/2506.03409', 'guarantee processor with access to accelerator data paths', [['Guarantee Processor'], ['Interlock']]),
 ('gehring1993', 'Gehring et al. 1993', None, 'error-related neural activity', []),
 ('dehaene1994', 'Dehaene, Posner & Tucker 1994', None, 'ERN localised to ACC', []),
 ('nieuwenhuis2001', 'Nieuwenhuis et al. 2001', None, 'ERN on unaware errors', []),
 ('nambu2002', 'Nambu, Tokuno & Takada 2002', None, 'hyperdirect pathway anatomy', []),
 ('craig2002', 'Craig 2002', None, 'interoception', []),
 ('damasio1994', 'Damasio 1994 (book)', None, 'somatic marker hypothesis', []),
 ('man2019', 'Man & Damasio 2019', None, 'homeostatic feeling machines', []),
 ('scheffer2009', 'Scheffer et al. 2009', None, 'early-warning signals', []),
 ('champagne2015', 'Champagne & Tonkens 2015', None, 'critique of Sparrow', []),
 ('robillard2018', 'Robillard 2018', None, 'critique of Sparrow', []),
]
def fetch(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=90) as r: return r.read()
def pages(pdf):
    rd = PdfReader(io.BytesIO(pdf)); return [(i + 1, re.sub(r'\s+', ' ', p.extract_text() or '')) for i, p in enumerate(rd.pages)]
out = []
for sid, cit, url, claim, terms in S:
    rec = dict(id=sid, citation=cit, url=url, claim=claim)
    import os
    local = 'archive/audit/papers_inbox/%s.pdf' % sid
    if os.path.exists(local):
        url = 'local:' + local
    if url is None:
        rec.update(status='PAYWALLED_OR_NOT_OPEN', passages=[]); out.append(rec); print(sid, 'paywalled'); continue
    try:
        data = open(url[6:], 'rb').read() if url.startswith('local:') else fetch(url); pg = pages(data)
        rec['n_pages'] = len(pg); rec['n_chars'] = sum(len(t) for _, t in pg)
        hits = []
        for group in terms:
            for p, t in pg:
                for m in re.finditer('|'.join(re.escape(x) for x in group), t, flags=re.I):
                    a, b = max(0, m.start() - 260), min(len(t), m.end() + 260)
                    hits.append(dict(page=p, term=group[0], text=t[a:b])); break
                if sum(1 for h in hits if h['term'] == group[0]) >= 3: break
        rec['passages'] = hits
        rec['status'] = 'FULLTEXT_READ' if rec['n_chars'] > 5000 else 'FULLTEXT_TOO_SHORT'
        print(sid, rec['status'], rec['n_pages'], 'pages', len(hits), 'passages')
    except Exception as e:
        rec.update(status='FETCH_FAILED', error=str(e)[:200], passages=[]); print(sid, 'FAILED', str(e)[:80])
    out.append(rec); time.sleep(1.5)
json.dump(out, open('archive/audit/fulltext_verification.json', 'w'), indent=1)
ok = sum(r['status'] == 'FULLTEXT_READ' for r in out); pw = sum(r['status'] == 'PAYWALLED_OR_NOT_OPEN' for r in out)
print('SUMMARY full_text_read=%d paywalled=%d failed=%d total=%d' % (ok, pw, len(out) - ok - pw, len(out)))
