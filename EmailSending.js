function sendAllMentorshipEmails() {
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
  
  var mentorMap = {};
  for (var i = 1; i < mentorData.length; i++) {
    var email = mentorData[i][mEmailIdx];
    if (email) {
      mentorMap[email.toString().trim().toLowerCase()] = {
        name: mentorData[i][mNameIdx],
        course: mentorData[i][mCourseIdx]
      };
    }
  }
  
  // 3. Load Mentee Data into a lookup map using Email Address
  var menteeData = menteeSheet.getDataRange().getValues();
  var menteeHeaders = menteeData[0];
  var tEmailIdx = menteeHeaders.indexOf("Email Address");
  var tNameIdx = menteeHeaders.indexOf("Full Name");
  var tCourseIdx = menteeHeaders.indexOf("Course");
  
  var menteeMap = {};
  for (var i = 1; i < menteeData.length; i++) {
    var email = menteeData[i][tEmailIdx];
    if (email) {
      menteeMap[email.toString().trim().toLowerCase()] = {
        name: menteeData[i][tNameIdx],
        course: menteeData[i][tCourseIdx]
      };
    }
  }
  
  // 4. Process Matches and Send Emails
  var matchData = matchSheet.getDataRange().getValues();
  var mentorEmailCount = 0;
  var menteeEmailCount = 0;
  
  // Replace this placeholder with your actual webinar link
  var webinarLink = "https://your-actual-webinar-link-here.com"; 
  
  for (var i = 1; i < matchData.length; i++) {
    var rawMentorEmail = matchData[i][0];
    if (!rawMentorEmail || rawMentorEmail.toString().trim() === "") continue;
    
    var cleanMentorEmail = rawMentorEmail.toString().trim().toLowerCase();
    var mentorInfo = mentorMap[cleanMentorEmail];
    
    if (!mentorInfo) continue; // Skip if mentor details aren't found
    
    var mentorName = mentorInfo.name || "Mentor";
    var mentorCourse = mentorInfo.course || "Not Specified";
    
    // Collect all valid assigned mentees for this mentor row
    var assignedMentees = [];
    for (var j = 1; j < matchData[i].length; j++) {
      var rawMenteeEmail = matchData[i][j];
      if (rawMenteeEmail && rawMenteeEmail.toString().trim() !== "") {
        var cleanMenteeEmail = rawMenteeEmail.toString().trim().toLowerCase();
        var menteeInfo = menteeMap[cleanMenteeEmail];
        
        assignedMentees.push({
          email: rawMenteeEmail.toString().trim(),
          name: menteeInfo ? menteeInfo.name : "Student",
          course: menteeInfo ? menteeInfo.course : "Not Specified"
        });
      }
    }
    
    if (assignedMentees.length === 0) continue;
    
    // ==========================================
    // A. BUILD & SEND EMAIL TO THE MENTOR
    // ==========================================
    var menteeBlocksHtml = "";
    var menteeBlocksText = "";
    
    for (var m = 0; m < assignedMentees.length; m++) {
      var curMentee = assignedMentees[m];
      menteeBlocksHtml += "Name: " + curMentee.name + "<br>" +
                          "Course: " + curMentee.course + "<br>" +
                          "Email: " + curMentee.email + "<br><br>";
                          
      menteeBlocksText += "Name: " + curMentee.name + "\n" +
                          "Course: " + curMentee.course + "\n" +
                          "Email: " + curMentee.email + "\n\n";
    }
    
    var mentorSubject = "Your Assigned Mentees - STEM Muslims UCAS Mentorship Scheme";
    var mentorHtmlBody = "<p>As salamu alaykum,</p>" +
                         "<p>Jazakallah khayr for taking the time to sign up as a mentor for the STEM Muslim's UCAS Mentorship Scheme!</p>" +
                         "<p>This scheme aims to pair Imperial undergraduates with year 13s looking to apply to university this academic year. As a mentor, you will provide personalised, one-to-one support to guide your mentees through their UCAS application with confidence.</p>" +
                         "<p>Your role is to support them every step of the way &mdash; whether you have questions about the UCAS process, need help writing a compelling personal statement, or want to prepare for upcoming interviews or admissions tests.</p>" +
                         "<p><strong>Your mentees are:</strong><br><br>" + menteeBlocksHtml + "</p>" +
                         "<p>Please keep in mind that it is your responsibility to reply to any emails from your mentee. We appreciate that you may have busy periods, but we ask that you communicate this to your mentee so they are able to make the most of this scheme. Please also ensure you keep communications via email only!</p>" +
                         "<p>Thank you once again for helping us support these students with their applications. May Allah reward you greatly for your efforts and grant you ease in your affairs, Ameen.</p>" +
                         "<p>Jazakallah khayr,<br><br>The STEM Muslims Outreach Team</p>";
                         
    try {
      MailApp.sendEmail({
        to: rawMentorEmail.toString().trim(),
        subject: mentorSubject,
        body: mentorHtmlBody.replace(/<[^>]*>/g, ""), // Plain text fallback
        htmlBody: mentorHtmlBody
      });
      mentorEmailCount++;
    } catch (e) {
      Logger.log("Failed to email mentor " + rawMentorEmail + ": " + e.toString());
    }
    
    // ==========================================
    // B. BUILD & SEND EMAILS TO EACH MATCHED MENTEE
    // ==========================================
    for (var m = 0; m < assignedMentees.length; m++) {
      var curMentee = assignedMentees[m];
      
      var menteeSubject = "Your Assigned Mentor - STEM Muslims UCAS Mentorship Scheme";
      var menteeHtmlBody = "<p>As salamu alaykum,</p>" +
                           "<p>Congratulations, your application to the STEM Muslim's UCAS Mentorship Scheme was successful!&#127881;</p>" +
                           "<p>This scheme pairs you with an Imperial undergraduate mentor who will provide personalised, one-to-one support to guide you through your UCAS application with confidence.</p>" +
                           "<p>Your mentor is here to support you every step of the way &mdash; whether you have questions about the UCAS process, need help writing a compelling personal statement, or want to prepare for upcoming interviews or admissions tests.</p>" +
                           "<p><strong>Your mentor is:</strong><br>" +
                           "Name: " + mentorName + "<br>" +
                           "Course: " + mentorCourse + "<br>" +
                           "Email: " + rawMentorEmail.toString().trim() + "</p>" +
                           "<p>Please keep in mind that it is your responsibility to reach out to your mentor for any questions you may have. You can ask them for resources, help with marking your personal statements, or guidance for interview preparation. Allow your mentor time to respond, and ensure you keep communications via email only.</p>" +
                           "<p>We hope this scheme is of benefit to you, and wish you the best in your applications!!</p>" +
                           "<p><strong>Reminder:</strong> Do not forget to join us for our opening webinar on Sunday, 4th October 2026<br>" +
                           "Link: <a href=\"" + webinarLink + "\">STEM Muslims x Daniiaal Anawar: Personal Statement Webinar</a></p>" +
                           "<p>Jazakallah khayr,<br><br>The STEM Muslims Outreach Team</p>";
                           
      try {
        MailApp.sendEmail({
          to: curMentee.email,
          subject: menteeSubject,
          body: menteeHtmlBody.replace(/<[^>]*>/g, ""), // Plain text fallback
          htmlBody: menteeHtmlBody
        });
        menteeEmailCount++;
      } catch (e) {
        Logger.log("Failed to email mentee " + curMentee.email + ": " + e.toString());
      }
    }
  }
  
  SpreadsheetApp.getUi().alert("Finished! Successfully sent " + mentorEmailCount + " mentor emails and " + menteeEmailCount + " mentee emails.");
}