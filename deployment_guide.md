# 🚀 Deployment Guide: Bill Genius

This guide outlines the production deployment steps for the containerized Python backend (Google Cloud Run) and the static Next.js frontend (Firebase Hosting).

## 📍 Configuration Details
- **Project ID**: `soulmate-tours`
- **Region**: `asia-south1`
- **Service Account**: `prince-deployer@soulmate-tours.iam.gserviceaccount.com`
- **GitHub Registry**: `asia-south1-docker.pkg.dev/soulmate-tours/prince-images`

---

## 1. Backend Deployment (Google Cloud Run)

The backend uses `uv` for dependency management and requires a multi-stage Docker build.

### Step 1: Build and Push Docker Image
Run from the `backend-extraction/` directory:

```powershell
# Create the Artifact Registry repository (if it doesn't exist)
gcloud artifacts repositories create prince-images `
    --repository-format=docker `
    --location=asia-south1

# Build and Push using Google Cloud Build
gcloud builds submit --tag asia-south1-docker.pkg.dev/soulmate-tours/prince-images/bill-extraction-backend:latest .
```

### Step 2: Deploy to Cloud Run
Deploy with high resources and IAM-based authentication:

```powershell
gcloud run deploy bill-extraction-backend `
    --image asia-south1-docker.pkg.dev/soulmate-tours/prince-images/bill-extraction-backend:latest `
    --platform managed `
    --region asia-south1 `
    --allow-unauthenticated `
    --memory 4Gi `
    --cpu 2 `
    --timeout 300 `
    --set-env-vars="GOOGLE_SHEET_ID=1ESpXPrhesyxgD9WELxtf0es9WU742iZXPlnXrg-YuE0,IMPERSONATED_SERVICE_ACCOUNT=prince-deployer@soulmate-tours.iam.gserviceaccount.com"
```

> [!IMPORTANT]
> **Keyless Auth**: No service account JSON key is needed inside the container. The instance uses the `prince-deployer` identity via impersonation.

---

## 2. Frontend Deployment (Firebase Hosting)

The frontend is a static Next.js site. Environment variables are "baked in" during the build.

### Step 1: Update Environment Variables
Ensure `frontend/.env.local` contains the live backend URL:

```text
NEXT_PUBLIC_BACKEND_URL=https://bill-extraction-backend-b7wi5z7maq-el.a.run.app
GOOGLE_SHEET_ID=1ESpXPrhesyxgD9WELxtf0es9WU742iZXPlnXrg-YuE0
```

### Step 2: Build and Deploy
Run from the `frontend/` directory:

```powershell
# Install dependencies
npm install

# Generate static export (creates the 'out' directory)
npm run build

# Deploy to Firebase Hosting (specified project soulmate-tours)
npx firebase-tools deploy --project soulmate-tours --only hosting
```

---

## 🧹 Maintenance & Cleanup

### Updates
- **Backend**: Repeating the "Build" and "Deploy" steps will create a new revision on Cloud Run.
- **Frontend**: Updating code requires a new `npm run build` and `firebase deploy`.

### IAM Verification
If the system cannot write to Sheets:
1. Ensure the `prince-deployer` service account has "Editor" permissions on the Google Sheet.
2. Ensure the "Default Compute Service Account" (used by Cloud Run) has the `Service Account Token Creator` role assigned to the `prince-deployer` account.

### Troubleshooting
- **Build Errors**: Check the Cloud Build logs in the GCP Console.
- **Logs**: View live backend logs: `gcloud logs read --service bill-extraction-backend --region asia-south1`
- **Firebase Sites**: If deployment fails with a "hosting target" error, use `npx firebase-tools hosting:sites:list` to check the site ID.
