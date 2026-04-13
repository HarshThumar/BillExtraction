const { GoogleSpreadsheet } = require('google-spreadsheet');
const { GoogleAuth } = require('google-auth-library');
require('dotenv').config({ path: './frontend/.env.local' });

async function setupHeaders() {
  try {
    const sheetId = process.env.GOOGLE_SHEET_ID || '17qEvzBBu9dnmEgyM4G23yKj7MeFYyeZfakqJu9fkurE';
    
    console.log(`Initialising headers for Sheet ID: ${sheetId}`);

    const auth = new GoogleAuth({
      scopes: ['https://www.googleapis.com/auth/spreadsheets'],
    });

    const doc = new GoogleSpreadsheet(sheetId, auth);
    await doc.loadInfo();
    
    const sheet = doc.sheetsByIndex[0];
    
    // Define the headers based on the extraction logic
    const headers = [
      'Buyer Name', 
      'Buyer Address', 
      'GST No', 
      'Mobile No', 
      'Bill No', 
      'Date', 
      'Total Amount', 
      'Timestamp', 
      'Status'
    ];

    await sheet.setHeaderRow(headers);
    
    console.log('✅ Headers successfully created!');
    console.log('Columns:', headers.join(' | '));
  } catch (error) {
    console.error('❌ Error setting up headers:', error.message);
    console.log('\nMake sure:');
    console.log('1. You have run: gcloud auth application-default login');
    console.log('2. The service account has "Editor" access to the Google Sheet.');
  }
}

setupHeaders();
