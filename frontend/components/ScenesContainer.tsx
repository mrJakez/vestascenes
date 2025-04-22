"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { BoardPreview, LinearProgress, IBoard } from "@vestaboard/installables";
import { encodeBoardCharacters } from "@vestaboard/installables/lib/utils/encodeBoardCharacters";

export interface Scene {
  scene: string;
  priority: number;
  raw: IBoard
}

export interface ApiResponse {
  meta: Record<string, string>;
  content: Scene[];
}

export function ScenesContainer() {
  const [scenes, setScenes] = useState<Scene[]>([]);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    const fetchScenes = async () => {
      try {
        const res = await fetch(`${process.env.FALLBACK_BACKEND_URL}/scenes`);
        const data: ApiResponse = await res.json();

        const scenesWithRaw = await Promise.all(
          data.content.map(async (scene) => {
            try {
              const res = await fetch(`${process.env.FALLBACK_BACKEND_URL}/scene/${scene.scene}`);
              const extra = await res.json();
              console.log("RAW:", extra.raw)
              return { ...scene, raw: extra.raw };
            } catch (err) {
              console.error("Fehler beim Laden von raw für", scene.scene, err);
              return scene;
            }
          })
        );
        setScenes(scenesWithRaw);

        // setScenes(data.content);
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
        {scenes.map((scene) => (
          <div
            key={scene.scene}
            onClick={() => router.push(`/scene/?scene=${scene.scene}`)}
            style={{ cursor: "pointer" }}
          >
            {scene.raw ? (
              <BoardPreview characters={scene.raw}>
                {scene.scene}
                {scene.priority.toString()}
              </BoardPreview>
            ) : (
              <BoardPreview characters={encodeBoardCharacters('No Content available')}>
                {scene.scene}
                {scene.priority.toString()}
              </BoardPreview>
            )}
          </div>
        ))}
    </div>
  );
}