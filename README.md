# DeepFake Video Detector - Frontend

A modern, interactive React + Vite web interface for DeepFake video classification, featuring beautiful animations, responsive design, and seamless integration with a FastAPI backend.

## 🎨 Features

- **Modern UI/UX**: Beautiful gradients, soft shadows, and premium design
- **Interactive Upload**: Drag-and-drop file upload with visual feedback
- **Animated Results**: Dynamic result cards with confetti animations and progress indicators
- **Real-time Feedback**: Loading states, error handling, and smooth transitions
- **History Tracking**: View recent predictions with confidence scores
- **100% Responsive**: Works perfectly on desktop, tablet, and mobile devices
- **Micro-animations**: Smooth, professional animations throughout

## 📦 Installation

### Prerequisites

- Node.js (v16 or higher)
- npm or yarn
- FastAPI backend running on `http://127.0.0.1:8000`

### Step 1: Install Dependencies

```bash
npm install
```

### Step 2: Start Development Server

```bash
npm run dev
```

The application will be available at `http://localhost:3000`

### Step 3: Build for Production

```bash
npm run build
```

The production build will be in the `dist/` directory.

### Step 4: Preview Production Build

```bash
npm run preview
```

## 🔌 Backend Connection

### FastAPI Backend Setup

1. **Activate your virtual environment:**
   ```bash
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

2. **Run the FastAPI server:**
   
   **Important:** Use `python -m uvicorn` instead of just `uvicorn` to ensure the correct Python environment is used:
   
   ```bash
   python -m uvicorn scripts.app:app --reload --host 127.0.0.1 --port 8000
   ```
   
   Or use the provided scripts:
   - Windows: `run_server.bat`
   - Linux/Mac: `bash run_server.sh` or `chmod +x run_server.sh && ./run_server.sh`

3. **Verify the backend is running:**
   - The server should start on `http://127.0.0.1:8000`
   - You should see: `🚀 Running on Device: cpu` or `cuda` in the console
   - Visit `http://127.0.0.1:8000` to see the API welcome message

4. **Backend API Requirements:**
   - Endpoint: `POST /predict_video/`
   - Accepts FormData with a `file` field
   - Response format:
     ```json
     {
       "label": "Real" or "Fake",
       "confidence": 0.0-1.0,
       "filename": "video.mp4"
     }
     ```

### CORS Configuration

The FastAPI backend should have CORS enabled. If not, add this to your `app.py`:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or specify ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Changing Backend URL

If your backend runs on a different URL, update the API endpoint in `src/App.jsx`:

```javascript
const response = await fetch('YOUR_BACKEND_URL/predict_video/', {
  method: 'POST',
  body: formData,
})
```

Or configure it via environment variables (recommended for production).

## 📁 Project Structure

```
src/
├── App.jsx              # Main application component
├── App.css              # Main application styles
├── main.jsx             # React entry point
├── index.css            # Global styles
└── components/
    ├── UploadBox.jsx    # Drag-and-drop upload component
    ├── UploadBox.css    # Upload component styles
    ├── ResultCard.jsx   # Result display component
    └── ResultCard.css   # Result component styles
```

## 🎯 Usage

1. **Upload Video**: Drag and drop a video file or click to browse
2. **Wait for Analysis**: The app will show a loading animation while processing
3. **View Results**: See the prediction (Real/Fake) with confidence score
4. **Try Again**: Upload another video to test

## 🛠️ Technologies Used

- **React 18**: UI library
- **Vite**: Build tool and dev server
- **CSS3**: Modern styling with animations
- **Fetch API**: HTTP requests to backend

## 📦 Note on 21st.dev Components

This project includes custom implementations of drag-and-drop, card, and animation components that follow modern design principles. The `@21st.dev/ui` and `@21st.dev/motion` packages are listed in `package.json`, but if they're not available on npm, the app will work perfectly with the custom component implementations provided.

The custom components include:
- **UploadBox**: Full drag-and-drop functionality with visual feedback
- **ResultCard**: Animated result display with progress indicators
- **Animations**: Custom CSS animations and transitions

If you prefer to use actual 21st.dev packages (if available), you can modify the components to import from those packages instead.

## 🎨 Design Philosophy

This interface follows modern design principles:

- **Soft UI**: Glassmorphism effects with backdrop blur
- **Gradient Backgrounds**: Beautiful color transitions
- **Micro-animations**: Smooth, purposeful animations
- **Responsive Design**: Mobile-first approach
- **Accessibility**: Clear visual feedback and error messages

## 🚀 Deployment

### Vercel

1. Push your code to GitHub
2. Import project in Vercel
3. Set build command: `npm run build`
4. Set output directory: `dist`
5. Deploy!

### Netlify

1. Push your code to GitHub
2. Create new site from Git in Netlify
3. Build command: `npm run build`
4. Publish directory: `dist`
5. Deploy!

### Environment Variables

For production, set the backend URL as an environment variable:

```env
VITE_API_URL=https://your-backend-url.com
```

Then update `App.jsx` to use it:

```javascript
const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'
```

## 🐛 Troubleshooting

### Backend Connection Issues

- **ModuleNotFoundError for torch or other packages:**
  - Make sure you're using `python -m uvicorn` instead of just `uvicorn`
  - Ensure your virtual environment is activated
  - Verify packages are installed in the correct venv: `pip list` should show torch
  - If using conda, ensure the venv Python is being used, not the base conda Python

- **Server not starting:**
  - Check that port 8000 is not already in use
  - Verify all dependencies are installed: `pip install -r requirements.txt`
  - Check that the model file exists at `models/best_xception_optuna.pth`

- **CORS errors:**
  - Ensure CORS middleware is enabled in `scripts/app.py`
  - Check browser console for specific CORS error messages

- **API endpoint not found:**
  - Verify the backend is running on `http://127.0.0.1:8000`
  - Test the endpoint directly: `curl http://127.0.0.1:8000/`
  - Check browser network tab for failed requests

### Build Issues

- Clear `node_modules` and reinstall: `rm -rf node_modules && npm install`
- Update Node.js to latest LTS version
- Check for conflicting dependencies

### Styling Issues

- Clear browser cache
- Ensure all CSS files are imported correctly
- Check for CSS conflicts in browser DevTools

## 📝 License

This project is part of a DeepFake detection system. Use responsibly.

## 🤝 Contributing

Feel free to submit issues and enhancement requests!

---

**Built with ❤️ using FastAPI + React + Vite**

