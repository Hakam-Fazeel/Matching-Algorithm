function sendPersonalizedMentorEmails() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  
  // 1. Get the three sheets by their exact tab names
  var matchSheet = ss.getSheetByName("Matches");
  var mentorSheet = ss.getSheetByName("Mentors");
  var menteeSheet = ss.getSheetByName("Mentees");
  
  if (!matchSheet || !mentorSheet || !menteeSheet) {
    SpreadsheetApp.getUi().alert("Error: Please make sure your 3 tabs are named exactly 'Matches', 'Mentors', and 'Mentees'.");
    return;
  }
  
  // 2. Load Mentor Data into a lookup map using Email Address
  var mentorData = mentorSheet.getDataRange().getValues();
  var mentorHeaders = mentorData[0];
  var mEmailIdx = mentorHeaders.indexOf("Email Address");
  var mNameIdx = mentorHeaders.indexOf("Full Name");
  var mCourseIdx = mentorHeaders.indexOf("Course");
  var mInterestsIdx = mentorHeaders.indexOf("Interests");
  
  var mentorMap = {};
  for (var i = 1; i < mentorData.length; i++) {
    var email = mentorData[i][mEmailIdx];
    if (email) {
      mentorMap[email.toString().trim().toLowerCase()] = {
        name: mentorData[i][mNameIdx],
        course: mentorData[i][mCourseIdx],
        interests: mentorData[i][mInterestsIdx]
      };
    }
  }
  
  // 3. Load Mentee Data into a lookup map using Email Address
  var menteeData = menteeSheet.getDataRange().getValues();
  var menteeHeaders = menteeData[0];
  var tEmailIdx = menteeHeaders.indexOf("Email Address");
  var tNameIdx = menteeHeaders.indexOf("Full Name");
  var tCourseIdx = menteeHeaders.indexOf("Course");
  var tInterestsIdx = menteeHeaders.indexOf("Interests");
  
  var menteeMap = {};
  for (var i = 1; i < menteeData.length; i++) {
    var email = menteeData[i][tEmailIdx];
    if (email) {
      menteeMap[email.toString().trim().toLowerCase()] = {
        name: menteeData[i][tNameIdx],
        course: menteeData[i][tCourseIdx],
        interests: menteeData[i][tInterestsIdx]
      };
    }
  }
  
  // 4. Process Matches and Send Personalized Emails
  var matchData = matchSheet.getDataRange().getValues();
  var successCount = 0;
  
  for (var i = 1; i < matchData.length; i++) {
    var mentorEmail = matchData[i][0];
    if (!mentorEmail || mentorEmail.toString().trim() === "") continue;
    
    var cleanMentorEmail = mentorEmail.toString().trim().toLowerCase();
    var mentorInfo = mentorMap[cleanMentorEmail];
    
    if (!mentorInfo) continue; // Skip if mentor info isn't found
    
    var mentorName = mentorInfo.name || "Mentor";
    
    // Build a detailed list of assigned mentees
    var menteeDetailsList = [];
    for (var j = 1; j < matchData[i].length; j++) {
      var menteeEmail = matchData[i][j];
      if (menteeEmail && menteeEmail.toString().trim() !== "") {
        var cleanMenteeEmail = menteeEmail.toString().trim().toLowerCase();
        var menteeInfo = menteeMap[cleanMenteeEmail];
        
        if (menteeInfo) {
          menteeDetailsList.push(
            "• Name: " + menteeInfo.name + "\n" +
            "  Email: " + menteeEmail.toString().trim() + "\n" +
            "  Course Applying For: " + menteeInfo.course + "\n" +
            "  Interests: " + (menteeInfo.interests || "None specified")
          );
        } else {
          menteeDetailsList.push("• Email: " + menteeEmail.toString().trim() + " (Details not found in Mentees tab)");
        }
      }
    }
    
    if (menteeDetailsList.length === 0) continue;
    
    // Construct the personalized email body
    var subject = "Your Assigned Mentees & Conversation Starters - University Mentorship Scheme";
    var body = "Hi " + mentorName + ",\n\n" +
               "Thank you so much for volunteering as a mentor for our university mentorship scheme! As a reminder, you are studying " + mentorInfo.course + " and share interests in: " + (mentorInfo.interests || "None specified") + ".\n\n" +
               "We have successfully matched you with the following student(s):\n\n" +
               menteeDetailsList.join("\n\n") + "\n\n" +
               "Please reach out to them via email to introduce yourself, schedule a chat, and use their shared interests as a great starting point for conversation!\n\n" +
               "Best regards,\n" +
               "Mentorship Scheme Organisers";
    
    try {
      MailApp.sendEmail(mentorEmail, subject, body);
      successCount++;
    } catch (e) {
      Logger.log("Failed to send to " + mentorEmail + ": " + e.toString());
    }
  }
  
  SpreadsheetApp.getUi().alert("Finished! Successfully sent personalized emails to " + successCount + " mentors.");
}