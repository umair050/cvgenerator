import { useState } from "react";
import axios from "axios";
import { useDropzone } from "react-dropzone";
import "./App.css";

const API_BASE_URL = "http://localhost:8000";

const SECTIONS = [
  {
    id: "technical_skills",
    label: "Technical Skills",
    icon: "⚙️",
    placeholder:
      "Format: Category Name: skill1, skill2, skill3\nExample:\nERP Systems: SAP S/4HANA, SAP ECC 6.0\nCloud & Infrastructure: Microsoft Azure, AWS, Terraform",
  },
  {
    id: "summary",
    label: "Summary",
    icon: "📝",
    placeholder: "Write your professional summary...",
  },
  {
    id: "industry_experience",
    label: "Industry Experience",
    icon: "🏢",
    placeholder: "List industries you have worked in...",
  },
  {
    id: "functional_skills",
    label: "Functional Skills",
    icon: "💼",
    placeholder: "List your soft skills, management skills...",
  },
  {
    id: "certifications",
    label: "Certification & Trainings",
    icon: "🎓",
    placeholder: "List your certifications and training...",
  },
  {
    id: "education",
    label: "Education",
    icon: "📚",
    placeholder: "List your educational qualifications...",
  },
  {
    id: "projects_experience",
    label: "Work Experience",
    icon: "💼",
    placeholder:
      "Format each position as:\nJob Title / Company Name | MM/YYYY – MM/YYYY | Location\n- Responsibility 1\n- Responsibility 2\nTechnologies: Tech1, Tech2\n\nOR\n\nJob Title, Company Name, Location | MM/YYYY – MM/YYYY\n- Responsibility 1\n- Responsibility 2",
  },
];

