"""Resolve curated papers plus newly published papers from selected journal families."""
import re

# Exact journal names avoid accidentally admitting unrelated journals such as
# Science China, Cellulose, Advanced Functional Materials or PNAS Nexus.
SCIENCE = {"science", "science advances", "science robotics", "science translational medicine", "science immunology", "science signaling"}
CELL_PRESS = {"cell", "cancer cell", "cell chemical biology", "cell genomics", "cell host & microbe", "cell host and microbe", "cell metabolism", "cell reports", "cell reports medicine", "cell reports methods", "cell reports physical science", "cell stem cell", "cell systems", "chem", "chem catalysis", "current biology", "developmental cell", "device", "immunity", "iscience", "joule", "matter", "med", "molecular cell", "neuron", "one earth", "patterns", "structure", "trends in biotechnology"}

def journal_matches(journal, policy):
    name = re.sub(r"\s+", " ", journal.strip().casefold())
    families = set(policy.get("journal_families", []))
    if "Nature Portfolio" in families and (name == "nature" or name.startswith(("nature ", "npj ")) or name in {"scientific reports", "microsystems & nanoengineering", "light: science & applications", "signal transduction and targeted therapy", "cell research", "cell discovery", "communications biology", "communications chemistry", "communications physics", "communications materials", "communications medicine", "communications engineering", "communications earth & environment"}):
        return True
    if "Science family" in families and name in SCIENCE:
        return True
    if "Cell Press" in families and name in CELL_PRESS:
        return True
    aliases = {"pnas": "proceedings of the national academy of sciences", "proc. natl. acad. sci. u.s.a.": "proceedings of the national academy of sciences"}
    name = aliases.get(name, name)
    return name in {j.casefold() for j in policy.get("additional_journals", [])}

def selected_paper_ids(papers, config):
    available = {p["id"] for p in papers}
    manual = set(config["paper_ids"])
    missing = manual - available
    if missing:
        raise ValueError(f"Selected publications not found: {sorted(missing)}")
    policy = config.get("automatic_inclusion", {})
    if policy.get("enabled"):
        manual.update(p["id"] for p in papers if p["id"] > policy.get("after_paper_id", 0) and journal_matches(p["journal"], policy))
    return sorted(manual, reverse=True)
