"use client";

import { useSearchParams, useRouter } from "next/navigation";
import { useEffect, useState, Suspense } from "react";
import { BoardPreview, Toast } from "@vestaboard/installables";
import { getRuntimeConfig } from "@/utils/runtime-config";

interface Snapshot {
  id: string;
  title: string;
  raw: string;
  filename: string;
}

interface SnapshotSceneDetailListProps {
  selectedFilename: string | null;
  setSelectedFilename: (filename: string | null) => void;
}

function SnapshotSceneDetailList({
  selectedFilename,
  setSelectedFilename,
}: SnapshotSceneDetailListProps) {
  const [filenames, setFilenames] = useState<string[]>([]);
  const [snapshots, setSnapshots] = useState<Snapshot[]>([]);
  const [loading, setLoading] = useState(true);
  const [toastOpen, setToastOpen] = useState(false);
  const [toastMessage, setToastMessage] = useState("");
  const [toastSeverity, setToastSeverity] = useState<"success" | "error">("success");

  useEffect(() => {
    const fetchFilenames = async () => {
      try {
        const config = await getRuntimeConfig();
        const res = await fetch(`${config.apiUrl}/snapshot-filenames`);
        const data = await res.json();
        setFilenames(data.content);
      } catch (err) {
        console.error("Fehler beim Laden der Dateinamen:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchFilenames();
  }, []);

  useEffect(() => {
    const loadSnapshots = async () => {
      if (!selectedFilename) return;
      setLoading(true);
      try {
        const config = await getRuntimeConfig();
        const res = await fetch(`${config.apiUrl}/snapshots/?filename=${selectedFilename}`);
        const data = await res.json();
        const withFilename = data.content.map((s: Snapshot) => ({
          ...s,
          filename: selectedFilename,
        }));
        setSnapshots(withFilename);
      } catch (err) {
        console.error("Fehler beim Laden der Snapshots:", err);
      } finally {
        setLoading(false);
      }
    };

    if (selectedFilename) loadSnapshots();
  }, [selectedFilename]);

  async function handleBoardClick(snap: Snapshot) {
    try {
      const config = await getRuntimeConfig();
      const res = await fetch(`${config.apiUrl}/write/?raw=${snap.raw}`);

      if (!res.ok) {
        throw new Error(`Fehler: ${res.status}`);
      }

      const data = await res.json();
      console.log("Antwort vom Server:", data);

      // Erfolgs-Toast
      setToastMessage(`Snapshot ${snap.title} erfolgreich gesendet!`);
      setToastSeverity("success");
      setToastOpen(true);
    } catch (err) {
      console.error("Fehler beim AJAX-Request:", err);
      setToastMessage(`Fehler beim Senden von ${snap.title}`);
      setToastSeverity("error");
      setToastOpen(true);
    }
  }

  if (loading) return <div>Lade...</div>;

  if (selectedFilename) {
    return (
      <div style={{ padding: "2rem" }}>
        <ul style={{ listStyle: "none", padding: 0 }}>
          {snapshots.map((snap) => (
            <li key={snap.id} style={{ marginBottom: "2rem" }}>
              <div onClick={() => handleBoardClick(snap)} style={{ cursor: "pointer" }}>
                <BoardPreview characters={JSON.parse(snap.raw)}>
                  {snap.title}
                </BoardPreview>
              </div>
            </li>
          ))}
        </ul>

        {/* Toast-Komponente */}
        <Toast
          severity={toastSeverity}
          message={toastMessage}
          open={toastOpen}
          onClose={() => setToastOpen(false)}
        />
      </div>
    );
  }

  return (
    <div style={{ padding: "2rem" }}>
      <ul style={{ listStyle: "none", padding: 0 }}>
        {filenames.map((filename) => (
          <li key={filename}>
            <button
              onClick={() => setSelectedFilename(filename)}
              style={{
                marginBottom: "0.5rem",
                fontSize: "1.2rem",
                padding: "0.5rem 1rem",
                cursor: "pointer",
              }}
            >
              📂 {filename}
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}

function PageInner() {
  const params = useSearchParams();
  const scene = params.get("scene");
  const router = useRouter();
  const [selectedFilename, setSelectedFilename] = useState<string | null>(null);

  const handleBack = () => {
    if (selectedFilename) {
      setSelectedFilename(null);
    } else {
      router.back();
    }
  };

  return (
    <div style={{ padding: "2rem" }}>
      <div
        style={{
          display: "flex",
          alignItems: "center",
          marginBottom: "1.5rem",
          gap: "1rem",
        }}
      >
        <button
          onClick={handleBack}
          style={{
            background: "#444",
            border: "none",
            borderRadius: "6px",
            padding: "0.5rem 1rem",
            color: "#fff",
            cursor: "pointer",
            fontSize: "1rem",
          }}
        >
          Back
        </button>
        <span style={{ fontSize: "1.2rem", color: "#ccc" }}>
          {selectedFilename ? selectedFilename : "File list"}
        </span>
      </div>

      {scene === "SnapshotScene" ? (
        <SnapshotSceneDetailList
          selectedFilename={selectedFilename}
          setSelectedFilename={setSelectedFilename}
        />
      ) : (
        <div style={{ fontSize: "2rem", fontWeight: "bold" }}>
          Szene: {scene}
        </div>
      )}
    </div>
  );
}

export default function ScenePageWrapper() {
  return (
    <Suspense fallback={<div>Lade Szene...</div>}>
      <PageInner />
    </Suspense>
  );
}