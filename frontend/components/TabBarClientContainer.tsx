"use client";

import dynamic from "next/dynamic";
import { useState, useEffect } from "react";
import Editor from "@/components/BoardEditor";
import invariant from "tiny-invariant";
import {HistoryContainer} from "@/components/HistoryContainer"
import {ScenesContainer} from "@/components/ScenesContainer"
import { getRuntimeConfig } from "../utils/runtime-config"; // Pfad anpassen

// Dynamisch laden
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
              <Editor backendUrl={apiUrl} />
          </div>}
	  </div>
	</div>
  );
}