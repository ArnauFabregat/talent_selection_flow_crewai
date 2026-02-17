from datetime import datetime


def render_to_markdown(
        process_type: str,
        metadata_dict: dict,
        related_docs: dict,
        gap_analysis_output: dict,
        inverview_questions_output: dict,
) -> str:
    if process_type == "job":
        report = [
            "# Recruitment Analysis Report",
            f"*Date: {datetime.today().strftime('%Y-%m-%d')}*",
            "\nThis document provides a comprehensive evaluation of the job role against several targeted candidates' cvs. "
            "The analysis was performed by an automated multi-agent system (CrewAI) that identifies skill gaps, "
            "calculates role similarity, and generates tailored interview strategies to bridge the identified technical voids.",
            "## Job summary",
            "*This section provides a high-level overview of the job role, extracting key technical "
            "competencies, regional availability, and educational background to establish a baseline for comparison.*",
        ]
        # Add candidate info
        for k, v in metadata_dict.items():
            report.append(f"- **{k.replace("_", " ").capitalize()}**: {v}")

        # Add matched cvs summary
        report.append("## Matched cvs summary")
        report.append(
            "*A curated list of candidates' cvs that demonstrate high semantic alignment with the job role. Each match "
            "includes a 'Similarity Score' (where 1.0 is a perfect match) and a summary of the responsibilities"
            "the candidate would undertake.*"
        )
        for k, v in related_docs.items():
            report.append(f"### {v['title']} (ID: {k})")
            for k2, v2 in v.items():
                report.append(f"- **{k2.replace("_", " ").capitalize()}**: {v2}")

        # Add gaps analysis
        report.append("## Gaps analysis")
        report.append(
            "*An objective technical audit identifying the delta between the candidate's current skillset and the job's "
            "mandatory requirements.*"
        )
        for k, v in gap_analysis_output['docs'].items():
            report.append(f"### CV ID: {k}")
            for k2, v2 in v.items():
                report.append(f"- **{k2.replace("_", " ").capitalize()}**: {', '.join(v2)}")

        # Add interview questions
        report.append("## Interview questions")
        report.append(
            "*Strategic guidance for the hiring team. These questions are algorithmically generated to verify existing "
            "strengths, probe the specific gaps identified in the previous section, and assess the candidate's "
            "seniority through behavioral scenarios.*"
        )
        for k, v in inverview_questions_output['docs'].items():
            report.append(f"### CV ID: {k}")
            for k2, v2 in v.items():
                report.append(f"- **{k2.replace("_", " ").capitalize()}**:")
                for i in v2:
                    report.append(f"\n\t → Question: {i["question"]}")
                    report.append(f"\n\t ✓ Response: {i["response"]}")

    elif process_type == "cv":
        report = [
            "# Recruitment Analysis Report",
            f"*Date: {datetime.today().strftime('%Y-%m-%d')}*",
            "\nThis document provides a comprehensive evaluation of the candidate against several targeted job roles. "
            "The analysis was performed by an automated multi-agent system (CrewAI) that identifies skill gaps, "
            "calculates role similarity, and generates tailored interview strategies to bridge the identified technical voids.",
            "## Candidate summary",
            "*This section provides a high-level overview of the candidate's professional profile, extracting key technical "
            "competencies, regional availability, and educational background to establish a baseline for comparison.*",
        ]
        # Add candidate info
        for k, v in metadata_dict.items():
            report.append(f"- **{k.replace("_", " ").capitalize()}**: {v}")

        # Add matched jobs summary
        report.append("## Matched jobs summary")
        report.append(
            "*A curated list of roles that demonstrate high semantic alignment with the candidate's profile. Each match "
            "includes a 'Similarity Score' (where 1.0 is a perfect match) and a summary of the responsibilities"
            "the candidate would undertake.*"
        )
        for k, v in related_docs.items():
            report.append(f"### {v['title']} (ID: {k})")
            for k2, v2 in v.items():
                report.append(f"- **{k2.replace("_", " ").capitalize()}**: {v2}")

        # Add gaps analysis
        report.append("## Gaps analysis")
        report.append(
            "*An objective technical audit identifying the delta between the candidate's current skillset and the job's "
            "mandatory requirements.*"
        )
        for k, v in gap_analysis_output['docs'].items():
            report.append(f"### Job ID: {k}")
            for k2, v2 in v.items():
                report.append(f"- **{k2.replace("_", " ").capitalize()}**: {', '.join(v2)}")

        # Add interview questions
        report.append("## Interview questions")
        report.append(
            "*Strategic guidance for the hiring team. These questions are algorithmically generated to verify existing "
            "strengths, probe the specific gaps identified in the previous section, and assess the candidate's "
            "seniority through behavioral scenarios.*"
        )
        for k, v in inverview_questions_output['docs'].items():
            report.append(f"### Job ID: {k}")
            for k2, v2 in v.items():
                report.append(f"- **{k2.replace("_", " ").capitalize()}**:")
                for i in v2:
                    report.append(f"\n\t → Question: {i["question"]}")
                    report.append(f"\n\t ✓ Response: {i["response"]}")
    else:
        report = []
    return "\n".join(report)
