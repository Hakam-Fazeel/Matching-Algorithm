import pandas as pd

def match_mentors_with_interests(mentors_file, mentees_file):
    # Load data from Google Forms CSV exports
    mentors_df = pd.read_csv(mentors_file)
    mentees_df = pd.read_csv(mentees_file)

    # Standardize column names based on the Google Forms structure
    mentor_email_col = 'Email Address'
    mentee_email_col = 'Email Address'
    
    mentor_gender_col = 'Gender'
    mentee_gender_col = 'Gender'
    
    mentor_course_col = 'Course'
    mentee_course_col = 'Course'
    
    max_mentees_col = 'Max Mentees'

    # Initialize tracking structures
    mentors_df['Assigned_Mentees'] = [[] for _ in range(len(mentors_df))]
    mentees_df['Matched'] = False

    # Helper function to calculate similarity score between mentor and mentee
    def calc_score(mentor_row, mentee_row):
        # Handle potential empty values gracefully
        m_interests = set(str(mentor_row.get('Interests', '')).split(';'))
        t_interests = set(str(mentee_row.get('Interests', '')).split(';'))
        
        m_advice = set(str(mentor_row.get('Advice', '')).split(';'))
        t_advice = set(str(mentee_row.get('Advice', '')).split(';'))

        # Clean up empty strings that split might generate
        for s in [m_interests, t_interests, m_advice, t_advice]:
            s.discard('')
            s.discard('nan')

        # Score is the total count of overlapping interests and advice areas
        interest_overlap = len(m_interests.intersection(t_interests))
        advice_overlap = len(m_advice.intersection(t_advice))
        
        return interest_overlap + advice_overlap

    # Helper function to execute matching passes by gender pool
    def run_matching_pass(gender_val):
        m_subset = mentors_df[mentors_df[mentor_gender_col] == gender_val].index
        
        # Pass 1: Assign 1 matching course mentee (with highest score) to each eligible mentor
        for m_idx in m_subset:
            m_course = mentors_df.loc[m_idx, mentor_course_col]
            max_m = int(mentors_df.loc[m_idx, max_mentees_col])
            current_assigned = len(mentors_df.loc[m_idx, 'Assigned_Mentees'])

            if current_assigned < max_m:
                # Filter mentees: Same gender, same course, not yet matched
                eligible_mask = (
                    (~mentees_df['Matched']) & 
                    (mentees_df[mentee_gender_col] == gender_val) & 
                    (mentees_df[mentee_course_col] == m_course)
                )
                eligible_indices = mentees_df[eligible_mask].index

                if not eligible_indices.empty:
                    # Find the mentee with the highest similarity score
                    best_t_idx = max(
                        eligible_indices, 
                        key=lambda t_idx: calc_score(mentors_df.loc[m_idx], mentees_df.loc[t_idx])
                    )
                    
                    mentees_df.loc[best_t_idx, 'Matched'] = True
                    mentors_df.loc[m_idx, 'Assigned_Mentees'].append(
                        mentees_df.loc[best_t_idx, mentee_email_col]
                    )

        # Pass 2: Keep passing remaining same-course mentees to mentors based on score until capacity runs out
        assigned_more = True
        while assigned_more:
            assigned_more = False
            for m_idx in m_subset:
                m_course = mentors_df.loc[m_idx, mentor_course_col]
                max_m = int(mentors_df.loc[m_idx, max_mentees_col])
                current_assigned = len(mentors_df.loc[m_idx, 'Assigned_Mentees'])

                if current_assigned < max_m:
                    eligible_mask = (
                        (~mentees_df['Matched']) & 
                        (mentees_df[mentee_gender_col] == gender_val) & 
                        (mentees_df[mentee_course_col] == m_course)
                    )
                    eligible_indices = mentees_df[eligible_mask].index

                    if not eligible_indices.empty:
                        best_t_idx = max(
                            eligible_indices, 
                            key=lambda t_idx: calc_score(mentors_df.loc[m_idx], mentees_df.loc[t_idx])
                        )
                        
                        mentees_df.loc[best_t_idx, 'Matched'] = True
                        mentors_df.loc[m_idx, 'Assigned_Mentees'].append(
                            mentees_df.loc[best_t_idx, mentee_email_col]
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
        columns=['Mentor_Email'] + [f'Mentee_Email_{i+1}' for i in range(max_cols)],
    )
    matched_df.to_csv('mentor_mentee_matches.csv', index=False)

    # 2. Generate CSV file 2: Unmatched mentees and their requested course
    unmatched_df = mentees_df[~mentees_df['Matched']][[mentee_email_col, mentee_course_col, mentee_gender_col]]
    unmatched_df.columns = ['Mentee_Email', 'Course', 'Gender']
    unmatched_df.to_csv('unmatched_mentees.csv', index=False)

    # 3. Generate CSV file 3: Mentors capable of taking another mentee and their course
    available_mentors = []
    for _, row in mentors_df.iterrows():
        current_assigned = len(row['Assigned_Mentees'])
        max_m = int(row[max_mentees_col])
        if current_assigned < max_m:
            available_mentors.append({
                'Mentor_Email': row[mentor_email_col],
                'Course': row[mentor_course_col],
                'Current_Assigned': current_assigned,
                'Max_Mentees': max_m,
                'Gender': row[mentor_gender_col],
            })

    available_mentors_df = pd.DataFrame(available_mentors)
    available_mentors_df.to_csv('available_mentors.csv', index=False)

    print('Matching complete! Generated 3 CSV files successfully.')

# Run the script using the Google Form CSV names you specified
match_mentors_with_interests('Cleaned Mentors.csv', 'Cleaned Mentees.csv')