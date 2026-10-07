#!/usr/bin/env python3
"""Build 1,000 unique Muse naming briefs, 100 .com candidates each.
No external agents are launched; dispatch requires authorized Muse control.
"""
import argparse
import csv
import itertools
import json
from datetime import datetime, timezone
from pathlib import Path

LANES = {
 "unexpected-metaphor": ["weather","navigation","astronomy","gardens","architecture","music","photography","ecology","cartography","materials"],
 "publishing-culture": ["literary culture","indie media","journalism","readers","subscription communities","public debate","ideas","essays","authorship","culture"],
 "ordinary-words": ["verbs","nouns","adjectives","colors","motion","sensations","instruments","places","objects","shapes"],
 "invented-brands": ["crisp","warm","quiet","energetic","refined","simple","classic","international","contemporary","editorial"],
 "institutions": ["libraries","exchanges","universities","museums","societies","public squares","guilds","observatories","archives","theaters"],
 "cultural-transfer": ["sport","fashion","hospitality","transportation","food","film","science","design","retail","architecture"],
 "linguistic": ["French","Italian","Spanish","Nordic","Germanic","Greek","Latin","Japanese","Portuguese","Old English"],
 "trust-without-jargon": ["memory","time","evidence","integrity","longevity","custody","authenticity","continuity","reputation","originality"],
 "writer-pride": ["novelist","journalist","researcher","biographer","columnist","essayist","poet","publisher","historian","independent creator"],
 "category-breaker": ["surreal","minimal","unexpected","contrarian","prestige","future-facing","playful","understated","monumental","human"],
}
MOODS = ["confident", "beautiful", "unconventional", "timeless", "friendly", "editorial", "iconic", "premium", "human", "remarkable"]
RECORD_FIELDS = ["job_id","status","lane","territory","angle","target_domains","result_file","agent_id","started_at","finished_at","error"]
def build(destination: Path):
    destination.mkdir(parents=True,exist_ok=True)
    rows=[]
    for lane,topics in LANES.items():
        for topic in topics:
            for angle in MOODS:
                index=len(rows)+1
                jid=f"MUSE-NAME-{index:04d}"
                prompt=(
                    f"JOB {jid}. Generate exactly 100 distinct, original, pronounceable consumer publishing platform brand names with EXACT matching .com domains. "
                    f"Creative territory: {lane}; focus: {topic}; tone: {angle}. "
                    "The platform rivals Medium/Substack while preserving verifiable, timestamped publication history. "
                    "The brand should feel like a cultural institution, not software infrastructure. "
                    "Avoid stet, proof/press/ink formulae, forced Latin endings, prefixes like get/try/use, hyphens, digits, alternate TLDs, and near-identical variants. "
                    "Prioritize names easy to hear, spell, and say in 'I publish on NAME.' "
                    "Do not claim a domain is available without registry RDAP verification. "
                    "Return exactly 100 rows as CSV: name,domain,pronunciation,why,brand_score_1_10,rdap_status,rdap_evidence_url; "
                    "set rdap_status to unchecked unless you really checked. Preserve all names even if registered; exceptional registered names enter acquisition research. "
                    "Do not register, purchase, or change domains. Deliver CSV and a short top-5 rationale."
                )
                result_file=f"results/{jid}.csv"
                (destination/"jobs"/f"{jid}.md").parent.mkdir(parents=True,exist_ok=True)
                (destination/"jobs"/f"{jid}.md").write_text(prompt+"\n")
                rows.append(dict(job_id=jid,status="prepared",lane=lane,territory=topic,angle=angle,target_domains=100,
                                 result_file=result_file,agent_id="",started_at="",finished_at="",error=""))
    assert len(rows)==1000
    with (destination/"jobs.csv").open("w",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=RECORD_FIELDS)
        writer.writeheader();writer.writerows(rows)
    info={"campaign":"exact-match-com-publishing","created_at_utc":datetime.now(timezone.utc).isoformat(),
          "total_jobs":len(rows),"domains_per_job":100,"target_candidates":100000,
          "prepared_jobs":len(rows),"launched_jobs":0,"verified_domains":0,
          "dispatch":"not launched: Fleet work/agent control grant required",
          "quality_gates":["phonetic & human review","cross-job deduplication","registry RDAP","trademark discovery","registrar eligibility"],
          "registry_note":"RDAP 404 signals unregistered, not a registrar purchase guarantee",
          "human_review":"No names approved automatically; don't invent uniqueness, availability or trademark clearance."}
    (destination/"campaign.json").write_text(json.dumps(info,indent=2)+"\n")
    return info
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--out",default="research/muse-naming");a=p.parse_args()
    print(json.dumps(build(Path(a.out)),indent=2))
