import pandas as pd


def match_mentors(mentors_file, mentees_file):
  # Load data from Excel or CSV files exported from Microsoft Forms
  if mentors_file.endswith('.xlsx'):
    mentors_df = pd.read_excel(mentors_file)
  else:
    mentors_df = pd.read_csv(mentors_file)

  if mentees_file.endswith('.xlsx'):
    mentees_df = pd.read_excel(mentees_file)
  else:
    mentees_df = pd.read_csv(mentees_file)

  # Standardize column names based on typical MS Forms export formats
  mentor_email_col = 'Email2'
  mentee_email_col = 'Email2'

  mentor_gender_col = 'Gender'
  mentee_gender_col = 'Gender'

  mentor_course_col = (
      'Course studying'
      if 'Course studying' in mentors_df.columns
      else mentors_df.columns[-1]
  )
  mentee_course_col = (
      'Course applying for'
      if 'Course applying for' in mentees_df.columns
      else mentees_df.columns[-1]
  )

  max_mentees_col = 'Max Mentees'

  # Initialize tracking structures
  mentors_df['Assigned_Mentees'] = [[] for _ in range(len(mentors_df))]
  mentees_df['Matched'] = False

  # Helper function to execute matching passes by gender pool
  def run_matching_pass(gender_val):
    m_subset = mentors_df[mentors_df[mentor_gender_col] == gender_val].index
    t_subset = mentees_df[
        (mentees_df[mentee_gender_col] == gender_val)
        & (~mentees_df['Matched'])
    ].index

    # Pass 1: Assign 1 matching course mentee to each eligible mentor
    for m_idx in m_subset:
      m_course = mentors_df.loc[m_idx, mentor_course_col]
      max_m = int(mentors_df.loc[m_idx, max_mentees_col])
      current_assigned = len(mentors_df.loc[m_idx, 'Assigned_Mentees'])

      if current_assigned < max_m:
        available_mentees = [
            t_idx
            for t_idx in t_subset
            if not mentees_df.loc[t_idx, 'Matched']
            and mentees_df.loc[t_idx, mentee_course_col] == m_course
        ]
        if available_mentees:
          t_idx = available_mentees[0]
          mentees_df.loc[t_idx, 'Matched'] = True
          mentors_df.loc[m_idx, 'Assigned_Mentees'].append(
              mentees_df.loc[t_idx, mentee_email_col]
          )

    # Pass 2: Keep passing remaining same-course mentees to mentors until capacity or mentees run out
    assigned_more = True
    while assigned_more:
      assigned_more = False
      for m_idx in m_subset:
        m_course = mentors_df.loc[m_idx, mentor_course_col]
        max_m = int(mentors_df.loc[m_idx, max_mentees_col])
        current_assigned = len(mentors_df.loc[m_idx, 'Assigned_Mentees'])

        if current_assigned < max_m:
          available_mentees = [
              t_idx
              for t_idx in t_subset
              if not mentees_df.loc[t_idx, 'Matched']
              and mentees_df.loc[t_idx, mentee_course_col] == m_course
          ]
          if available_mentees:
            t_idx = available_mentees[0]
            mentees_df.loc[t_idx, 'Matched'] = True
            mentors_df.loc[m_idx, 'Assigned_Mentees'].append(
                mentees_df.loc[t_idx, mentee_email_col]
            )
            assigned_more = True

  # Execute matching for Brothers then Sisters
  run_matching_pass('Brother')
  run_matching_pass('Sister')

  # 1. Generate CSV file 1: Mentor emails with adjacent mentee emails
  max_cols = mentors_df['Assigned_Mentees'].apply(len).max()
  max_cols = max(max_cols, 1)

  output_data = []
  for _, row in mentors_df.iterrows():
    row_data = [row[mentor_email_col]] + row['Assigned_Mentees']
    row_data += [''] * (max_cols - len(row['Assigned_Mentees']))
    output_data.append(row_data)

  matched_df = pd.DataFrame(
      output_data,
      columns=['Mentor_Email']
      + [f'Mentee_Email_{i+1}' for i in range(max_cols)],
  )
  matched_df.to_csv('mentor_mentee_matches.csv', index=False)

  # 2. Generate CSV file 2: Unmatched mentees and their requested course
  unmatched_df = mentees_df[~mentees_df['Matched']][
      [mentee_email_col, mentee_course_col]
  ]
  unmatched_df.columns = ['Mentee_Email', 'Course_Applying_For']
  unmatched_df.to_csv('unmatched_mentees.csv', index=False)

  # 3. Generate CSV file 3: Mentors capable of taking another mentee and their course
  available_mentors = []
  for _, row in mentors_df.iterrows():
    current_assigned = len(row['Assigned_Mentees'])
    max_m = int(row[max_mentees_col])
    if current_assigned < max_m:
      available_mentors.append({
          'Mentor_Email': row[mentor_email_col],
          'Course_Studying': row[mentor_course_col],
          'Current_Assigned': current_assigned,
          'Max_Mentees': max_m,
      })

  available_mentors_df = pd.DataFrame(available_mentors)
  available_mentors_df.to_csv('available_mentors.csv', index=False)

  print('Matching complete! Generated 3 CSV files successfully.')


# To run the script, replace with your actual file names:
match_mentors('UCAS mentor form.xlsx', 'UCAS mentee form.xlsx')
