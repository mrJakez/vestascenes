"use client";

import { useEffect, useState } from "react";
import {BoardPreview, LinearProgress} from "@vestaboard/installables";
import { formatDistanceToNow } from "date-fns";
import { de } from "date-fns/locale";
import { getRuntimeConfig } from "../utils/runtime-config"; // Pfad anpassen

export interface SceneInstance {
  id: string;
  class_string: string;
  start_date: string;
  end_date: string;
  overwritable: boolean;
  raw: string;
  priority: number;
  is_active: boolean;
}


export interface ApiResponse {
  meta: Record<string, string>; // wenn du später Metadaten brauchst
  content: SceneInstance[];
}

export function HistoryContainer() {
  const [history, setHistory] = useState<SceneInstance[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchScenes = async () => {
      try {
        const config = await getRuntimeConfig();
        const res = await fetch(`${config.apiUrl}/history`);
        const data: ApiResponse = await res.json();
        setHistory(data.content);

      } catch (error) {
        console.error("Fehler beim Laden der Szenen:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchScenes();
  }, []);

  if (loading) return <LinearProgress />;

  return (
    <div>
        {history.map((scene) => (
          <div key={scene.id}>
            <BoardPreview characters={JSON.parse(scene.raw)}>
              {scene.class_string}
              {formatDistanceToNow(new Date(scene.start_date), {
              addSuffix: true,
              locale: de,
            })}
            </BoardPreview>
          </div>
        ))}
    </div>
  );
}