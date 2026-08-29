import pandas as pd
import csv

# --- CONFIGURATION ---
# Updated file names to reference the new files
MENTOR_FILE = "UCAS mentor form.xlsx"
MENTEE_FILE = "UCAS mentee form.xlsx"
OUTPUT_FILE = "matched_mentors.csv"

# Updated Column Names based on the new form structure
MENTOR_EMAIL = "Email2" # Update if mentors use a different email column header
MENTOR_MAX = "Max Mentees" 

MENTEE_EMAIL = "email2"
MENTEE_ALT_OK = "Okay with someone in Faculty but not desired course? " # Matches the header shown in the mentee image

# Similarity Dictionary: Define which courses are acceptable alternatives
# Note: Lowercase mapping is used here to avoid case-sensitivity issues
SIMILAR_COURSES = {
    'eee': ['eie'],
    'eie': ['eee'],
    'mecheng': ['aeroeng', 'civileng', 'eie'], # Added 'eie' as an example
    'medicine': ['biomed'],
    'physics': ['maths', 'chemistry']
}

def consolidate_course(row):
    """
    Extracts the actual course by checking the branched columns.
    It returns the first non-empty value found in the specific faculty columns.
    """
    course_columns = ['Engineerings', 'Medicines', 'NatSci', 'Business']
    
    for col in course_columns:
        if col in row and pd.notna(row[col]) and str(row[col]).strip() != '':
            # Return lowercase and stripped text for robust matching
            return str(row[col]).strip().lower() 
            
    return "unknown"

def main():
    # 1. Load Data
    try:
        mentors_df = pd.read_excel(MENTOR_FILE)
        mentees_df = pd.read_excel(MENTEE_FILE)
    except FileNotFoundError as e:
        print(f"Error loading files. Ensure the files are in the same folder as this script. Details: {e}")
        return

    # 2. Organize Mentors (Applying the course consolidation)
    mentors = []
    for _, row in mentors_df.iterrows():
        # Assuming Mentors also use branching logic. If they use a single column, 
        # replace consolidate_course(row) with str(row['Your Column Name']).strip().lower()
        mentors.append({
            'email': row.get(MENTOR_EMAIL, 'Unknown Email'),
            'course': consolidate_course(row),
            'capacity': int(row.get(MENTOR_MAX, 1)), # Default to 1 if max is missing
            'assigned_mentees': []
        })

    # 3. Organize Mentees & First Pass (Exact Matches)
    unassigned_mentees = []
    
    for _, row in mentees_df.iterrows():
        mentee_email = row.get(MENTEE_EMAIL)
        mentee_course = consolidate_course(row)
        mentee_alt_ok = str(row.get(MENTEE_ALT_OK, 'No')).strip().lower()
        
        assigned = False
        
        # Look for a mentor with the exact course and available capacity
        for mentor in mentors:
            if mentor['course'] == mentee_course and len(mentor['assigned_mentees']) < mentor['capacity']:
                mentor['assigned_mentees'].append(mentee_email)
                assigned = True
                break
        
        if not assigned:
            unassigned_mentees.append({
                'email': mentee_email,
                'course': mentee_course,
                'alt_ok': mentee_alt_ok
            })

    # 4. Second Pass: Alternative Course Matches
    final_unassigned = []
    
    for mentee in unassigned_mentees:
        assigned = False
        
        # Check if they are okay with an alternative course 
        if mentee['alt_ok'] == 'yes':
            similar_options = SIMILAR_COURSES.get(mentee['course'], [])
            
            for mentor in mentors:
                if mentor['course'] in similar_options and len(mentor['assigned_mentees']) < mentor['capacity']:
                    mentor['assigned_mentees'].append(mentee['email'])
                    assigned = True
                    break
                    
        if not assigned:
            final_unassigned.append(mentee['email'])

    # 5. Export to CSV (Format: Mentor Email, Mentee 1, Mentee 2, ...)
    with open(OUTPUT_FILE, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        
        # Write header dynamically based on the maximum capacity found
        max_capacity = max([m['capacity'] for m in mentors] + [0])
        headers = ["Mentor Email"] + [f"Mentee {i+1}" for i in range(max_capacity)]
        writer.writerow(headers)
        
        for mentor in mentors:
            # This constructs a single row placing mentees immediately next to the mentor
            row = [mentor['email']] + mentor['assigned_mentees']
            writer.writerow(row)

    print(f"Matching complete! Output saved to {OUTPUT_FILE}")
    print(f"Total unassigned mentees due to lack of capacity/matches: {len(final_unassigned)}")
    print(unassigned_mentees)

if __name__ == "__main__":
    main()