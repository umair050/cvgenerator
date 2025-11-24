import React, { useState } from "react";

// Job Editor Component
const JobEditor = ({ job, onSave, onCancel }) => {
  const [title, setTitle] = useState(job.title);
  const [responsibilities, setResponsibilities] = useState(
    job.responsibilities
      .map((r) => (r.type === "category" ? r.text : "- " + r.text))
      .join("\n")
  );
  const [technologies, setTechnologies] = useState(job.technologies || "");

  const handleSave = () => {
    // Parse responsibilities back
    const respLines = responsibilities.split("\n").filter((l) => l.trim());
    const parsedResp = respLines.map((line) => {
      const trimmed = line.trim();
      if (
        trimmed.endsWith(":") &&
        !trimmed.startsWith("-") &&
        !trimmed.startsWith("•")
      ) {
        return { type: "category", text: trimmed };
      }
      return { type: "bullet", text: trimmed.replace(/^[-•]\s*/, "") };
    });

    onSave({
      title: title,
      responsibilities: parsedResp,
      technologies: technologies,
    });
  };

  return (
    <div className="bg-gradient-to-br from-blue-50 to-indigo-50 p-4 rounded-lg border-2 border-blue-300 shadow-lg">
      {/* Job Title */}
      <div className="mb-4">
        <label className="block text-sm font-bold text-gray-900 mb-2">
          Job Title (Format: POSITION | MM/YYYY - MM/YYYY | LOCATION)
        </label>
        <input
          type="text"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          className="w-full px-3 py-2 border-2 border-blue-300 rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition-all text-sm"
          placeholder="SENIOR CONSULTANT | 12/2023 - PRESENT | MALAYSIA"
        />
      </div>

      {/* Responsibilities */}
      <div className="mb-4">
        <label className="block text-sm font-bold text-gray-900 mb-2">
          Responsibilities (One per line. Category headers end with ":")
        </label>
        <textarea
          value={responsibilities}
          onChange={(e) => setResponsibilities(e.target.value)}
          className="w-full px-3 py-2 border-2 border-blue-300 rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition-all text-sm font-mono"
          style={{ minHeight: "200px", lineHeight: "1.5" }}
          placeholder={`Project Management:\n- Managed multiple projects\n- Delivered on time\n\nTechnical Implementation:\n- Designed solutions\n- Implemented systems`}
        />
        <p className="text-xs text-gray-600 mt-1">
          💡 Tip: Lines ending with ":" become bold headers. Lines starting with
          "-" become bullets.
        </p>
      </div>

      {/* Technologies */}
      <div className="mb-4">
        <label className="block text-sm font-bold text-gray-900 mb-2">
          Technologies (comma-separated)
        </label>
        <input
          type="text"
          value={technologies}
          onChange={(e) => setTechnologies(e.target.value)}
          className="w-full px-3 py-2 border-2 border-blue-300 rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition-all text-sm"
          placeholder="SAP PP, SAP QM, Microsoft Azure, AWS"
        />
      </div>

      {/* Action Buttons */}
      <div className="flex justify-end gap-3">
        <button
          onClick={onCancel}
          className="px-4 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600 transition-colors text-sm font-medium"
        >
          Cancel
        </button>
        <button
          onClick={handleSave}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium"
        >
          Save Changes
        </button>
      </div>
    </div>
  );
};

