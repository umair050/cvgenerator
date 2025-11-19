# CV Converter - AI-Powered Resume Formatting Tool

An online tool that converts existing CVs into specific formats using OpenAI's LLM models. Upload your CV, select a target format, and get a professionally reformatted resume.

## 🚀 Features

- **Multiple Format Support**: Convert to Datamatics Professional, Modern, Traditional, Academic, ATS-Friendly, or Creative formats
- **AI-Powered Conversion**: Uses GPT-4 to intelligently reformat your CV while preserving all key information
- **File Format Support**: Accepts PDF and DOCX files
- **Custom Instructions**: Add specific requirements for your CV conversion
- **Modern UI**: Clean, responsive interface built with React and Tailwind CSS

## 🏗️ Architecture

### Backend (Python + FastAPI)
- **FastAPI**: High-performance async web framework
- **OpenAI API**: GPT-4 for intelligent CV conversion
- **PDF/DOCX Parsing**: pdfplumber and python-docx for extracting CV content
- **File Generation**: Creates formatted DOCX output files

### Frontend (React + Vite)
- **React**: Modern UI framework
- **Tailwind CSS**: Utility-first CSS framework
- **React Dropzone**: Drag-and-drop file upload
- **Axios**: HTTP client for API communication

## 📋 Prerequisites

- Python 3.8+
- Node.js 16+
- OpenAI API Key

## 🔧 Installation

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python -m venv venv
```

3. Activate the virtual environment:
- Windows: `venv\Scripts\activate`
- Linux/Mac: `source venv/bin/activate`

4. Install dependencies:
```bash
pip install -r requirements.txt
```

5. Create a `.env` file:
```bash
cp .env.example .env
```

6. Add your OpenAI API key to `.env`:
```
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-4-turbo-preview
```

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

## 🚀 Running the Application

### Start Backend Server

```bash
cd backend
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

### Start Frontend Development Server

```bash
cd frontend
npm run dev
```

The frontend will be available at `http://localhost:3000`

## 📖 API Endpoints

### `GET /`
Health check endpoint

### `GET /api/formats`
Get available CV format options

### `POST /api/convert`
Convert CV to target format

**Parameters:**
- `file`: CV file (PDF or DOCX)
- `format_type`: Target format (datamatics, modern, traditional, academic, ats-friendly, creative)
- `additional_instructions` (optional): Custom formatting instructions

**Response:** DOCX file download

## 🎨 Available Formats

1. **Datamatics Professional**: Two-column professional format with technical/functional skills on left, summary and certifications on right, plus detailed projects experience
2. **Modern**: Clean, contemporary design with emphasis on achievements
3. **Traditional**: Classic format for conservative industries
4. **Academic**: Optimized for academic and research positions
5. **ATS-Friendly**: Format optimized for Applicant Tracking Systems
6. **Creative**: Bold design for creative industries

## 🔒 Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key (required)
- `OPENAI_MODEL`: Model to use (default: gpt-4-turbo-preview)

## 📁 Project Structure

```
CVConvertor/
├── backend/
│   ├── main.py                 # FastAPI application
│   ├── services/
│   │   ├── cv_parser.py        # CV parsing logic
│   │   ├── llm_service.py      # OpenAI integration
│   │   └── cv_generator.py     # DOCX generation
│   ├── uploads/                # Temporary upload storage
│   ├── outputs/                # Generated CV files
│   ├── requirements.txt        # Python dependencies
│   └── .env.example            # Environment variables template
├── frontend/
│   ├── src/
│   │   ├── App.jsx             # Main React component
│   │   ├── main.jsx            # React entry point
│   │   └── index.css           # Global styles
│   ├── package.json            # Node dependencies
│   └── vite.config.js          # Vite configuration
└── README.md                   # This file
```

## 🛠️ Technology Stack

### Backend
- FastAPI
- OpenAI API
- pdfplumber
- python-docx
- Uvicorn

### Frontend
- React 18
- Vite
- Tailwind CSS
- Axios
- React Dropzone

## 📝 Usage

1. Open the application in your browser
2. Upload your CV (PDF or DOCX)
3. Select your desired format
4. Optionally add custom instructions
5. Click "Convert CV"
6. Download your formatted CV

## 🔐 Security Notes

- Never commit your `.env` file with API keys
- Consider adding authentication for production use
- Implement rate limiting for API endpoints
- Add file size limits for uploads

## 🚧 Future Enhancements

- Support for more input/output formats
- Multiple template options per format
- CV preview before download
- Batch conversion
- User accounts and CV history
- Integration with job boards

## 📄 License

MIT License

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

