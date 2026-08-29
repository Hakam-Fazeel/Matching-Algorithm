import pandas as pd

def run_mentorship_matching(mentor_file, mentee_file, 
                            output_matches="mentor_mentee_matches.csv",
                            output_unmatched_mentees="unmatched_mentees.csv",
                            output_available_mentors="available_mentors.csv"):
    
    # Load data from Excel exports
    mentors_df = pd.read_excel(mentor_file)
    mentees_df = pd.read_excel(mentee_file)
    
    # Clean column names (strip whitespace)
    mentors_df.columns = [str(c).strip() for c in mentors_df.columns]
    mentees_df.columns = [str(c).strip() for c in mentees_df.columns]
    
    # --- CONFIGURABLE COLUMN NAMES ---
    # Update these strings if your Microsoft Forms columns differ slightly
    M_EMAIL = 'Email2'               # or 'Email2' depending on your form export
    M_GENDER = 'Gender'
    M_MAX = 'Max Mentees'
    M_COURSE = 'Course studying'             # or use faculty/course helper below
    
    ME_EMAIL = 'Email2'              # or 'email'
    ME_GENDER = 'Gender'
    ME_COURSE = 'Course applying for'
    
  
    
    
# sssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssss

import pandas as pd


def run_matching_algorithm(
    mentor_path="UCAS mentor form.xlsx", mentee_path="UCAS mentee form.xlsx"
):
  # Load excel data
  mentors = pd.read_excel(mentor_path)
  mentees = pd.read_excel(mentee_path)

  # Standardize column names for flexible matching
  mentors.columns = (
      mentors.columns.str.strip().str.lower().str.replace(" ", "_")
  )
  mentees.columns = (
      mentees.columns.str.strip().str.lower().str.replace(" ", "_")
  )



  m_email = 'Email2'
  m_gender = 'Gender'
  m_max = 'Max Mentees'
  m_course = 'Course studying'

  u_email = 'Email2'
  u_gender = 'Gender'
  u_course = 'Course applying for'


  # Normalize values for comparison
  mentors["gender_clean"] = (
      mentors[m_gender].astype(str).str.strip().str.lower()
  )
  mentees["gender_clean"] = (
      mentees[u_gender].astype(str).str.strip().str.lower()
  )
  mentors["course_clean"] = (
      mentors[m_course].astype(str).str.strip().str.lower()
  )
  mentees["course_clean"] = (
      mentees[u_course].astype(str).str.strip().str.lower()
  )

  matched_mentee_emails = set()
  mentor_allocations = {
      row[m_email]: {
          "gender": row[m_gender],
          "course": row[m_course],
          "max": int(row[m_max]),
          "assigned": [],
      }
      for _, row in mentors.iterrows()
  }

  def process_gender_group(gender_prefix):
    gender_mentors = [
        email
        for email, data in mentor_allocations.items()
        if data["gender"].startswith(gender_prefix)
    ]

    # Pass 1: Exact course match (1 mentee per mentor matching course)
    for mentor_email in gender_mentors:
      m_data = mentor_allocations[mentor_email]
      if len(m_data["assigned"]) >= m_data["max"]:
        continue

      available_mentees = mentees[
          (mentees["gender_clean"].str.startswith(gender_prefix))
          & (mentees["course_clean"] == m_data["course"])
          & (~mentees[u_email].isin(matched_mentee_emails))
      ]

      if not available_mentees.empty:
        mentee_row = available_mentees.iloc[0]
        m_email_val = mentee_row[u_email]
        m_data["assigned"].append(m_email_val)
        matched_mentee_emails.add(m_email_val)

    # Pass 2: Overflow capacity (fill remaining slots with any unmatched mentees of same gender)
    for mentor_email in gender_mentors:
      m_data = mentor_allocations[mentor_email]

      while len(m_data["assigned"]) < m_data["max"]:
        remaining_mentees = mentees[
            (mentees["gender_clean"].str.startswith(gender_prefix))
            & (~mentees[u_email].isin(matched_mentee_emails))
        ]

        if remaining_mentees.empty:
          break

        mentee_row = remaining_mentees.iloc[0]
        m_email_val = mentee_row[u_email]
        m_data["assigned"].append(m_email_val)
        matched_mentee_emails.add(m_email_val)

  # Execute passes for brothers ('m') and sisters ('f')
  process_gender_group("m")
  process_gender_group("f")

  # 1. Output CSV 1: Mentor assignments matrix
  match_rows = [
      [mentor_email] + data["assigned"]
      for mentor_email, data in mentor_allocations.items()
  ]
  max_mentees = (
      max(len(data["assigned"]) for data in mentor_allocations.values())
      if mentor_allocations
      else 0
  )
  col_names = ["mentor_email"] + [
      f"mentee_{i+1}" for i in range(max_mentees)
  ]
  padded_rows = [
      row + [""] * (len(col_names) - len(row)) for row in match_rows
  ]

  pd.DataFrame(padded_rows, columns=col_names).to_csv(
      "mentor_mentee_matches.csv", index=False
  )

  # 2. Output CSV 2: Unmatched mentees
  unmatched_df = mentees[~mentees[u_email].isin(matched_mentee_emails)][
      [u_email, u_course, u_gender]
  ]
  unmatched_df.to_csv("unmatched_mentees.csv", index=False)

  # 3. Output CSV 3: Under-utilized mentors with remaining capacity
  under_utilized = [
      {
          "mentor_email": email,
          "course": data["course"],
          "max_capacity": data["max"],
          "assigned_count": len(data["assigned"]),
          "remaining_capacity": data["max"] - len(data["assigned"]),
      }
      for email, data in mentor_allocations.items()
      if len(data["assigned"]) < data["max"]
  ]

  pd.DataFrame(under_utilized).to_csv(
      "under_utilized_mentors.csv", index=False
  )
  print("Matching complete. Output files generated successfully.")


if __name__ == "__main__":
  run_matching_algorithm()