function onFormSubmit(e) {
  var response = e.namedValues;
  
  // Update these strings to match your exact Google Form question titles
  var course = response["Which course do you study?"][0];
  var studentName = response["Full Name"][0];
  
  // Note: Ensure your form collects email addresses (or has a question titled "Email Address")
  var studentEmail = response["Email Address"] ? response["Email Address"][0] : null; 
  var statementUrl = response["UCAS Statement (File Upload)"][0];
  
  // Get the designated volunteer email(s) dynamically from the "Volunteers" tab
  var recipientEmails = getVolunteersForCourseFromSheet(course);
  
  // 1. Notify Volunteers if available, otherwise notify Admin
  if (recipientEmails && recipientEmails.length > 0) {
    var subject = "New UCAS Statement to Review: " + course + " (" + studentName + ")";
    var body = "Hello,\n\n" +
               "A new UCAS application statement has been submitted.\n\n" +
               "Student: " + studentName + "\n" +
               "Course: " + course + "\n" +
               "View Statement: " + statementUrl + "\n\n" +
               "Please log in to review.";
               
    GmailApp.sendEmail(recipientEmails.join(","), subject, body);
  } else {
    // Fallback: Notify Admin if no volunteers are found for this course
    var adminEmail = "stemmuslims.outreach@gmail.com"; // Sends to your account
    var alertSubject = "ALERT: No volunteer available for course: " + course;
    var alertBody = "Hello Admin,\n\n" +
                    "A student (" + studentName + ") submitted a UCAS statement for '" + course + "', " +
                    "but no volunteers were found listed under that column in the 'Volunteers' tab.\n\n" +
                    "Please update the spreadsheet so they can receive future submissions.";
                    
    GmailApp.sendEmail(adminEmail, alertSubject, alertBody);
  }
  
  // 2. Send confirmation receipt to the student
  if (studentEmail) {
    var studentSubject = "UCAS Statement Submission Received";
    var studentBody = "Hi " + studentName + ",\n\n" +
                      "Thank you for submitting your UCAS statement for " + course + ".\n\n" +
                      "We have successfully received your upload and our team is currently processing your request. " +
                      "Please be patient, and we will get back to you with feedback as soon as possible.\n\n" +
                      "Best regards,\nReview Team";
                      
    GmailApp.sendEmail(studentEmail, studentSubject, studentBody);
  }
}

function getVolunteersForCourseFromSheet(course) {
  var sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName("Volunteers");
  if (!sheet) return [];
  
  var data = sheet.getDataRange().getValues();
  var headers = data[0]; // Row 1 contains the course headers
  var columnIndex = -1;
  
  // Find the column matching the course name (case-insensitive search)
  for (var i = 0; i < headers.length; i++) {
    if (headers[i].toString().trim().toLowerCase() === course.toString().trim().toLowerCase()) {
      columnIndex = i;
      break;
    }
  }
  
  var recipientEmails = [];
  if (columnIndex !== -1) {
    // Loop through rows starting from row 2 downwards to collect emails
    for (var row = 1; row < data.length; row++) {
      var email = data[row][columnIndex];
      if (email && email.toString().trim() !== "") {
        recipientEmails.push(email.toString().trim());
      }
    }
  }
  
  return recipientEmails;
}