function App() {
  const [file, setFile] = useState(null);
  const [sections, setSections] = useState({
    name: "",
    designation: "",
    technical_skills: "",
    summary: "",
    industry_experience: "",
    functional_skills: "",
    certifications: "",
    education: "",
    projects_experience: "",
  });
  const [loading, setLoading] = useState(false);
  const [parsing, setParsing] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);

  const onDrop = async (acceptedFiles) => {
    if (acceptedFiles.length > 0) {
      setFile(acceptedFiles[0]);
      setError(null);
      setSuccess(false);
      await parseCV(acceptedFiles[0]);
    }
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      "application/pdf": [".pdf"],
      "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        [".docx"],
      "application/msword": [".doc"],
    },
    maxFiles: 1,
  });

  const parseCV = async (fileToParse) => {
    setParsing(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append("file", fileToParse);

      const response = await axios.post(
        `${API_BASE_URL}/api/parse-cv`,
        formData
      );
      setSections(response.data);
    } catch (err) {
      setError(
        err.response?.data?.detail || "Failed to parse CV. Please try again."
      );
      console.error("Parse error:", err);
    } finally {
      setParsing(false);
    }
  };

  const handleGenerateCV = async () => {
    setLoading(true);
    setError(null);
    setSuccess(false);

    try {
      const response = await axios.post(
        `${API_BASE_URL}/api/generate-cv`,
        sections,
        {
          params: { format_type: "datamatics" },
          responseType: "blob",
        }
      );

      // Create download link
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", "cv_datamatics.docx");
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);

      setSuccess(true);
    } catch (err) {
      setError(
        err.response?.data?.detail || "Failed to generate CV. Please try again."
      );
      console.error("Generate error:", err);
    } finally {
      setLoading(false);
    }
  };

  const updateSection = (sectionId, value) => {
    setSections({
      ...sections,
      [sectionId]: value,
    });
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50">
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-6xl mx-auto">
          {/* Header */}
          <div className="text-center mb-8">
            <h1 className="text-5xl font-bold text-gray-900 mb-3">
              CV Converter
            </h1>
            <p className="text-xl text-gray-600">
              Upload your CV, edit sections, and generate a professional resume
            </p>
          </div>

          {/* File Upload Section */}
          {!sections.technical_skills && !parsing && (
            <div className="bg-white rounded-2xl shadow-xl p-8 mb-6">
              <label className="block text-lg font-semibold text-gray-700 mb-4">
                Upload Your CV
              </label>
              <div
                {...getRootProps()}
                className={`border-2 border-dashed rounded-xl p-12 text-center cursor-pointer transition-all ${
                  isDragActive
                    ? "border-blue-500 bg-blue-50 scale-105"
                    : "border-gray-300 hover:border-blue-400 hover:bg-gray-50"
                }`}
              >
                <input {...getInputProps()} />
                <div className="space-y-4">
                  <svg
                    className="mx-auto h-16 w-16 text-gray-400"
                    stroke="currentColor"
                    fill="none"
                    viewBox="0 0 48 48"
                  >
                    <path
                      d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02"
                      strokeWidth={2}
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    />
                  </svg>
                  {file ? (
                    <>
                      <p className="text-lg font-medium text-gray-900">
                        {file.name}
                      </p>
                      <p className="text-sm text-gray-500">
                        Click or drag to replace
                      </p>
                    </>
                  ) : (
                    <>
                      <p className="text-lg text-gray-700">
                        {isDragActive
                          ? "Drop the file here"
                          : "Drag & drop your CV here, or click to select"}
                      </p>
                      <p className="text-sm text-gray-500">
                        Supports PDF and DOCX files
                      </p>
                    </>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* Parsing Indicator */}
          {parsing && (
            <div className="bg-white rounded-2xl shadow-xl p-8 mb-6 text-center">
              <div className="inline-block animate-spin rounded-full h-12 w-12 border-4 border-blue-500 border-t-transparent mb-4"></div>
              <p className="text-lg text-gray-700">Parsing your CV...</p>
            </div>
          )}

          {/* CV Sections Form */}
          {(sections.technical_skills || sections.name) && !parsing && (
            <div className="max-w-4xl mx-auto">
              <div className="space-y-6">
                {/* Name and Designation Section */}
                <div className="bg-white rounded-2xl shadow-xl p-6 hover:shadow-2xl transition-shadow">
                  <div className="flex items-center space-x-3 mb-4">
                    <span className="text-3xl">👤</span>
                    <h2 className="text-2xl font-bold text-gray-900">
                      Header Information
                    </h2>
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Full Name
                      </label>
                      <input
                        type="text"
                        value={sections.name}
                        onChange={(e) => updateSection("name", e.target.value)}
                        placeholder="Enter your full name"
                        className="w-full px-4 py-2 border-2 border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Designation/Title
                      </label>
                      <input
                        type="text"
                        value={sections.designation}
                        onChange={(e) =>
                          updateSection("designation", e.target.value)
                        }
                        placeholder="e.g., DevOps Engineer"
                        className="w-full px-4 py-2 border-2 border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                      />
                    </div>
                  </div>
                </div>

                {SECTIONS.map((section) => (
                  <div
                    key={section.id}
                    className="bg-white rounded-2xl shadow-xl p-6 hover:shadow-2xl transition-shadow"
                  >
                    <div className="flex items-center space-x-3 mb-4">
                      <span className="text-3xl">{section.icon}</span>
                      <h2 className="text-2xl font-bold text-gray-900">
                        {section.label}
                      </h2>
                    </div>
                    {section.id === "projects_experience" ? (
                      <div
                        contentEditable
                        suppressContentEditableWarning
                        onInput={(e) =>
                          updateSection(section.id, e.currentTarget.textContent)
                        }
                        placeholder={section.placeholder}
                        className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-y min-h-[300px] transition-all whitespace-pre-wrap overflow-auto bg-white"
                        style={{
                          fontFamily: "monospace",
                          fontSize: "14px",
                          lineHeight: "1.6",
                        }}
                      >
                        {sections[section.id] || ""}
                      </div>
                    ) : (
                      <textarea
                        value={sections[section.id]}
                        onChange={(e) =>
                          updateSection(section.id, e.target.value)
                        }
                        placeholder={section.placeholder}
                        className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-y min-h-[100px] transition-all"
                        rows={section.id === "summary" ? 6 : 4}
                      />
                    )}
                  </div>
                ))}

                {/* Generate Button */}
                <div className="bg-white rounded-2xl shadow-xl p-6">
                  <button
                    onClick={handleGenerateCV}
                    disabled={loading}
                    className="w-full bg-gradient-to-r from-blue-600 to-indigo-700 text-white py-4 px-6 rounded-xl font-bold text-lg hover:from-blue-700 hover:to-indigo-800 disabled:from-gray-400 disabled:to-gray-500 disabled:cursor-not-allowed transition-all transform hover:scale-105 active:scale-95 shadow-lg flex items-center justify-center space-x-3"
                  >
                    {loading ? (
                      <>
                        <svg
                          className="animate-spin h-6 w-6"
                          xmlns="http://www.w3.org/2000/svg"
                          fill="none"
                          viewBox="0 0 24 24"
                        >
                          <circle
                            className="opacity-25"
                            cx="12"
                            cy="12"
                            r="10"
                            stroke="currentColor"
                            strokeWidth="4"
                          ></circle>
                          <path
                            className="opacity-75"
                            fill="currentColor"
                            d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                          ></path>
                        </svg>
                        <span>Generating CV...</span>
                      </>
                    ) : (
                      <>
                        <svg
                          className="h-6 w-6"
                          fill="none"
                          stroke="currentColor"
                          viewBox="0 0 24 24"
                        >
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                          />
                        </svg>
                        <span>Generate CV</span>
                      </>
                    )}
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* Error Message */}
          {error && (
            <div className="mt-6 p-4 bg-red-50 border-l-4 border-red-500 rounded-lg">
              <div className="flex items-center">
                <svg
                  className="h-5 w-5 text-red-500 mr-2"
                  fill="currentColor"
                  viewBox="0 0 20 20"
                >
                  <path
                    fillRule="evenodd"
                    d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                    clipRule="evenodd"
                  />
                </svg>
                <p className="text-sm font-medium text-red-800">{error}</p>
              </div>
            </div>
          )}

          {/* Success Message */}
          {success && (
            <div className="mt-6 p-4 bg-green-50 border-l-4 border-green-500 rounded-lg">
              <div className="flex items-center">
                <svg
                  className="h-5 w-5 text-green-500 mr-2"
                  fill="currentColor"
                  viewBox="0 0 20 20"
                >
                  <path
                    fillRule="evenodd"
                    d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                    clipRule="evenodd"
                  />
                </svg>
                <p className="text-sm font-medium text-green-800">
                  CV generated successfully! Your file should start downloading.
                </p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;
