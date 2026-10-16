"use client";

import dynamic from "next/dynamic";
import { useState, useEffect } from "react";
import { getRuntimeConfig } from "../utils/runtime-config"; // Pfad anpassen

// Dynamisch laden
// Vestaboard components access window when their modules are loaded.
const Editor = dynamic(() => import("./BoardEditor"), { ssr: false });
const HistoryContainer = dynamic(
  () => import("./HistoryContainer").then((module) => module.HistoryContainer),
  { ssr: false },
);
const ScenesContainer = dynamic(
  () => import("./ScenesContainer").then((module) => module.ScenesContainer),
  { ssr: false },
);
const TabBarWrapper = dynamic(() => import("./TabBarWrapper"), {
  ssr: false,
});


export default function TabBarClientContainer() {
  const [tabIndex, setTabIndex] = useState(0);
  const [apiUrl, setApiUrl] = useState<string | null>(null);

  useEffect(() => {
    const loadConfig = async () => {
      try {
        const config = await getRuntimeConfig();
        setApiUrl(config.apiUrl);
      } catch (err) {
        console.error("Fehler beim Laden der Config:", err);
      }
    };

    loadConfig();
  }, []);

  return (
	<div>
	  <TabBarWrapper onChange={setTabIndex} />

	  <div style={{ marginTop: "1rem" }}>
          {tabIndex === 0 && <div>
              <HistoryContainer />
          </div>}
          {tabIndex === 1 && <div>
              <ScenesContainer />
          </div>}
          {tabIndex === 2 && <div>
              <Editor backendUrl={apiUrl ?? ""} />
          </div>}
	  </div>
	</div>
  );
}
