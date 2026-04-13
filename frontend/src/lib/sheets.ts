import { GoogleSpreadsheet } from 'google-spreadsheet';
import { GoogleAuth } from 'google-auth-library';

export async function appendToSheet(data: any) {
  try {
    const sheetId = process.env.GOOGLE_SHEET_ID;

    if (!sheetId) {
      throw new Error('Missing GOOGLE_SHEET_ID');
    }

    // Using GoogleAuth for ADC (Application Default Credentials)
    // This will use the impersonated credentials from the user's terminal environment
    const auth = new GoogleAuth({
      scopes: ['https://www.googleapis.com/auth/spreadsheets'],
    });

    const doc = new GoogleSpreadsheet(sheetId, auth);
    await doc.loadInfo();
    
    const sheet = doc.sheetsByIndex[0]; // Assumes first sheet
    await sheet.addRow(data);
    
    return { success: true };
  } catch (error: any) {
    console.error('Sheet append error:', error);
    throw error;
  }
}
