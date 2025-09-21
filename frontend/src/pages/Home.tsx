// src/pages/Home.tsx
import React, { useEffect, useState } from "react";
import axios from "axios";
import ConnectWallet from "../components/ConnectWallet";

interface Project {
  id: number;
  app_id: number;
  asa_id: number;
  app_address: string;
  creator_address: string;
  admin_address: string;
  title: string;
  description: string;
}

export function Home() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Wallet modal state
  const [openWalletModal, setOpenWalletModal] = useState(false);

  // Form state
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    app_id: "",
    asa_id: "",
    app_address: "",
    creator_address: "",
    admin_address: "",
    title: "",
    description: "",
  });

  // API URL from environment
  const apiUrl = import.meta.env.VITE_API_URL || "http://localhost:8000";

  useEffect(() => {
    fetchProjects();
  }, []);

  const fetchProjects = async () => {
    try {
      const response = await axios.get<Project[]>(
        `${apiUrl.replace(/\/+$/, "")}/api/projects`
      );
      setProjects(response.data);
    } catch (err) {
      console.error("Failed to fetch projects:", err);
      setError("Failed to load projects.");
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
  ) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await axios.post(`${apiUrl.replace(/\/+$/, "")}/api/projects`, {
        app_id: formData.app_id ? Number(formData.app_id) : 0,
        asa_id: formData.asa_id ? Number(formData.asa_id) : 0,
        app_address: formData.app_address,
        creator_address: formData.creator_address,
        admin_address: formData.admin_address,
        title: formData.title,
        description: formData.description,
      });
      setShowForm(false);
      setFormData({
        app_id: "",
        asa_id: "",
        app_address: "",
        creator_address: "",
        admin_address: "",
        title: "",
        description: "",
      });
      fetchProjects();
    } catch (err) {
      console.error("Failed to create project:", err);
      setError("Failed to create project.");
    }
  };

  if (loading) return <p>Loading projects...</p>;
  if (error) return <p style={{ color: "red" }}>{error}</p>;

  return (
    <div>
      <h1>Hyperdrive Projects 🚀</h1>

      {/* Connect Wallet Button */}
      <button
        className="btn btn-primary"
        style={{ marginBottom: "16px" }}
        onClick={() => setOpenWalletModal(true)}
      >
        Connect Wallet
      </button>
      <ConnectWallet
        openModal={openWalletModal}
        closeModal={() => setOpenWalletModal(false)}
      />

      {/* Create Project Button */}
      <button
        onClick={() => setShowForm(!showForm)}
        style={{ marginBottom: "16px", marginLeft: "8px" }}
      >
        {showForm ? "Cancel" : "Create Project"}
      </button>

      {showForm && (
        <form onSubmit={handleSubmit} style={{ marginBottom: "24px" }}>
          <input
            type="number"
            name="app_id"
            placeholder="App ID"
            value={formData.app_id}
            onChange={handleChange}
            required
          />
          <input
            type="number"
            name="asa_id"
            placeholder="ASA ID"
            value={formData.asa_id}
            onChange={handleChange}
            required
          />
          <input
            type="text"
            name="app_address"
            placeholder="App Address"
            value={formData.app_address}
            onChange={handleChange}
            required
          />
          <input
            type="text"
            name="creator_address"
            placeholder="Creator Address"
            value={formData.creator_address}
            onChange={handleChange}
            required
          />
          <input
            type="text"
            name="admin_address"
            placeholder="Admin Address"
            value={formData.admin_address}
            onChange={handleChange}
            required
          />
          <input
            type="text"
            name="title"
            placeholder="Title"
            value={formData.title}
            onChange={handleChange}
            required
          />
          <textarea
            name="description"
            placeholder="Description"
            value={formData.description}
            onChange={handleChange}
            required
          />
          <button type="submit">Submit</button>
        </form>
      )}

      {projects.length === 0 ? (
        <p>No projects found.</p>
      ) : (
        <div style={{ display: "grid", gap: "16px" }}>
          {projects.map((project) => (
            <div
              key={project.id}
              style={{
                border: "1px solid #ddd",
                padding: "16px",
                borderRadius: "8px",
              }}
            >
              <h2>{project.title}</h2>
              <p>{project.description}</p>
              <small>
                <strong>Creator:</strong> {project.creator_address}
              </small>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