const CVDisplay = ({ sections, onUpdate }) => {
  const [editingSection, setEditingSection] = useState(null);
  const [editingJobIndex, setEditingJobIndex] = useState(null);

  const handleEdit = (sectionId, currentValue) => {
    setEditingSection(sectionId);
  };

  const handleBlur = (sectionId, newValue) => {
    if (onUpdate) {
      onUpdate(sectionId, newValue);
    }
    setEditingSection(null);
  };

  const handleEditJob = (jobIndex) => {
    setEditingJobIndex(jobIndex);
  };

  const handleSaveJob = (jobIndex, updatedJob) => {
    const jobs = parseWorkExperience(sections.projects_experience);
    jobs[jobIndex] = updatedJob;

    // Convert back to text format
    const newText = jobs
      .map((job) => {
        let text = job.title + "\n\n";
        job.responsibilities.forEach((resp) => {
          if (resp.type === "category") {
            text += resp.text + "\n";
          } else {
            text += "- " + resp.text + "\n";
          }
        });
        if (job.technologies) {
          text += "Technologies: " + job.technologies + "\n";
        }
        return text;
      })
      .join("\n\n");

    if (onUpdate) {
      onUpdate("projects_experience", newText);
    }
    setEditingJobIndex(null);
  };

  const handleDeleteJob = (jobIndex) => {
    const jobs = parseWorkExperience(sections.projects_experience);
    jobs.splice(jobIndex, 1);

    // Convert back to text format
    const newText = jobs
      .map((job) => {
        let text = job.title + "\n\n";
        job.responsibilities.forEach((resp) => {
          if (resp.type === "category") {
            text += resp.text + "\n";
          } else {
            text += "- " + resp.text + "\n";
          }
        });
        if (job.technologies) {
          text += "Technologies: " + job.technologies + "\n";
        }
        return text;
      })
      .join("\n\n");

    if (onUpdate) {
      onUpdate("projects_experience", newText);
    }
  };

  const handleAddJob = () => {
    const newJob = `NEW POSITION | MM/YYYY - MM/YYYY | LOCATION

- Add your responsibilities here

Technologies: Add technologies here`;

    const currentText = sections.projects_experience || "";
    const newText = currentText.trim() ? currentText + "\n\n" + newJob : newJob;

    if (onUpdate) {
      onUpdate("projects_experience", newText);
    }
  };

  // Parse work experience into structured format
  const parseWorkExperience = (text) => {
    if (!text) return [];
    const jobs = [];
    const lines = text.split("\n");
    let currentJob = null;

    lines.forEach((line) => {
      line = line.trim();
      if (!line) return;

      // Check if it's a job header (contains | for dates/location)
      if (
        line.includes("|") &&
        !line.startsWith("-") &&
        !line.startsWith("•")
      ) {
        if (currentJob) jobs.push(currentJob);
        currentJob = {
          title: line,
          responsibilities: [],
          technologies: "",
        };
      } else if (line.toLowerCase().startsWith("technologies:")) {
        if (currentJob) {
          currentJob.technologies = line.replace(/technologies:\s*/i, "");
        }
      } else if (line.startsWith("-") || line.startsWith("•")) {
        if (currentJob) {
          currentJob.responsibilities.push({
            type: "bullet",
            text: line.replace(/^[-•]\s*/, ""),
          });
        }
      } else if (line.endsWith(":") && currentJob && line.length < 100) {
        // Category header
        currentJob.responsibilities.push({ type: "category", text: line });
      } else if (currentJob && line.length > 10) {
        // Regular responsibility without bullet
        currentJob.responsibilities.push({ type: "bullet", text: line });
      }
    });

    if (currentJob) jobs.push(currentJob);
    return jobs;
  };

  // Parse bullet list items (for skills, industry, etc.)
  const parseListItems = (text) => {
    if (!text) return [];
    return text
      .split("\n")
      .map((line) => line.trim())
      .filter((line) => line && line.length > 1)
      .map((line) => line.replace(/^[-•▪]\s*/, ""));
  };

  // Parse technical skills with categories
  const parseTechnicalSkills = (text) => {
    if (!text) return [];
    const lines = text.split("\n").filter((line) => line.trim());
    return lines.map((line) => {
      const match = line.match(/^(.+?):\s*(.+)$/);
      if (match) {
        return { category: match[1].trim(), skills: match[2].trim() };
      }
      return { category: "", skills: line.trim() };
    });
  };

  return (
    <div
      className="cv-display bg-white shadow-2xl rounded-lg overflow-hidden"
      style={{ maxWidth: "900px", margin: "0 auto" }}
    >
      {/* Header */}
      <div className="cv-header bg-white border-b-2 border-gray-200 px-8 py-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <span
              className="text-2xl font-bold text-black cursor-text hover:bg-blue-50 px-2 py-1 rounded transition-colors"
              contentEditable
              suppressContentEditableWarning
              onBlur={(e) => handleBlur("name", e.currentTarget.textContent)}
              onClick={(e) => handleEdit("name", e.currentTarget.textContent)}
            >
              {sections.name || "Candidate Name"}
            </span>
            <span className="text-gray-400">|</span>
            <span
              className="text-2xl font-bold text-blue-600 cursor-text hover:bg-blue-50 px-2 py-1 rounded transition-colors"
              contentEditable
              suppressContentEditableWarning
              onBlur={(e) =>
                handleBlur("designation", e.currentTarget.textContent)
              }
              onClick={(e) =>
                handleEdit("designation", e.currentTarget.textContent)
              }
            >
              {sections.designation || "Position"}
            </span>
          </div>
          <img
            src="/logo.png"
            alt="Datamatics Technologies Logo"
            className="h-10"
            onError={(e) => {
              e.target.style.display = "none";
            }}
          />
        </div>
      </div>

      {/* Main Content */}
      <div className="cv-body px-8 py-6">
        {/* Two Column Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Left Column */}
          <div className="cv-left-column space-y-6">
            {/* Functional Skills */}
            {sections.functional_skills && (
              <div className="cv-section">
                <h3 className="cv-section-header text-base font-bold text-gray-900 mb-3">
                  Functional Skills
                </h3>
                {editingSection === "functional_skills" ? (
                  // Edit Mode
                  <div
                    className="text-sm text-gray-700 whitespace-pre-line cursor-text bg-blue-50 px-2 py-1 rounded transition-colors"
                    contentEditable
                    suppressContentEditableWarning
                    onBlur={(e) =>
                      handleBlur(
                        "functional_skills",
                        e.currentTarget.textContent
                      )
                    }
                    autoFocus
                  >
                    {sections.functional_skills}
                  </div>
                ) : (
                  // Display Mode with bullets
                  <div
                    className="cursor-text hover:bg-blue-50 px-2 py-1 rounded transition-colors"
                    onClick={() =>
                      handleEdit(
                        "functional_skills",
                        sections.functional_skills
                      )
                    }
                  >
                    {parseListItems(sections.functional_skills).map(
                      (skill, idx) => (
                        <div
                          key={idx}
                          className="flex items-start text-sm text-gray-700 mb-1"
                        >
                          <span className="mr-2 flex-shrink-0">•</span>
                          <span className="flex-1">{skill}</span>
                        </div>
                      )
                    )}
                  </div>
                )}
              </div>
            )}

            {/* Industry Experience */}
            {sections.industry_experience && (
              <div className="cv-section">
                <h3 className="cv-section-header text-base font-bold text-gray-900 mb-3">
                  Industry Experience
                </h3>
                {editingSection === "industry_experience" ? (
                  // Edit Mode
                  <div
                    className="text-sm text-gray-700 whitespace-pre-line cursor-text bg-blue-50 px-2 py-1 rounded transition-colors"
                    contentEditable
                    suppressContentEditableWarning
                    onBlur={(e) =>
                      handleBlur(
                        "industry_experience",
                        e.currentTarget.textContent
                      )
                    }
                    autoFocus
                  >
                    {sections.industry_experience}
                  </div>
                ) : (
                  // Display Mode with bullets
                  <div
                    className="cursor-text hover:bg-blue-50 px-2 py-1 rounded transition-colors"
                    onClick={() =>
                      handleEdit(
                        "industry_experience",
                        sections.industry_experience
                      )
                    }
                  >
                    {parseListItems(sections.industry_experience).map(
                      (industry, idx) => (
                        <div
                          key={idx}
                          className="flex items-start text-sm text-gray-700 mb-1"
                        >
                          <span className="mr-2 flex-shrink-0">•</span>
                          <span className="flex-1">{industry}</span>
                        </div>
                      )
                    )}
                  </div>
                )}
              </div>
            )}

            {/* Technical Skills */}
            {sections.technical_skills && (
              <div className="cv-section">
                <h3 className="cv-section-header text-base font-bold text-gray-900 mb-3">
                  Technical Skills
                </h3>
                {editingSection === "technical_skills" ? (
                  // Edit Mode
                  <div
                    className="text-sm text-gray-700 whitespace-pre-line cursor-text bg-blue-50 px-2 py-1 rounded transition-colors"
                    contentEditable
                    suppressContentEditableWarning
                    onBlur={(e) =>
                      handleBlur(
                        "technical_skills",
                        e.currentTarget.textContent
                      )
                    }
                    autoFocus
                  >
                    {sections.technical_skills}
                  </div>
                ) : (
                  // Display Mode with formatting
                  <div
                    className="cursor-text hover:bg-blue-50 px-2 py-1 rounded transition-colors"
                    onClick={() =>
                      handleEdit("technical_skills", sections.technical_skills)
                    }
                  >
                    {parseTechnicalSkills(sections.technical_skills).map(
                      (item, idx) => (
                        <div
                          key={idx}
                          className="flex items-start text-sm text-gray-700 mb-2"
                        >
                          <span className="mr-2 flex-shrink-0">•</span>
                          <span className="flex-1">
                            {item.category && (
                              <>
                                <strong className="font-semibold">
                                  {item.category}:
                                </strong>{" "}
                              </>
                            )}
                            {item.skills}
                          </span>
                        </div>
                      )
                    )}
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Right Column */}
          <div className="cv-right-column space-y-6">
            {/* Summary */}
            {sections.summary && (
              <div className="cv-section">
                <h3 className="cv-section-header text-base font-bold text-gray-900 mb-3">
                  Summary
                </h3>
                <div
                  className="text-sm text-gray-700 text-justify leading-relaxed whitespace-pre-line cursor-text hover:bg-blue-50 px-2 py-1 rounded transition-colors"
                  contentEditable
                  suppressContentEditableWarning
                  onBlur={(e) =>
                    handleBlur("summary", e.currentTarget.textContent)
                  }
                  onClick={(e) =>
                    handleEdit("summary", e.currentTarget.textContent)
                  }
                >
                  {sections.summary}
                </div>
              </div>
            )}

            {/* Education/Qualifications/Certifications */}
            {(sections.certifications || sections.education) && (
              <div className="cv-section">
                {sections.certifications && (
                  <>
                    <h3 className="cv-section-header text-base font-bold text-gray-900 mb-3">
                      Certifications
                    </h3>
                    {editingSection === "certifications" ? (
                      // Edit Mode
                      <div
                        className="text-sm text-gray-700 whitespace-pre-line cursor-text bg-blue-50 px-2 py-1 rounded transition-colors mb-4"
                        contentEditable
                        suppressContentEditableWarning
                        onBlur={(e) =>
                          handleBlur(
                            "certifications",
                            e.currentTarget.textContent
                          )
                        }
                        autoFocus
                      >
                        {sections.certifications}
                      </div>
                    ) : (
                      // Display Mode with bullets
                      <div
                        className="cursor-text hover:bg-blue-50 px-2 py-1 rounded transition-colors mb-4"
                        onClick={() =>
                          handleEdit("certifications", sections.certifications)
                        }
                      >
                        {parseListItems(sections.certifications).map(
                          (cert, idx) => (
                            <div
                              key={idx}
                              className="flex items-start text-sm text-gray-700 mb-1"
                            >
                              <span className="mr-2 flex-shrink-0">•</span>
                              <span className="flex-1">{cert}</span>
                            </div>
                          )
                        )}
                      </div>
                    )}
                  </>
                )}

                {sections.education && (
                  <>
                    <h3 className="cv-section-header text-base font-bold text-gray-900 mb-3 mt-4">
                      Education
                    </h3>
                    {editingSection === "education" ? (
                      // Edit Mode
                      <div
                        className="text-sm text-gray-700 whitespace-pre-line cursor-text bg-blue-50 px-2 py-1 rounded transition-colors"
                        contentEditable
                        suppressContentEditableWarning
                        onBlur={(e) =>
                          handleBlur("education", e.currentTarget.textContent)
                        }
                        autoFocus
                      >
                        {sections.education}
                      </div>
                    ) : (
                      // Display Mode with bullets (education in bold)
                      <div
                        className="cursor-text hover:bg-blue-50 px-2 py-1 rounded transition-colors"
                        onClick={() =>
                          handleEdit("education", sections.education)
                        }
                      >
                        {parseListItems(sections.education).map((edu, idx) => (
                          <div
                            key={idx}
                            className="flex items-start text-sm text-gray-700 mb-1"
                          >
                            <span className="mr-2 flex-shrink-0">•</span>
                            <span className="flex-1 font-bold">{edu}</span>
                          </div>
                        ))}
                      </div>
                    )}
                  </>
                )}
              </div>
            )}
          </div>
        </div>

        {/* Work Experience - Full Width */}
        {sections.projects_experience && (
          <div className="cv-work-experience mt-8 pt-6 border-t-2 border-gray-200">
            <h3 className="cv-section-header text-base font-bold text-red-600 mb-4">
              Work Experience
            </h3>

            {editingSection === "projects_experience" ? (
              // Edit Mode - Structured Guide
              <div className="bg-blue-50 p-4 rounded-lg border-2 border-blue-300">
                {/* Formatting Guide */}
                <div className="bg-white p-3 rounded mb-4 border border-blue-200">
                  <h4 className="text-sm font-bold text-gray-900 mb-2">
                    📝 Formatting Guide:
                  </h4>
                  <div className="text-xs text-gray-700 space-y-1">
                    <div>
                      <strong>Job Title:</strong> POSITION | MM/YYYY - MM/YYYY |
                      LOCATION (will be bold & uppercase)
                    </div>
                    <div>
                      <strong>Category Header:</strong> Type header followed by
                      colon "Category Name:" (will be bold)
                    </div>
                    <div>
                      <strong>Responsibility:</strong> Start with - or • for
                      bullet points
                    </div>
                    <div>
                      <strong>Technologies:</strong> Technologies: Tool1, Tool2,
                      Tool3
                    </div>
                    <div className="mt-2 pt-2 border-t border-gray-300">
                      <strong>Example:</strong>
                      <pre className="text-xs bg-gray-100 p-2 rounded mt-1 overflow-x-auto whitespace-pre-wrap">
                        {`SENIOR CONSULTANT | 12/2023 - PRESENT | MALAYSIA

Project Management:
- Managed multiple projects
- Delivered projects on time

Technologies: SAP PP, SAP QM`}
                      </pre>
                    </div>
                  </div>
                </div>

                {/* Editable Text Area */}
                <div>
                  <label className="block text-sm font-semibold text-gray-900 mb-2">
                    Edit Work Experience:
                  </label>
                  <textarea
                    className="w-full text-sm text-gray-700 whitespace-pre-wrap p-3 rounded border-2 border-blue-400 focus:border-blue-600 focus:ring-2 focus:ring-blue-200 transition-all font-mono"
                    style={{ minHeight: "400px", lineHeight: "1.5" }}
                    value={sections.projects_experience}
                    onChange={(e) => {
                      if (onUpdate) {
                        onUpdate("projects_experience", e.target.value);
                      }
                    }}
                    placeholder="Enter your work experience following the format guide above..."
                  />
                </div>

                {/* Action Buttons */}
                <div className="flex justify-end gap-3 mt-4">
                  <button
                    onClick={() => setEditingSection(null)}
                    className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors text-sm font-medium"
                  >
                    Done Editing
                  </button>
                </div>
              </div>
            ) : (
              // Display Mode - Individual Job Editing
              <div>
                {parseWorkExperience(sections.projects_experience).map(
                  (job, idx) => (
                    <div
                      key={idx}
                      className="cv-job mb-6 last:mb-0 relative group"
                    >
                      {editingJobIndex === idx ? (
                        // Edit Individual Job
                        <JobEditor
                          job={job}
                          onSave={(updatedJob) =>
                            handleSaveJob(idx, updatedJob)
                          }
                          onCancel={() => setEditingJobIndex(null)}
                        />
                      ) : (
                        // Display Job
                        <div className="relative">
                          {/* Edit/Delete Buttons */}
                          <div className="absolute -right-2 -top-2 opacity-0 group-hover:opacity-100 transition-opacity flex gap-2 z-10">
                            <button
                              onClick={() => handleEditJob(idx)}
                              className="bg-blue-600 text-white px-3 py-1 rounded-md text-xs font-medium hover:bg-blue-700 transition-colors shadow-lg"
                            >
                              ✏️ Edit
                            </button>
                            <button
                              onClick={() => {
                                if (window.confirm("Delete this job entry?")) {
                                  handleDeleteJob(idx);
                                }
                              }}
                              className="bg-red-600 text-white px-3 py-1 rounded-md text-xs font-medium hover:bg-red-700 transition-colors shadow-lg"
                            >
                              🗑️ Delete
                            </button>
                          </div>

                          {/* Job Content */}
                          <div className="hover:bg-blue-50 p-2 rounded transition-colors">
                            {/* Job Title - Bold, Uppercase */}
                            <h4 className="text-sm font-bold text-gray-900 mb-3 uppercase">
                              {job.title}
                            </h4>

                            {/* Responsibilities */}
                            <div className="space-y-2">
                              {job.responsibilities.map((resp, respIdx) => {
                                if (resp.type === "category") {
                                  return (
                                    <div
                                      key={respIdx}
                                      className="text-sm font-bold text-gray-900 mt-3 mb-1"
                                    >
                                      {resp.text}
                                    </div>
                                  );
                                }
                                return (
                                  <div
                                    key={respIdx}
                                    className="flex items-start text-sm text-gray-700"
                                  >
                                    <span className="mr-2 mt-0.5 flex-shrink-0">
                                      •
                                    </span>
                                    <span className="flex-1 text-justify leading-snug">
                                      {resp.text}
                                    </span>
                                  </div>
                                );
                              })}
                            </div>

                            {/* Technologies */}
                            {job.technologies && (
                              <p className="text-sm text-gray-700 mt-3 text-justify">
                                <span className="font-normal">
                                  Technologies:{" "}
                                </span>
                                {job.technologies}
                              </p>
                            )}
                          </div>
                        </div>
                      )}
                    </div>
                  )
                )}

                {/* Add New Job Button */}
                <button
                  onClick={handleAddJob}
                  className="w-full mt-4 py-3 border-2 border-dashed border-gray-300 rounded-lg text-gray-600 hover:border-blue-500 hover:text-blue-600 hover:bg-blue-50 transition-colors flex items-center justify-center gap-2 font-medium"
                >
                  <span className="text-xl">+</span>
                  Add New Job Experience
                </button>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default CVDisplay;
